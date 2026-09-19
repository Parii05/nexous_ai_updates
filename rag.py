import os
import json
import re
import uuid
from collections import Counter
from datetime import datetime
from typing import TypedDict
from pathlib import Path

from dotenv import dotenv_values
import fitz
from groq import Groq
from langgraph.graph import StateGraph, END
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer

# ---------------------------------------------------------------------
# 1. CONFIG
# ---------------------------------------------------------------------
_env_values = dotenv_values(Path(__file__).resolve().parent / ".env")
for key, value in (_env_values or {}).items():
    if value is not None and key not in os.environ:
        os.environ[key] = value

GROQ_API_KEY = os.getenv("GROQ_API_KEY") or ""
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY") or ""

INDEX_NAME = "rag-index-euclidean"

EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBED_DIM = 384

GROQ_MODEL = "qwen/qwen3.8-27b"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
MIN_PARAGRAPH_CHARS = 120

TOP_K = 3
RERANK_TOP_K = 5
RERANK_CANDIDATE_K = 10

DOC_NAMESPACE = "documents"
MEMORY_NAMESPACE = "memory"

MEMORY_TOP_K = 5
MEMORY_IMPORTANCE_THRESHOLD = 0.65


class RAGState(TypedDict, total=False):
    """Shared state for the RAG pipeline."""

    question: str
    domain: str | None
    sub_queries: list[str]
    retrieved_chunks: list[dict]
    memories: list[dict]
    final_answer: str
    citations: list[dict]
    last_agent: str
    error: str
    needs_retrieval: bool
    metadata: dict


# ---------------------------------------------------------------------
# 2. INIT CLIENTS
# ---------------------------------------------------------------------

embedder = None
groq_client = None
pc = None
index = None


def _as_vector_list(vector):
    """Normalize embedding vectors from NumPy arrays or plain Python sequences."""
    if hasattr(vector, "tolist"):
        return vector.tolist()
    return list(vector)


def get_embedder():
    """Lazily initialize the sentence embedding model when it is actually needed."""
    global embedder
    if embedder is None:
        embedder = SentenceTransformer(EMBED_MODEL)
    return embedder


def get_groq_client():
    """Return the Groq client, raising only when an actual API call requires it."""
    global groq_client
    if groq_client is None:
        if not GROQ_API_KEY:
            raise ValueError("Missing GROQ_API_KEY environment variable")
        groq_client = Groq(api_key=GROQ_API_KEY)
    return groq_client


def get_pinecone_index():
    """Create or fetch the configured Pinecone index on demand."""
    global pc, index
    if index is not None:
        return index

    if not PINECONE_API_KEY:
        raise ValueError("Missing PINECONE_API_KEY environment variable")

    pc = Pinecone(api_key=PINECONE_API_KEY)
    existing = [i.name for i in pc.list_indexes()]

    if INDEX_NAME not in existing:
        pc.create_index(
            name=INDEX_NAME,
            dimension=EMBED_DIM,
            metric="euclidean",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        print(f"[+] Created Pinecone index: {INDEX_NAME}")

    index = pc.Index(INDEX_NAME)
    return index

# ---------------------------------------------------------------------
# 3. PDF TO TEXT CHUNKS
# ---------------------------------------------------------------------

def extract_text_from_pdf(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    text = "\n".join(page.get_text() for page in doc)
    doc.close()
    return text


def chunk_text(
    text: str,
    size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[str]:
    """Chunk text using a structural strategy: preserve paragraph boundaries first."""

    cleaned = re.sub(r"\n{3,}", "\n\n", text).strip()
    if not cleaned:
        return []

    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", cleaned) if p.strip()]
    if not paragraphs:
        return []

    chunks = []

    for paragraph in paragraphs:
        if len(paragraph) <= size:
            chunks.append(paragraph)
            continue

        start = 0
        while start < len(paragraph):
            end = start + size
            chunk = paragraph[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start += size - overlap

    return chunks

# ---------------------------------------------------------------------
# 4. UPLOAD PDF TO PINECONE
# ---------------------------------------------------------------------

def _index_text(
    raw_text: str,
    source_name: str,
    domain: str | None = None,
    ocr: bool = False,
    document_id: str | None = None,
):
    """Chunk, embed and index extracted text with source/domain metadata."""
    chunks = chunk_text(raw_text)

    if not chunks:
        raise ValueError("No readable text could be extracted from the document.")

    embeddings = get_embedder().encode(chunks, show_progress_bar=True)
    normalized_domain = domain or "General"
    now = datetime.utcnow().isoformat()

    vectors = [
        (
            f"chunk-{uuid.uuid4()}",
            emb.tolist(),
            {
                "text": chunk,
                "source": source_name,
                "domain": normalized_domain,
                "type": "document_chunk",
                "ocr": ocr,
                "document_id": document_id,
                "created_at": now,
            },
        )
        for emb, chunk in zip(embeddings, chunks)
    ]

    for i in range(0, len(vectors), 100):
        get_pinecone_index().upsert(vectors=vectors[i:i + 100], namespace=DOC_NAMESPACE)

    # One registry record per uploaded document. It lives in the same
    # Pinecone namespace, but retrieval explicitly filters to document_chunk.
    registry_id = f"document-{document_id or uuid.uuid4()}"
    registry_vector = embeddings.mean(axis=0).tolist()
    get_pinecone_index().upsert(
        vectors=[(
            registry_id,
            registry_vector,
            {
                "filename": source_name,
                "source": source_name,
                "domain": normalized_domain,
                "file_type": Path(source_name).suffix.lower().lstrip(".") or "unknown",
                "status": "indexed",
                "ocr": ocr,
                "indexed": True,
                "chunk_count": len(vectors),
                "document_id": document_id,
                "created_at": now,
            },
        )],
        namespace=DOC_NAMESPACE,
    )

    print(f"[+] Uploaded {len(vectors)} chunks to Pinecone namespace '{DOC_NAMESPACE}'")
    return len(vectors)


def upload_pdf(pdf_path: str, source_name: str | None = None, domain: str | None = None):
    """Index a PDF document."""
    print(f"[+] Extracting text from: {pdf_path}")
    raw_text = extract_text_from_pdf(pdf_path)
    return _index_text(
        raw_text,
        source_name or Path(pdf_path).name,
        domain=domain,
    )


def upload_document(
    file_path: str,
    source_name: str | None = None,
    domain: str | None = None,
    document_id: str | None = None,
):
    """Extract and index supported documents and record lifecycle metadata.

    Legacy .doc files remain unsupported because the current environment has
    no guaranteed Word/LibreOffice conversion dependency.
    """
    path = Path(file_path)
    extension = path.suffix.lower()
    source = source_name or path.name
    normalized_domain = domain or "General"
    ocr = extension in {".png", ".jpg", ".jpeg", ".webp"}

    if extension == ".doc":
        raise ValueError(
            "Legacy .doc files are not supported by the current ingestion environment. "
            "Convert the file to .docx before uploading."
        )

    if extension not in {".pdf", ".txt", ".docx", ".png", ".jpg", ".jpeg", ".webp"}:
        raise ValueError(
            f"Unsupported document type: {extension or 'unknown'}. "
            "Supported types: PDF, TXT, DOCX, PNG, JPG, JPEG, WEBP."
        )

    document_id = document_id or str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    # Create a processing record before extraction so the library can expose
    # failures as well as successful documents.
    registry_id = f"document-{document_id}"
    registry_embedding = get_embedder().encode([source])[0].tolist()
    base_metadata = {
        "filename": source,
        "source": source,
        "domain": normalized_domain,
        "file_type": extension.lstrip(".") or "unknown",
        "status": "processing",
        "ocr": ocr,
        "indexed": False,
        "chunk_count": 0,
        "document_id": document_id,
        "created_at": now,
    }
    get_pinecone_index().upsert(
        vectors=[(registry_id, registry_embedding, base_metadata)],
        namespace=DOC_NAMESPACE,
    )

    try:
        if extension == ".pdf":
            raw_text = extract_text_from_pdf(file_path)
        elif extension == ".txt":
            raw_text = path.read_text(encoding="utf-8", errors="ignore")
        elif extension == ".docx":
            from docx import Document
            document = Document(file_path)
            raw_text = "\n\n".join(
                paragraph.text.strip()
                for paragraph in document.paragraphs
                if paragraph.text.strip()
            )
        else:
            try:
                import pytesseract
                from PIL import Image
            except ImportError as exc:
                raise RuntimeError(
                    "OCR dependencies are missing. Install pytesseract and Pillow, "
                    "and make sure the Tesseract OCR engine is installed."
                ) from exc
            raw_text = pytesseract.image_to_string(Image.open(file_path))

        chunk_count = _index_text(
            raw_text,
            source,
            domain=normalized_domain,
            ocr=ocr,
            document_id=document_id,
        )

        indexed_metadata = dict(base_metadata)
        indexed_metadata.update({
            "status": "indexed",
            "indexed": True,
            "chunk_count": chunk_count,
            "updated_at": datetime.utcnow().isoformat(),
        })
        get_pinecone_index().upsert(
            vectors=[(registry_id, registry_embedding, indexed_metadata)],
            namespace=DOC_NAMESPACE,
        )
        return {
            "success": True,
            "status": "indexed",
            "document_id": document_id,
            "chunk_count": chunk_count,
            "ocr": ocr,
            "domain": normalized_domain,
        }

    except Exception as exc:
        failed_metadata = dict(base_metadata)
        failed_metadata.update({
            "status": "failed",
            "indexed": False,
            "error": str(exc),
            "updated_at": datetime.utcnow().isoformat(),
        })
        get_pinecone_index().upsert(
            vectors=[(registry_id, registry_embedding, failed_metadata)],
            namespace=DOC_NAMESPACE,
        )
        raise

def list_document_records(domain: str | None = None) -> list[dict]:
    """Return persisted document registry records from the existing Pinecone index."""
    ids = []

    pinecone_index = get_pinecone_index()

    try:
        listed = pinecone_index.list(namespace=DOC_NAMESPACE, prefix="document-")
        for batch in listed:
            if isinstance(batch, dict):
                batch_ids = batch.get("ids", [])
            else:
                batch_ids = getattr(batch, "ids", None) or []
            ids.extend(batch_ids)
    except TypeError:
        listed = pinecone_index.list(namespace=DOC_NAMESPACE)
        for batch in listed:
            batch_ids = batch.get("ids", []) if isinstance(batch, dict) else (getattr(batch, "ids", None) or [])
            ids.extend([item for item in batch_ids if str(item).startswith("document-")])

    if not ids:
        return []

    records = []
    for start in range(0, len(ids), 100):
        fetched = pinecone_index.fetch(ids=ids[start:start + 100], namespace=DOC_NAMESPACE)
        vectors = fetched.get("vectors", {}) if isinstance(fetched, dict) else getattr(fetched, "vectors", {}) or {}

        iterable = vectors.items() if hasattr(vectors, "items") else []
        for vector_id, vector in iterable:
            metadata = vector.get("metadata", {}) if isinstance(vector, dict) else (getattr(vector, "metadata", {}) or {})
            if not metadata:
                continue
            if domain and metadata.get("domain") != domain:
                continue
            records.append({
                "document_id": metadata.get("document_id") or vector_id.replace("document-", "", 1),
                "filename": metadata.get("filename") or metadata.get("source") or "Unknown",
                "source": metadata.get("source") or metadata.get("filename"),
                "domain": metadata.get("domain", "General"),
                "file_type": metadata.get("file_type", "unknown"),
                "status": metadata.get("status", "unknown"),
                "ocr": bool(metadata.get("ocr", False)),
                "indexed": bool(metadata.get("indexed", False)),
                "chunk_count": int(metadata.get("chunk_count", 0) or 0),
                "created_at": metadata.get("created_at"),
                "updated_at": metadata.get("updated_at"),
                "error": metadata.get("error"),
            })

    records.sort(key=lambda item: item.get("created_at") or "", reverse=True)
    return records


# ---------------------------------------------------------------------
# 5. QUERY DECOMPOSITION
# ---------------------------------------------------------------------

def decompose_query(question: str) -> list[str]:
    """
    Breaks a complex question into focused sub-queries.
    Always returns at least one query.
    """

    system_prompt = (
        "You are a query decomposition assistant. "
        "Break the user's question into 2-4 simpler, focused sub-questions "
        "that together cover the full question. "
        "Return ONLY a numbered list like:\n"
        "1. sub-question one\n"
        "2. sub-question two\n\n"
        "If the question is already simple, return just:\n"
        "1. <the original question>"
    )

    response = get_groq_client().chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
        temperature=0.0,
        max_tokens=200,
    )

    raw = response.choices[0].message.content.strip()

    sub_queries = []

    for line in raw.splitlines():
        line = line.strip()

        if line and line[0].isdigit():
            parts = line.split(".", 1)

            if len(parts) == 2:
                sub_query = parts[1].strip()

                if sub_query:
                    sub_queries.append(sub_query)

    return sub_queries if sub_queries else [question]

# ---------------------------------------------------------------------
# 6. DOCUMENT RETRIEVAL
# ---------------------------------------------------------------------

def tokenize_text(text: str) -> list[str]:
    """Simple tokenizer for sparse keyword scoring."""

    return re.findall(r"\b\w+\b", text.lower())


def sparse_keyword_score(query: str, text: str) -> float:
    """Compute a simple BM25-like keyword overlap score."""

    query_terms = tokenize_text(query)
    doc_terms = tokenize_text(text)

    if not query_terms or not doc_terms:
        return 0.0

    query_counter = Counter(query_terms)
    doc_counter = Counter(doc_terms)
    overlap = sum(min(query_counter[term], doc_counter[term]) for term in query_counter)

    return round(overlap / len(query_terms), 4)


def rank_hybrid_results(query: str, candidates: list[dict]) -> list[dict]:
    """Combine dense similarity and sparse keyword overlap into a hybrid score."""

    ranked = []

    for item in candidates:
        dense_score = float(item.get("score", 0) or 0)
        sparse_score = sparse_keyword_score(query, item.get("text", ""))
        hybrid_score = round((dense_score * 0.6) + (sparse_score * 0.4), 4)

        ranked_item = dict(item)
        ranked_item["sparse_score"] = sparse_score
        ranked_item["hybrid_score"] = hybrid_score
        ranked.append(ranked_item)

    ranked.sort(key=lambda item: item["hybrid_score"], reverse=True)
    return ranked


def rerank_candidates(query: str, candidates: list[dict]) -> list[dict]:
    """Second-pass reranking stage over a broader candidate pool."""

    if not candidates:
        return []

    ranked = rank_hybrid_results(query, candidates)
    return ranked[:RERANK_TOP_K]


def retrieve_chunks(
    query: str,
    top_k: int = TOP_K,
    domain: str | None = None,
) -> list[dict]:
    """
    Retrieves document chunks from the document namespace.
    """

    q_vec = _as_vector_list(get_embedder().encode([query])[0])

    query_kwargs = {
        "vector": q_vec,
        "top_k": RERANK_CANDIDATE_K,
        "include_metadata": True,
        "namespace": DOC_NAMESPACE,
        "filter": {"type": {"$eq": "document_chunk"}},
    }

    if domain:
        query_kwargs["filter"] = {
            "$and": [
                {"type": {"$eq": "document_chunk"}},
                {"domain": {"$eq": domain}},
            ]
        }

    results = get_pinecone_index().query(**query_kwargs)

    chunks = []

    for match in results.get("matches", []):
        metadata = match.get("metadata", {})
        text = metadata.get("text")

        if text:
            # Defense in depth: Pinecone performs the primary metadata filter,
            # but the application also verifies the returned domain.
            if domain and metadata.get("domain") != domain:
                continue
            chunks.append({
                "text": text,
                "score": round(match.get("score", 0), 4),
                "source": metadata.get("source"),
                "domain": metadata.get("domain"),
                "ocr": metadata.get("ocr", False),
                "document_id": metadata.get("document_id"),
            })

    ranked_chunks = rerank_candidates(query, chunks)
    return ranked_chunks[:top_k]


def retrieve_with_decomposition(
    question: str,
    domain: str | None = None,
) -> tuple[list[str], list[dict]]:
    """
    Decomposes the question, retrieves chunks for each sub-query,
    and deduplicates repeated chunks.
    """

    sub_queries = decompose_query(question)

    print(f"\n--- Decomposed into {len(sub_queries)} sub-query/query(s) ---")

    for i, q in enumerate(sub_queries, 1):
        print(f"[{i}] {q}")

    seen_texts = set()
    all_chunks = []

    for sub_q in sub_queries:
        chunks = retrieve_chunks(sub_q, domain=domain)

        for chunk in chunks:
            if chunk["text"] not in seen_texts:
                seen_texts.add(chunk["text"])
                all_chunks.append(chunk)

    return sub_queries, all_chunks

# ---------------------------------------------------------------------
# 7. IMPORTANT CONTEXT MEMORY
# ---------------------------------------------------------------------

def retrieve_memories(question: str, top_k: int = MEMORY_TOP_K) -> list[dict]:
    """
    Retrieves previously stored important context relevant to the question.
    """

    q_vec = _as_vector_list(get_embedder().encode([question])[0])

    results = get_pinecone_index().query(
        vector=q_vec,
        top_k=RERANK_CANDIDATE_K,
        include_metadata=True,
        namespace=MEMORY_NAMESPACE,
    )

    memories = []

    for match in results.get("matches", []):
        metadata = match.get("metadata", {})
        text = metadata.get("text")

        if text:
            memories.append({
                "text": text,
                "score": round(match.get("score", 0), 4),
                "importance": metadata.get("importance"),
                "reason": metadata.get("reason"),
                "created_at": metadata.get("created_at"),
            })

    ranked_memories = rerank_candidates(question, memories)
    return ranked_memories[:top_k]

def extract_important_context(question: str, answer: str) -> list[dict]:
    """
    Uses the LLM to decide what should be stored as long-term context.
    """

    system_prompt = """
You extract only important long-term context worth remembering for future answers.

Return valid JSON only, in this exact format:
{
  "memories": [
    {
      "text": "short standalone memory",
      "importance": 0.0,
      "reason": "why this is worth remembering"
    }
  ]
}

Importance scale:
0.0 = not worth storing
0.5 = maybe useful
0.7 = useful long-term memory
1.0 = critical long-term memory

Store only durable context such as:
- user preferences
- project architecture decisions
- constraints
- important goals
- corrections from the user
- facts needed for future continuity

Do not store:
- API keys, passwords, tokens, or secrets
- private sensitive data
- temporary retrieved document snippets
- facts that are already in the uploaded documents
- generic information
"""
    user_prompt = f"""
User question:
{question}

Assistant answer:
{answer}
Extract only important context worth storing.
"""
    response = get_groq_client().chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.0,
        max_tokens=400,
    )

    raw = response.choices[0].message.content.strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []

    memories = data.get("memories", [])
    filtered = []

    for memory in memories:
        text = str(memory.get("text", "")).strip()

        try:
            importance = float(memory.get("importance", 0))
        except ValueError:
            importance = 0

        if not text:
            continue

        if importance < MEMORY_IMPORTANCE_THRESHOLD:
            continue

        filtered.append({
            "text": text,
            "importance": importance,
            "reason": memory.get("reason", ""),
        })

    return filtered

def memory_already_exists(memory_text: str) -> bool:
    """
    Prevents storing near-duplicate memories.
    """

    q_vec = _as_vector_list(get_embedder().encode([memory_text])[0])

    results = get_pinecone_index().query(
        vector=q_vec,
        top_k=1,
        include_metadata=True,
        namespace=MEMORY_NAMESPACE,
    )

    matches = results.get("matches", [])

    if not matches:
        return False

    best_score = matches[0].get("score")

    # For euclidean distance, lower score means more similar.
    return best_score is not None and best_score < 0.15


def store_memories(memories: list[dict]):
    """
    Stores important memories in Pinecone.
    """

    if not memories:
        return

    new_memories = []

    for memory in memories:
        if not memory_already_exists(memory["text"]):
            new_memories.append(memory)

    if not new_memories:
        print("[+] No new important memories to store")
        return

    texts = [m["text"] for m in new_memories]
    embeddings = get_embedder().encode(texts)

    now = datetime.utcnow().isoformat()

    vectors = []

    for memory, emb in zip(new_memories, embeddings):
        memory_id = f"memory-{uuid.uuid4()}"

        vectors.append((
            memory_id,
            emb.tolist(),
            {
                "text": memory["text"],
                "importance": memory["importance"],
                "reason": memory.get("reason", ""),
                "created_at": now,
                "type": "conversation_memory",
            },
        ))

    get_pinecone_index().upsert(
        vectors=vectors,
        namespace=MEMORY_NAMESPACE,
    )

    print(f"[+] Stored {len(vectors)} important memory item(s)")


# ---------------------------------------------------------------------
# 8. NODE WRAPPERS FOR LANGGRAPH
# ---------------------------------------------------------------------

def router_node(state: RAGState) -> RAGState:
    """Router: decide whether document retrieval is needed."""

    question = state.get("question", "")
    if not question:
        state["error"] = "No question provided"
        return state

    # A domain agent must always ground its answer in that domain's
    # authorized document set. Generic/direct answers are only used when
    # the request is not tied to a domain.
    needs_retrieval = bool(state.get("domain")) or any(
        keyword in question.lower()
        for keyword in ["document", "pdf", "file", "context", "based on", "according to"]
    )
    state["last_agent"] = "router"
    state["needs_retrieval"] = needs_retrieval

    if needs_retrieval:
        state["sub_queries"] = decompose_query(question)
    else:
        state["sub_queries"] = []

    return state


def retrieve_documents_node(state: RAGState) -> RAGState:
    """Node: retrieve document chunks for the sub-queries."""

    question = state.get("question", "")
    sub_queries = state.get("sub_queries") or [question]

    seen_texts = set()
    all_chunks = []

    for sub_q in sub_queries:
        for chunk in retrieve_chunks(sub_q, domain=state.get("domain")):
            if chunk["text"] not in seen_texts:
                seen_texts.add(chunk["text"])
                all_chunks.append(chunk)

    state["retrieved_chunks"] = all_chunks
    state["last_agent"] = "retrieve_documents"
    return state


def retrieve_memory_node(state: RAGState) -> RAGState:
    """Node: retrieve long-term memory relevant to the question."""

    question = state.get("question", "")
    state["memories"] = retrieve_memories(question)
    state["last_agent"] = "retrieve_memory"
    return state


def direct_answer_node(state: RAGState) -> RAGState:
    """Node: answer directly without document retrieval if retrieval is not needed."""

    question = state.get("question", "")
    response = get_groq_client().chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Answer the user's question directly."},
            {"role": "user", "content": question},
        ],
        temperature=0.2,
        max_tokens=512,
    )

    state["final_answer"] = response.choices[0].message.content.strip()
    state["last_agent"] = "direct_answer"
    return state


def generate_answer_node(state: RAGState) -> RAGState:
    """Node: generate the final answer from memories and retrieved chunks."""

    question = state.get("question", "")
    memories = state.get("memories", [])
    document_results = state.get("retrieved_chunks", [])
    citations = build_citation_entries(document_results)

    print("\n--- Retrieved memories ---")

    if memories:
        for i, memory in enumerate(memories, 1):
            print(f"[{i}] {memory['text']}")
    else:
        print("No relevant stored memories found.")

    print("\n--- Retrieved document chunks ---")

    for i, result in enumerate(document_results, 1):
        print(f"\n[{i}] Score: {result['score']}")
        print(result["text"][:300] + ("..." if len(result["text"]) > 300 else ""))

    memory_context = "\n".join(f"- {memory['text']}" for memory in memories)
    document_context = "\n\n---\n\n".join(result["text"] for result in document_results)

    system_prompt = (
        "You are a helpful assistant. Answer the user's question strictly "
        "based on the provided document context. You may use stored memory "
        "only when it helps understand the user's project, preferences, or "
        "constraints. If the answer is not in the document context, say "
        "'I don't know based on the provided document.'"
    )

    user_prompt = f"""
Stored important context:
{memory_context if memory_context else "No stored memory."}

Document context:
{document_context if document_context else "No document context found."}

Question:
{question}
"""

    response = get_groq_client().chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=512,
    )

    answer = response.choices[0].message.content.strip()
    state["final_answer"] = answer
    state["citations"] = citations
    state["last_agent"] = "generate_answer"
    return state


def extract_store_memory_node(state: RAGState) -> RAGState:
    """Node: extract durable memories and store them."""

    question = state.get("question", "")
    answer = state.get("final_answer", "")
    new_memories = extract_important_context(question, answer)
    store_memories(new_memories)
    state["last_agent"] = "extract_store_memory"
    return state


def build_citation_entries(chunks: list[dict]) -> list[dict]:
    """Create citation objects from retrieved chunks for grounding."""

    citations = []
    for index, chunk in enumerate(chunks, 1):
        source = chunk.get("source") or "unknown"
        page_number = chunk.get("page_number")
        text = chunk.get("text") or ""
        citations.append({
            "id": index,
            "source": source,
            "page_number": page_number,
            "text": text,
        })

    return citations


def build_result_metadata(state: RAGState) -> dict:
    """Create a structured result payload for the frontend."""

    retrieved_chunks = state.get("retrieved_chunks", [])
    sources = []
    seen_sources = set()

    for chunk in retrieved_chunks:
        source = chunk.get("source")
        if source and source not in seen_sources:
            seen_sources.add(source)
            sources.append(source)

    confidence = 0.0
    scores = [
        float(chunk.get("score", 0))
        for chunk in retrieved_chunks
        if isinstance(chunk.get("score"), (int, float))
    ]

    if scores:
        confidence = round(max(0.0, min(1.0, sum(scores) / len(scores))), 4)

    citations = state.get("citations") or build_citation_entries(retrieved_chunks)

    return {
        "answer": state.get("final_answer", ""),
        "agent": state.get("last_agent", "unknown"),
        "path": "retrieval" if state.get("needs_retrieval") else "direct",
        "sources": sources,
        "confidence": confidence,
        "citations": citations,
    }



def answer_question(question: str, domain: str | None = None) -> dict:
    """
    Answers the user's question and returns structured metadata.
    """

    # Import here to avoid circular import between rag.py and graph.py
    from graph import build_rag_graph

    rag_graph = build_rag_graph()

    state: RAGState = {
        "question": question,
        "domain": domain,
        "sub_queries": [],
        "retrieved_chunks": [],
        "memories": [],
        "final_answer": "",
        "citations": [],
        "last_agent": "answer_question",
        "error": "",
        "needs_retrieval": False,
    }

    result = rag_graph.invoke(state)
    metadata = build_result_metadata(result)
    result["metadata"] = metadata

    return metadata

# ---------------------------------------------------------------------
# 9. MAIN
# ---------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  Upload PDF     : python rag_pinecone.py upload <path/to/file.pdf>")
        print("  Ask a question : python rag_pinecone.py ask \"Your question here\"")
        sys.exit(0)

    mode = sys.argv[1].lower()

    if mode == "upload":
        if len(sys.argv) < 3:
            print("Provide PDF path:")
            print("python rag_pinecone.py upload <file.pdf>")
            sys.exit(1)

        upload_pdf(sys.argv[2])

    elif mode == "ask":
        if len(sys.argv) < 3:
            print("Provide a question:")
            print("python rag_pinecone.py ask \"Your question here\"")
            sys.exit(1)

        questions = sys.argv[2:]

        for idx, question in enumerate(questions, 1):
            if len(questions) > 1:
                print(f"\n{'=' * 55}")
                print(f"Query {idx}/{len(questions)}: {question}")
                print(f"{'=' * 55}")
            else:
                print(f"\nQ: {question}")

            answer = answer_question(question)
            print(f"\nA: {answer}")

    else:
        print(f"Unknown mode '{mode}'. Use 'upload' or 'ask'.")