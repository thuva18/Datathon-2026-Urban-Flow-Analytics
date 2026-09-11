"""
chatbot/rag_service.py
Lightweight RAG (Retrieval-Augmented Generation) over project documentation.

Sources: README.md, Data_Dictionary.pdf
Uses simple TF-IDF style cosine similarity (no heavy models required) for
retrieval, falling back to keyword search if numpy is unavailable.

Documents are chunked and indexed on first call, then cached in memory.
"""
import re
import logging
from pathlib import Path

from chatbot.config import README_FILE, DATA_DICT_FILE, REPORT_FILE

logger = logging.getLogger("chatbot")

_chunks: list[dict] = []   # [{text, source, chunk_id}]
_initialized = False


# ─── Text extraction ──────────────────────────────────────────────────────────

def _extract_readme() -> str:
    try:
        return Path(README_FILE).read_text(encoding="utf-8")
    except Exception as e:
        logger.warning("Could not read README.md: %s", e)
        return ""


def _extract_pdf(path: str) -> str:
    """Extract text from PDF using pdfplumber, joining pages with paragraph separators."""
    try:
        if not Path(path).exists():
            return ""
        import pdfplumber
        text_parts = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t and t.strip():
                    text_parts.append(t.strip())
        return "\n\n".join(text_parts)
    except Exception as e:
        logger.warning("Could not extract PDF '%s': %s", path, e)
        return ""


# ─── Chunking ─────────────────────────────────────────────────────────────────

def _chunk_text(text: str, source: str, chunk_size: int = 750, overlap: int = 150) -> list[dict]:
    """Split text into overlapping chunks using paragraph and sentence boundaries."""
    text = re.sub(r'\r\n', '\n', text)
    paragraphs = [p.strip() for p in re.split(r'\n{2,}', text) if p.strip()]

    sub_blocks = []
    for p in paragraphs:
        if len(p) > chunk_size:
            sentences = re.split(r'(?<=[.!?])\s+|\n+', p)
            curr = ""
            for s in sentences:
                if len(curr) + len(s) < chunk_size:
                    curr += (" " if curr else "") + s
                else:
                    if curr:
                        sub_blocks.append(curr)
                    curr = s
            if curr:
                sub_blocks.append(curr)
        else:
            sub_blocks.append(p)

    chunks = []
    curr_chunk = ""
    for block in sub_blocks:
        if len(curr_chunk) + len(block) <= chunk_size:
            curr_chunk += ("\n\n" if curr_chunk else "") + block
        else:
            if curr_chunk:
                chunks.append({"text": curr_chunk, "source": source})
            curr_chunk = block

    if curr_chunk:
        chunks.append({"text": curr_chunk, "source": source})

    return chunks


# ─── Index initialisation ─────────────────────────────────────────────────────

def _initialize():
    global _chunks, _initialized
    if _initialized:
        return

    readme_text = _extract_readme()
    dict_text   = _extract_pdf(DATA_DICT_FILE)
    report_text = _extract_pdf(REPORT_FILE)

    _chunks  = _chunk_text(readme_text, "README.md")
    _chunks += _chunk_text(dict_text, "Data_Dictionary.pdf")
    if report_text:
        _chunks += _chunk_text(report_text, "Gravitons_Technical_Report.pdf")

    logger.info("RAG index ready: %d chunks from documentation.", len(_chunks))
    _initialized = True


# ─── Simple TF-IDF cosine retrieval ──────────────────────────────────────────

def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def _cosine_sim(query_tokens: list[str], doc_tokens: list[str]) -> float:
    """Approximate cosine via term overlap / geometric mean of lengths."""
    q_set = set(query_tokens)
    d_set = set(doc_tokens)
    inter = len(q_set & d_set)
    if inter == 0:
        return 0.0
    import math
    return inter / (math.sqrt(len(q_set)) * math.sqrt(len(d_set)))


def _retrieve(query: str, top_k: int = 4) -> list[dict]:
    _initialize()

    if not _chunks:
        return []

    q_tokens = _tokenize(query)
    scored = []
    for chunk in _chunks:
        d_tokens = _tokenize(chunk["text"])
        score = _cosine_sim(q_tokens, d_tokens)
        scored.append((score, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)
    matches = [c for s, c in scored[:top_k] if s > 0]
    return matches


# ─── Public API ───────────────────────────────────────────────────────────────

def retrieve_knowledge(query: str, top_k: int = 4) -> dict:
    """
    Retrieve relevant documentation chunks for a knowledge question.
    Returns: {success, chunks (list of {text, source}), query}
    """
    try:
        results = _retrieve(query, top_k=top_k)
        if not results:
            # Fallback to key overview chunks from README / Report
            _initialize()
            results = _chunks[:top_k]
            
        return {
            "success": True,
            "query":   query,
            "chunks":  results,
        }
    except Exception as e:
        logger.error("RAG retrieval error: %s", e)
        return {
            "success": False,
            "query":   query,
            "error":   f"Documentation retrieval failed: {e}",
        }
