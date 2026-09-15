from gemini_models import get_gemini_model_name, list_generate_content_models


def main() -> None:
    models = list_generate_content_models()
    if not models:
        raise RuntimeError("No generateContent-capable models are available for this API key")

    print("Models supporting generateContent:")
    for model in models:
        name = getattr(model, "name", "unknown")
        display_name = getattr(model, "display_name", "")
        print(f"- {name} ({display_name})")
    print(f"Selected first flash model: {get_gemini_model_name()}")


if __name__ == "__main__":
    main()