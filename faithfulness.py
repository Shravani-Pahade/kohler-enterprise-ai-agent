from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any, Callable

from gemini_models import PRIMARY_GEMINI_MODEL, create_gemini_client, generate_with_fallback
from retriever import CHROMA_PATH, RetrievedChunk


DEFAULT_GEMINI_MODEL = PRIMARY_GEMINI_MODEL
FAITHFULNESS_LOG_PATH = Path(__file__).resolve().parent / "faithfulness_log.jsonl"


@dataclass(frozen=True)
class FaithfulnessResult:
    passed: bool
    reason: str


def _create_gemini_model(model_name: str | None = None) -> Any:
    return create_gemini_client()


def _format_context(retrieved_chunks: list[RetrievedChunk]) -> str:
    return "\n\n".join(chunk.text for chunk in retrieved_chunks) or "No context retrieved."


def _parse_check(response_text: str) -> FaithfulnessResult:
    match = re.match(r"^\s*(yes|no)\b\s*[:\-]?\s*(.*)$", response_text, re.IGNORECASE | re.DOTALL)
    if not match:
        raise ValueError("Faithfulness response must start with yes or no")
    return FaithfulnessResult(
        passed=match.group(1).lower() == "yes",
        reason=match.group(2).strip() or "No reason provided.",
    )


def append_faithfulness_log(
    query: str,
    source_domain: str,
    result: FaithfulnessResult,
    log_path: Path = FAITHFULNESS_LOG_PATH,
) -> None:
    """Append one faithfulness result to a local JSONL log."""
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "query": query,
        "source_domain": source_domain,
        "passed": result.passed,
        "reason": result.reason,
    }
    with log_path.open("a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(record) + "\n")


def check_faithfulness(
    query: str,
    answer: str,
    retrieved_chunks: list[RetrievedChunk],
    source_domain: str,
    model_name: str | None = DEFAULT_GEMINI_MODEL,
    model: Any | None = None,
    model_factory: Callable[[str], Any] = _create_gemini_model,
    log_path: Path = FAITHFULNESS_LOG_PATH,
) -> FaithfulnessResult:
    """Check whether an answer is supported by retrieved context and log it."""
    prompt = f"""Determine whether the answer is fully supported by the retrieved context.
Reply with exactly `yes: brief reason` or `no: brief reason`.
Do not repeat or reveal sensitive personal data.

User query:
{query}

Retrieved context:
{_format_context(retrieved_chunks)}

Answer:
{answer}
"""
    evaluator = model or model_factory(model_name)
    if hasattr(evaluator, "interactions"):
        response_text = generate_with_fallback(
            evaluator,
            prompt,
            system_instruction=(
                "You are a strict grounding evaluator. Do not repeat sensitive "
                "personal data from the answer or retrieved context."
            ),
            model_name=model_name or DEFAULT_GEMINI_MODEL,
        )
    else:
        response_text = evaluator.generate_content(prompt).text
    result = _parse_check(response_text)
    append_faithfulness_log(query, source_domain, result, log_path=log_path)
    return result