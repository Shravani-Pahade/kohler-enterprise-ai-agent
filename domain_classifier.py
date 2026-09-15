import json
from typing import Any, Callable

from document_loader import DOMAINS
from gemini_models import PRIMARY_GEMINI_MODEL, create_gemini_client, generate_with_fallback


DEFAULT_GEMINI_MODEL = PRIMARY_GEMINI_MODEL
DEFAULT_HISTORY_LIMIT = 6


def _create_gemini_model(model_name: str | None = None) -> Any:
    return create_gemini_client()


def _history_text(conversation_history: list[dict[str, str]]) -> str:
    recent_history = conversation_history[-DEFAULT_HISTORY_LIMIT:]
    if not recent_history:
        return "No prior conversation."

    return "\n".join(
        f"{turn.get('role', 'user')}: {turn.get('content', '')}"
        for turn in recent_history
    )


def _parse_domain(response_text: str) -> str:
    cleaned = response_text.strip()
    if cleaned.startswith("```") and cleaned.endswith("```"):
        cleaned = cleaned.split("\n", 1)[-1].removesuffix("```").strip()
    try:
        domain = json.loads(cleaned)["domain"]
    except (KeyError, json.JSONDecodeError, TypeError):
        domain = cleaned

    if domain not in DOMAINS:
        raise ValueError(f"Gemini returned an invalid domain: {domain!r}")
    return domain


def classify_domain(
    current_message: str,
    conversation_history: list[dict[str, str]],
    model_name: str | None = DEFAULT_GEMINI_MODEL,
    model: Any | None = None,
    model_factory: Callable[[str], Any] = _create_gemini_model,
) -> str:
    """Classify the current message using recent conversation context."""
    if not current_message.strip():
        raise ValueError("current_message must not be empty")

    prompt = f"""You classify the user's CURRENT message into exactly one domain.

Allowed domains:
- hr_policy: employee leave, benefits, workplace rules, or HR matters
- customer_support: products, orders, returns, refunds, replacements, or support
- privacy_policy: personal data, privacy rights, retention, deletion, or data handling

Use the conversation history only as context. The CURRENT message has priority:
if it switches topics, return the new domain rather than following the previous one.
Do not answer the user and do not repeat sensitive personal data.
Return only valid JSON in this exact shape: {{"domain": "one_allowed_domain"}}

Recent conversation:
{_history_text(conversation_history)}

CURRENT message:
{current_message}
"""

    classifier = model or model_factory(model_name)
    if hasattr(classifier, "interactions"):
        response_text = generate_with_fallback(
            classifier,
            prompt,
            model_name=model_name or DEFAULT_GEMINI_MODEL,
        )
    else:
        response_text = classifier.generate_content(prompt).text
    return _parse_domain(response_text)