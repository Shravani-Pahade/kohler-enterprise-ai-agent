import json
import re
from typing import Any, Literal


OutputFormat = Literal["json", "email", "markdown"]


def detect_output_format(user_message: str) -> OutputFormat:
    """Detect the requested response format from the user's message."""
    if not user_message.strip():
        raise ValueError("user_message must not be empty")

    normalized = user_message.lower()
    if re.search(r"\bjson\b", normalized):
        return "json"
    if re.search(r"\bemail\b", normalized) or re.search(
        r"\be-mail\b", normalized
    ):
        return "email"
    return "markdown"


def format_markdown(answer: str) -> str:
    """Return the answer unchanged for the default format."""
    return answer


def format_email(answer: str, subject: str = "Kohler Support Response") -> str:
    """Wrap an answer as a short professional email."""
    return f"Subject: {subject}\n\nHello,\n\n{answer}\n\nBest regards,\nKohler Support"


def format_json(answer: str, source_domain: str, confidence: float) -> str:
    """Return a validated JSON response containing the answer and metadata."""
    if not 0 <= confidence <= 1:
        raise ValueError("confidence must be between 0 and 1")

    payload = {
        "answer": answer,
        "source_domain": source_domain,
        "confidence": confidence,
    }
    serialized = json.dumps(payload)
    parsed: dict[str, Any] = json.loads(serialized)
    if parsed != payload:
        raise ValueError("Formatted response failed JSON round-trip validation")
    return serialized


def format_response(
    user_message: str,
    answer: str,
    source_domain: str,
    confidence: float,
) -> str:
    """Detect the requested format and format the generated answer."""
    output_format = detect_output_format(user_message)
    if output_format == "json":
        return format_json(answer, source_domain, confidence)
    if output_format == "email":
        return format_email(answer)
    return format_markdown(answer)