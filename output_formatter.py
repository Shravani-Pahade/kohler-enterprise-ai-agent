import csv
from io import StringIO
import json
import re
from typing import Any, Literal
from xml.etree.ElementTree import Element, SubElement, tostring


OutputFormat = Literal["json", "email", "markdown", "excel", "xml"]


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
    if re.search(r"\b(excel|csv|download)\b", normalized):
        return "excel"
    if re.search(r"\bxml\b", normalized):
        return "xml"
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


def format_excel(answer: str, source_domain: str, confidence: float) -> str:
    """Return CSV text suitable for a download button."""
    if not 0 <= confidence <= 1:
        raise ValueError("confidence must be between 0 and 1")

    output = StringIO(newline="")
    writer = csv.DictWriter(
        output,
        fieldnames=["answer", "source_domain", "confidence"],
    )
    writer.writeheader()
    writer.writerow(
        {
            "answer": answer,
            "source_domain": source_domain,
            "confidence": confidence,
        }
    )
    return output.getvalue()


def format_xml(answer: str, source_domain: str, confidence: float) -> str:
    """Return a simple XML response with escaped content."""
    if not 0 <= confidence <= 1:
        raise ValueError("confidence must be between 0 and 1")

    response = Element("response")
    SubElement(response, "answer").text = answer
    SubElement(response, "domain").text = source_domain
    SubElement(response, "confidence").text = str(confidence)
    return tostring(response, encoding="unicode")


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
    if output_format == "excel":
        return format_excel(answer, source_domain, confidence)
    if output_format == "xml":
        return format_xml(answer, source_domain, confidence)
    return format_markdown(answer)