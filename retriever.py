from dataclasses import dataclass
from pathlib import Path
from typing import Any

from document_loader import DOMAINS
from vector_store import CHROMA_PATH, DEFAULT_EMBEDDING_MODEL, create_embeddings, get_chroma_client


@dataclass(frozen=True)
class RetrievedChunk:
    text: str
    metadata: dict[str, Any]
    similarity_score: float
    distance: float


def retrieve_chunks(
    domain: str,
    query: str,
    top_k: int = 4,
    persist_path: Path = CHROMA_PATH,
    model_name: str = DEFAULT_EMBEDDING_MODEL,
) -> list[RetrievedChunk]:
    """Return up to four ranked chunks for a query in one domain.

    Chroma returns distances, so the score is converted to a bounded relevance
    score with ``1 / (1 + distance)``. Higher scores are more relevant.
    """
    if domain not in DOMAINS:
        raise ValueError(f"Unknown domain: {domain}")
    if not query.strip():
        raise ValueError("query must not be empty")
    if top_k < 1 or top_k > 4:
        raise ValueError("top_k must be between 1 and 4")

    client = get_chroma_client(persist_path=persist_path)
    collection = client.get_collection(name=domain)
    query_embedding = create_embeddings([query], model_name=model_name)[0]
    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    documents = result["documents"][0]
    metadatas = result["metadatas"][0]
    distances = result["distances"][0]
    return [
        RetrievedChunk(
            text=document,
            metadata=metadata,
            similarity_score=1 / (1 + distance),
            distance=distance,
        )
        for document, metadata, distance in zip(documents, metadatas, distances)
    ]