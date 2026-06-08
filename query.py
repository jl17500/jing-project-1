"""
query.py — Retrieval and grounded generation
Retrieves relevant chunks from ChromaDB and generates a grounded
answer using Groq's llama-3.3-70b-versatile model.

Usage: import and call ask(question), or run directly for CLI mode.
Requires: chroma_db/ directory (run embed.py first), GROQ_API_KEY in .env
"""

import os
import chromadb
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

CHROMA_DIR = "./chroma_db"
COLLECTION_NAME = "nyu_professors"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
GROQ_MODEL = "llama-3.3-70b-versatile"
TOP_K = 8

# Load model and DB once at module level (not on every call)
print("Loading embedding model...")
_model = SentenceTransformer(EMBEDDING_MODEL)

print("Connecting to ChromaDB...")
_client = chromadb.PersistentClient(path=CHROMA_DIR)
_collection = _client.get_collection(COLLECTION_NAME)

print("Connecting to Groq...")
_groq = Groq(api_key=os.environ.get("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are a helpful assistant for NYU students looking for honest, 
student-sourced information about professors and courses.

You will be given a question and a set of retrieved student reviews as context.

RULES:
1. Answer ONLY using the information in the provided context. Do not use any outside knowledge.
2. If the context does not contain enough information to answer the question, say exactly: 
   "I don't have enough information in my sources to answer that."
3. Do not make up facts, statistics, or student opinions that are not in the context.
4. Be direct and specific — students want actionable answers.
5. Always end your response with a "Sources:" line listing the filenames the answer draws from.

Format your response as:
[Your answer here]

Sources: [comma-separated list of source filenames]"""


def retrieve(query, k=TOP_K):
    """Retrieve the top-k most relevant chunks for a query."""
    query_embedding = _model.encode([query]).tolist()
    results = _collection.query(
        query_embeddings=query_embedding,
        n_results=k,
        include=["documents", "metadatas", "distances"]
    )
    chunks = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        chunks.append({
            "text": doc,
            "source": meta["source"],
            "professor": meta["professor"],
            "distance": dist
        })
    return chunks


def build_context(chunks):
    """Format retrieved chunks into a context string for the LLM."""
    lines = []
    for i, chunk in enumerate(chunks, 1):
        lines.append(f"[{i}] Source: {chunk['source']}\n{chunk['text']}")
    return "\n\n".join(lines)


def ask(question):
    """
    Full RAG pipeline: retrieve relevant chunks, generate grounded answer.
    Returns a dict with 'answer' and 'sources' keys.
    """
    # Retrieve
    chunks = retrieve(question, k=TOP_K)

    # Build context
    context = build_context(chunks)

    # Generate
    user_message = f"""Context (student reviews):
{context}

Question: {question}

Remember: answer only from the context above. End with a Sources: line."""

    response = _groq.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        temperature=0.2,  # low temp for factual, grounded responses
        max_tokens=600
    )

    full_response = response.choices[0].message.content.strip()

    # Extract sources list from response
    sources = []
    if "Sources:" in full_response:
        sources_line = full_response.split("Sources:")[-1].strip()
        sources = [s.strip() for s in sources_line.split(",") if s.strip()]
        answer = full_response.split("Sources:")[0].strip()
    else:
        answer = full_response
        # Fall back to listing unique sources from retrieved chunks
        sources = list(dict.fromkeys(c["source"] for c in chunks))

    return {
        "answer": answer,
        "sources": sources,
        "chunks": chunks  # included for debugging/evaluation
    }


if __name__ == "__main__":
    # Simple CLI mode for testing
    print("\n=== NYU Professor Guide — Query Interface (CLI) ===")
    print("Type your question and press Enter. Type 'quit' to exit.\n")
    while True:
        question = input("Your question: ").strip()
        if question.lower() in ("quit", "exit", "q"):
            break
        if not question:
            continue
        print("\nSearching...\n")
        result = ask(question)
        print(f"Answer:\n{result['answer']}")
        print(f"\nSources: {', '.join(result['sources'])}")
        print("\n" + "="*60 + "\n")