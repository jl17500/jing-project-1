"""
ingest.py — Document ingestion and chunking pipeline
Loads all 10 professor review .txt files, splits them into chunks,
and saves the chunks to a JSON file for the embedding step.

Usage: python ingest.py
Output: chunks.json
"""

import os
import json
import random

DATA_DIR = "documents"          # folder containing your prof_*.txt files
OUTPUT_FILE = "chunks.json"
CHUNK_SIZE = 500           # characters
OVERLAP = 100               # characters


def load_documents(data_dir):
    """Load all .txt files from the data directory."""
    documents = []
    for filename in sorted(os.listdir(data_dir)):
        if filename.endswith(".txt"):
            filepath = os.path.join(data_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
            # Extract professor name from the first line
            first_line = text.split("\n")[0]
            prof_name = first_line.replace("Professor:", "").strip()
            documents.append({
                "filename": filename,
                "professor": prof_name,
                "text": text
            })
            print(f"  Loaded: {filename} ({len(text)} chars)")
    return documents


def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=OVERLAP):
    """
    Split text into overlapping chunks of approximately chunk_size characters.
    Uses a simple character-based sliding window.
    """
    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = start + chunk_size

        # If not at the end, try to break at a sentence or word boundary
        if end < text_len:
            # Look for a newline or period near the end of the chunk
            boundary = text.rfind("\n", start, end)
            if boundary == -1 or boundary < start + chunk_size // 2:
                boundary = text.rfind(". ", start, end)
            if boundary == -1 or boundary < start + chunk_size // 2:
                boundary = text.rfind(" ", start, end)
            if boundary != -1 and boundary > start:
                end = boundary + 1

        chunk = text[start:end].strip()
        if len(chunk) > 20:  # skip tiny fragments
            chunks.append(chunk)

        # Move forward by chunk_size minus overlap
        start += max(chunk_size - overlap, 1)

    return chunks


def build_chunks(documents):
    """Chunk all documents and attach metadata."""
    all_chunks = []
    for doc in documents:
        chunks = chunk_text(doc["text"])
        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "id": f"{doc['filename']}_{i}",
                "text": chunk,
                "source": doc["filename"],
                "professor": doc["professor"],
                "chunk_index": i
            })
    return all_chunks


def inspect_chunks(chunks, n=5):
    """Print n random chunks for manual inspection."""
    print(f"\n{'='*60}")
    print(f"SAMPLE CHUNKS (randomly selected)")
    print(f"{'='*60}")
    sample = random.sample(chunks, min(n, len(chunks)))
    for i, chunk in enumerate(sample, 1):
        print(f"\n--- Chunk {i} ---")
        print(f"Source:    {chunk['source']}")
        print(f"Professor: {chunk['professor']}")
        print(f"Length:    {len(chunk['text'])} chars")
        print(f"Text:\n{chunk['text']}")


def main():
    print("=== NYU Professor Guide — Ingestion Pipeline ===\n")

    # 1. Load documents
    print(f"Loading documents from '{DATA_DIR}/'...")
    documents = load_documents(DATA_DIR)
    print(f"\nLoaded {len(documents)} documents.\n")

    # 2. Chunk documents
    print("Chunking documents...")
    chunks = build_chunks(documents)
    print(f"Produced {len(chunks)} chunks total.")

    # 3. Show stats per professor
    print(f"\n{'Professor':<30} {'File':<35} {'Chunks'}")
    print("-" * 75)
    from collections import Counter
    source_counts = Counter(c["source"] for c in chunks)
    for doc in documents:
        count = source_counts.get(doc["filename"], 0)
        print(f"{doc['professor']:<30} {doc['filename']:<35} {count}")

    # 4. Inspect sample chunks
    inspect_chunks(chunks, n=5)

    # 5. Validate: flag any bad chunks
    print(f"\n{'='*60}")
    print("VALIDATION")
    print(f"{'='*60}")
    empty = [c for c in chunks if len(c["text"].strip()) == 0]
    tiny = [c for c in chunks if len(c["text"].strip()) < 30]
    big = [c for c in chunks if len(c["text"]) > CHUNK_SIZE * 2]
    print(f"Empty chunks:   {len(empty)}")
    print(f"Tiny (<30 char): {len(tiny)}")
    print(f"Oversized:       {len(big)}")
    if empty or tiny:
        print("WARNING: You have empty or tiny chunks — check your source files.")
    else:
        print("All chunks look healthy.")

    # 6. Save to JSON
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
    print(f"\nSaved {len(chunks)} chunks to '{OUTPUT_FILE}'.")
    print("\nNext step: run embed.py to embed and store chunks in ChromaDB.")


if __name__ == "__main__":
    main()