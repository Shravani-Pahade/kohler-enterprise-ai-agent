from pathlib import Path
from typing import Any

from document_loader import DATA_ROOT, DOMAINS, DocumentChunk, load_all_documents


PROJECT_ROOT = Path(__file__).resolve().parent
CHROMA_PATH = PROJECT_ROOT / "chroma_db"
DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def _chunk_id(chunk: DocumentChunk) -> str:
    return f"{chunk.domain}:{chunk.source}:{chunk.chunk_index}"


def create_embeddings(
    texts: list[str],
    model_name: str = DEFAULT_EMBEDDING_MODEL,
) -> list[list[float]]:
    """Create sentence-transformer embeddings for document texts."""
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(model_name)
    embeddings = model.encode(texts, convert_to_numpy=True)
    return embeddings.tolist()


def get_chroma_client(persist_path: Path = CHROMA_PATH) -> Any:
    """Create a persistent local ChromaDB client."""
    import chromadb

    persist_path.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(persist_path))


def store_domain_chunks(
    client: Any,
    domain: str,
    chunks: list[DocumentChunk],
    embeddings: list[list[float]],
) -> Any:
    """Store one domain's chunks and embeddings in its own collection."""
    if domain not in DOMAINS:
        raise ValueError(f"Unknown domain: {domain}")
    if len(chunks) != len(embeddings):
        raise ValueError("Each chunk must have exactly one embedding")

    collection = client.get_or_create_collection(name=domain)
    if not chunks:
        return collection

    collection.upsert(
        ids=[_chunk_id(chunk) for chunk in chunks],
        documents=[chunk.text for chunk in chunks],
        embeddings=embeddings,
        metadatas=[
            {
                "domain": chunk.domain,
                "source": chunk.source,
                "chunk_index": chunk.chunk_index,
            }
            for chunk in chunks
        ],
    )
    return collection


def build_vector_store(
    data_root: Path = DATA_ROOT,
    persist_path: Path = CHROMA_PATH,
    model_name: str = DEFAULT_EMBEDDING_MODEL,
    chunk_size: int = 250,
    overlap: int = 50,
) -> dict[str, Any]:
    """Embed all domain chunks and persist them in separate collections."""
    documents_by_domain = load_all_documents(
        data_root=data_root,
        chunk_size=chunk_size,
        overlap=overlap,
    )
    client = get_chroma_client(persist_path=persist_path)
    collections: dict[str, Any] = {}

    for domain in DOMAINS:
        chunks = documents_by_domain[domain]
        embeddings = create_embeddings(
            [chunk.text for chunk in chunks],
            model_name=model_name,
        )
        collections[domain] = store_domain_chunks(
            client=client,
            domain=domain,
            chunks=chunks,
            embeddings=embeddings,
        )
    return collections