from vector_store import build_vector_store


if __name__ == "__main__":
    collections = build_vector_store()
    print("Built local ChromaDB collections:")
    for domain, collection in collections.items():
        print(f"- {domain}: {collection.count()} chunks")