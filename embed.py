"""
embed.py — Embedding and vector store pipeline
Loads chunks from chunks.json, embeds them with all-MiniLM-L6-v2,
and stores them in a local ChromaDB collection.

Usage: python embed.py
Requires: chunks.json (run ingest.py first)
Output: ./chroma_db/ directory
"""

import json
import chromadb
from sentence_transformers import SentenceTransformer
from chromadb.config import Settings

CHUNKS_FILE = "chunks.json"
CHROMA_DIR = "./chroma_db"
COLLECTION_NAME = "nyu_professors"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
BATCH_SIZE = 64  # embed in batches to avoid memory issues


def load_chunks(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def embed_and_store(chunks):
    # Load embedding model
    print(f"Loading embedding model: {EMBEDDING_MODEL}...")
    model = SentenceTransformer(EMBEDDING_MODEL)

    # Set up ChromaDB
    print(f"Setting up ChromaDB at '{CHROMA_DIR}'...")
    client = chromadb.PersistentClient(path=CHROMA_DIR)

    # Delete existing collection if re-running
    try:
        client.delete_collection(COLLECTION_NAME)
        print("Deleted existing collection.")
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}  # cosine similarity
    )

    # Embed and store in batches
    print(f"\nEmbedding {len(chunks)} chunks in batches of {BATCH_SIZE}...")
    total = len(chunks)

    for i in range(0, total, BATCH_SIZE):
        batch = chunks[i:i + BATCH_SIZE]
        texts = [c["text"] for c in batch]
        ids = [c["id"] for c in batch]
        metadatas = [
            {
                "source": c["source"],
                "professor": c["professor"],
                "chunk_index": c["chunk_index"]
            }
            for c in batch
        ]

        embeddings = model.encode(texts, show_progress_bar=False).tolist()

        collection.add(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )

        end = min(i + BATCH_SIZE, total)
        print(f"  Embedded chunks {i+1}–{end} / {total}")

    print(f"\nStored {total} chunks in ChromaDB collection '{COLLECTION_NAME}'.")
    return collection


def test_retrieval(collection):
    """Run 3 test queries and print results to verify retrieval works."""
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(EMBEDDING_MODEL)

    test_queries = [
        "Does Professor Bowmaker curve grades generously?",
        "Is Kyle Jung good for beginners with no accounting background?",
        "Does Professor Duan allow cheat sheets on exams?"
    ]

    print(f"\n{'='*60}")
    print("RETRIEVAL TEST — 3 sample queries")
    print(f"{'='*60}")

    for query in test_queries:
        print(f"\nQuery: \"{query}\"")
        print("-" * 50)
        query_embedding = model.encode([query]).tolist()
        results = collection.query(
            query_embeddings=query_embedding,
            n_results=3,
            include=["documents", "metadatas", "distances"]
        )
        for j, (doc, meta, dist) in enumerate(zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        )):
            print(f"  Result {j+1} | Source: {meta['source']} | Distance: {dist:.3f}")
            print(f"  Text: {doc[:150]}...")
            print()


def main():
    print("=== NYU Professor Guide — Embedding Pipeline ===\n")

    # Load chunks
    print(f"Loading chunks from '{CHUNKS_FILE}'...")
    chunks = load_chunks(CHUNKS_FILE)
    print(f"Loaded {len(chunks)} chunks.\n")

    # Embed and store
    collection = embed_and_store(chunks)

    # Test retrieval
    test_retrieval(collection)

    print("\nNext step: run app.py to launch the Gradio interface.")


if __name__ == "__main__":
    main()