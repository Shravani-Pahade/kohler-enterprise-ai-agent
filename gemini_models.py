from typing import Any

from config import get_gemini_api_key

PRIMARY_GEMINI_MODEL = "gemini-3.6-flash"
FALLBACK_GEMINI_MODELS = ("gemini-3.5-flash", "gemini-2.5-flash-lite")


def create_gemini_client() -> Any:
    """Create the current Google GenAI client from the environment key."""
    from google import genai

    return genai.Client(api_key=get_gemini_api_key())


def _is_not_found(error: Exception) -> bool:
    return getattr(error, "code", None) == 404 or getattr(error, "status_code", None) == 404


def generate_with_fallback(
    client: Any,
    prompt: str,
    system_instruction: str | None = None,
    model_name: str = PRIMARY_GEMINI_MODEL,
) -> str:
    """Generate text, retrying known fallback models after a model 404."""
    models = (model_name,) + tuple(
        model for model in FALLBACK_GEMINI_MODELS if model != model_name
    )
    last_error: Exception | None = None
    for model in models:
        try:
            interaction = client.interactions.create(
                model=model,
                input=prompt,
                system_instruction=system_instruction,
            )
            return interaction.output_text
        except Exception as error:
            if not _is_not_found(error):
                raise
            last_error = error
    raise RuntimeError(
        f"No configured Gemini model was available: {', '.join(models)}"
    ) from last_error


def list_generate_content_models(client: Any | None = None) -> list[Any]:
    """Return models from the API that support generateContent."""
    client = client or create_gemini_client()
    return [
        model
        for model in client.models.list()
        if "generateContent" in (getattr(model, "supported_actions", None) or [])
    ]


def _model_name(model: Any) -> str:
    return str(getattr(model, "name", "")).removeprefix("models/")


def select_flash_model(models: list[Any]) -> str:
    """Select the first generate-capable flash model from live model metadata."""
    for model in models:
        name = _model_name(model)
        display_name = str(getattr(model, "display_name", ""))
        if "flash" in f"{name} {display_name}".lower():
            return name
    raise RuntimeError("No generateContent-capable flash model is available for this API key")


def get_gemini_model_name() -> str:
    """Return the confirmed primary model used by the application."""
    return PRIMARY_GEMINI_MODEL