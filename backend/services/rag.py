"""
RAG (Retrieval-Augmented Generation) service.

Supports two LLM providers, switched via LLM_PROVIDER in .env:
  - "openai"  — OpenAI ChatOpenAI + OpenAIEmbeddings (default)
  - "ollama"  — local Ollama ChatOllama + OllamaEmbeddings (no API key needed)

Provides:
- get_vector_store()  — singleton ChromaDB vector store
- answer_with_rag()   — retrieves relevant docs then streams an LLM response
"""

import logging
from collections.abc import AsyncIterator
from functools import lru_cache

from langchain_chroma import Chroma
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from config import get_settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a helpful assistant that answers questions based on the user's documents.
Your job is to help users understand their uploaded documents by answering \
questions based on the provided documentation.

Rules:
- Answer based on the retrieved documentation excerpts provided below.
- If the documentation does not contain enough information to answer, say so clearly. Do not make things up.
- Be concise, accurate, and friendly.
- Use markdown formatting (bullet points, code blocks, tables) when it improves readability.
- PRIORITY RULE: If any excerpt contains a direct confirmation or first-hand account that a specific
  action resolved an issue (e.g. in a chat log, meeting note, or personal work note), present
  that confirmed fix FIRST and prominently — before any generic troubleshooting steps. Quote the source
  directly. Generic steps come after, clearly labelled as secondary.
"""

TOP_K = 10


def _make_embeddings():
    settings = get_settings()
    if settings.llm_provider == "ollama":
        from langchain_ollama import OllamaEmbeddings
        logger.info("Using Ollama embeddings: %s", settings.ollama_embedding_model)
        return OllamaEmbeddings(
            model=settings.ollama_embedding_model,
            base_url=settings.ollama_base_url,
        )
    else:
        from langchain_openai import OpenAIEmbeddings
        logger.info("Using OpenAI embeddings: %s", settings.openai_embedding_model)
        return OpenAIEmbeddings(
            model=settings.openai_embedding_model,
            api_key=settings.openai_api_key,
        )


def _make_llm():
    settings = get_settings()
    if settings.llm_provider == "ollama":
        from langchain_ollama import ChatOllama
        logger.info("Using Ollama LLM: %s", settings.ollama_model)
        return ChatOllama(
            model=settings.ollama_model,
            base_url=settings.ollama_base_url,
            temperature=0.2,
            # Disable Qwen3 chain-of-thought thinking mode — not needed for RAG Q&A
            # and roughly halves response latency. Has no effect on other models.
            think=False,
        )
    else:
        from langchain_openai import ChatOpenAI
        logger.info("Using OpenAI LLM: %s", settings.openai_model)
        return ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            streaming=True,
            temperature=0.2,
        )


@lru_cache(maxsize=1)
def get_vector_store() -> Chroma:
    settings = get_settings()
    try:
        return Chroma(
            collection_name="pocketnotelm_docs",
            embedding_function=_make_embeddings(),
            persist_directory=settings.chroma_persist_dir,
        )
    except Exception as exc:
        raise RuntimeError(
            f"Failed to initialise ChromaDB at '{settings.chroma_persist_dir}': {exc}"
        ) from exc


@lru_cache(maxsize=1)
def get_llm():
    return _make_llm()


def _reorder_for_lost_in_middle(
    results: list[tuple],
) -> list[tuple]:
    """
    Mitigate the 'lost in the middle' problem: LLMs pay most attention to
    content at the start and end of their context window, and tend to ignore
    content in the middle. So we place the highest-scoring chunk first, the
    second-highest last, and fill the middle with the remaining chunks.

    Example for 5 chunks ranked [A, B, C, D, E] by score:
      Output order: [A, C, D, E, B]
    """
    if len(results) <= 2:
        return results
    best = results[0]
    second_best = results[1]
    middle = results[2:]
    return [best] + middle + [second_best]


def _retrieve_context(query: str) -> str:
    vector_store = get_vector_store()
    results = vector_store.similarity_search_with_relevance_scores(query, k=TOP_K)
    if not results:
        logger.info("RAG retrieval: no chunks found for query: %s", query[:80])
        return ""

    logger.info("RAG retrieval for query: %r", query[:80])
    for i, (doc, score) in enumerate(results, 1):
        source = doc.metadata.get("source", "unknown")
        page = doc.metadata.get("page", "?")
        preview = doc.page_content[:120].replace("\n", " ")
        logger.info("  [%d] score=%.4f  src=%s  page=%s  preview: %s", i, score, source, page, preview)

    # Reorder to reduce lost-in-the-middle effect before passing to LLM
    reordered = _reorder_for_lost_in_middle(results)
    parts = []
    for i, (doc, _score) in enumerate(reordered, 1):
        source = doc.metadata.get("source", "unknown")
        page = doc.metadata.get("page", "?")
        parts.append(f"[{i}] (Source: {source}, page {page})\n{doc.page_content}")
    return "\n\n".join(parts)


async def answer_with_rag(
    question: str,
    history: list[dict[str, str]],
) -> AsyncIterator[str]:
    """
    Retrieve relevant doc chunks, build a prompt, and stream the LLM response.
    Yields string tokens one at a time.
    """
    context = _retrieve_context(question)

    system_content = SYSTEM_PROMPT
    if context:
        system_content += f"\n\n--- Retrieved Documentation ---\n{context}\n---"

    messages = [SystemMessage(content=system_content)]
    for msg in history[-10:]:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(AIMessage(content=msg["content"]))
    messages.append(HumanMessage(content=question))

    llm = get_llm()
    async for chunk in llm.astream(messages):
        token = chunk.content
        if token:
            yield token

