from dataclasses import dataclass
from pathlib import Path
import re


PROJECT_ROOT = Path(__file__).resolve().parent
DATA_ROOT = PROJECT_ROOT / "data"
DOMAINS = ("hr_policy", "customer_support", "privacy_policy")


@dataclass(frozen=True)
class DocumentChunk:
    text: str
    domain: str
    source: str
    chunk_index: int


def _split_words(text: str) -> list[str]:
    return re.findall(r"\S+", text)


def chunk_text(text: str, chunk_size: int = 250, overlap: int = 50) -> list[str]:
    """Split text into overlapping word-based chunks."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be non-negative and smaller than chunk_size")

    words = _split_words(text)
    if not words:
        return []

    step = chunk_size - overlap
    chunks: list[str] = []
    covered_until = 0
    for start in range(0, len(words), step):
        end = min(start + chunk_size, len(words))
        if end <= covered_until:
            continue
        chunks.append(" ".join(words[start:end]))
        covered_until = end
    return chunks


def load_domain_documents(
    domain: str,
    data_root: Path = DATA_ROOT,
    chunk_size: int = 250,
    overlap: int = 50,
) -> list[DocumentChunk]:
    """Load and chunk all text files for one domain."""
    domain_path = data_root / domain
    if not domain_path.is_dir():
        raise FileNotFoundError(f"Domain directory not found: {domain_path}")

    chunks: list[DocumentChunk] = []
    for source_path in sorted(domain_path.glob("*.txt")):
        text = source_path.read_text(encoding="utf-8")
        for chunk_index, chunk in enumerate(
            chunk_text(text, chunk_size=chunk_size, overlap=overlap)
        ):
            chunks.append(
                DocumentChunk(
                    text=chunk,
                    domain=domain,
                    source=str(source_path.relative_to(data_root)),
                    chunk_index=chunk_index,
                )
            )
    return chunks


def load_all_documents(
    data_root: Path = DATA_ROOT,
    chunk_size: int = 250,
    overlap: int = 50,
) -> dict[str, list[DocumentChunk]]:
    """Load and chunk documents for all configured domains."""
    return {
        domain: load_domain_documents(
            domain,
            data_root=data_root,
            chunk_size=chunk_size,
            overlap=overlap,
        )
        for domain in DOMAINS
    }