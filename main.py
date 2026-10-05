import logging
from fastapi import FastAPI
import inngest
import inngest.fast_api
from inngest.experimental import ai
from dotenv import load_dotenv
import uuid
import os
import datetime
from data_loader import load_and_chunk_file, embed_texts
from vector_db import QdrantStorage
from custom_types import RAQQueryResult, RAGSearchResult, RAGUpsertResult, RAGChunkAndSrc
from rag_utils import build_rag_prompt

load_dotenv()


def _friendly_openai_error(exc: Exception) -> str:
    message = str(exc).lower()
    if any(token in message for token in ["credit_balance_exhausted", "insufficient_quota", "429", "quota", "rate limit"]):
        return "The OpenAI API is unavailable because the account has no remaining credits. Add billing credits or use a different API key."
    if "api key" in message or "authentication" in message:
        return "The OpenAI API key is missing or invalid. Check your environment configuration."
    return f"The AI service failed: {exc}"


inngest_client = inngest.Inngest(
    app_id="rag_app",
    logger=logging.getLogger("uvicorn"),
    is_production=False,
    serializer=inngest.PydanticSerializer()
)

@inngest_client.create_function(
    fn_id="RAG: Ingest PDF",
    trigger=inngest.TriggerEvent(event="rag/ingest_document"),
    throttle=inngest.Throttle(
        limit=2, period=datetime.timedelta(minutes=1)
    ),
    rate_limit=inngest.RateLimit(
        limit=1,
        period=datetime.timedelta(hours=4),
        key="event.data.source_id",
  ),
)
async def rag_ingest_pdf(ctx: inngest.Context):
    def _load(ctx: inngest.Context) -> RAGChunkAndSrc:
        file_path = ctx.event.data["file_path"]
        source_id = ctx.event.data.get("source_id", file_path)
        chunks = load_and_chunk_file(file_path)
        return RAGChunkAndSrc(chunks=chunks, source_id=source_id)

    def _upsert(chunks_and_src: RAGChunkAndSrc) -> RAGUpsertResult:
        try:
            chunks = chunks_and_src.chunks
            source_id = chunks_and_src.source_id
            vecs = embed_texts(chunks)
            ids = [str(uuid.uuid5(uuid.NAMESPACE_URL, f"{source_id}:{i}")) for i in range(len(chunks))]
            payloads = [{"source": source_id, "text": chunks[i]} for i in range(len(chunks))]
            QdrantStorage().upsert(ids, vecs, payloads)
            return RAGUpsertResult(ingested=len(chunks))
        except Exception as exc:
            return RAGUpsertResult(ingested=0, error=_friendly_openai_error(exc))

    chunks_and_src = await ctx.step.run("load-and-chunk", lambda: _load(ctx), output_type=RAGChunkAndSrc)
    ingested = await ctx.step.run("embed-and-upsert", lambda: _upsert(chunks_and_src), output_type=RAGUpsertResult)
    return ingested.model_dump()


@inngest_client.create_function(
    fn_id="RAG: Query PDF",
    trigger=inngest.TriggerEvent(event="rag/query_pdf_ai")
)
async def rag_query_pdf_ai(ctx: inngest.Context):
    def _search(question: str, top_k: int = 5) -> RAGSearchResult:
        try:
            query_vec = embed_texts([question])[0]
            store = QdrantStorage()
            found = store.search(query_vec, top_k, query_text=question)
            return RAGSearchResult(contexts=found["contexts"], sources=found["sources"])
        except Exception as exc:
            return RAGSearchResult(contexts=[], sources=[], error=_friendly_openai_error(exc))

    question = ctx.event.data["question"]
    top_k = int(ctx.event.data.get("top_k", 5))
    chat_history = ctx.event.data.get("chat_history", []) or []

    found = await ctx.step.run("embed-and-search", lambda: _search(question, top_k), output_type=RAGSearchResult)

    if found.error:
        return {
            "answer": found.error,
            "sources": [],
            "num_contexts": 0,
            "error": found.error,
        }

    if not found.contexts:
        return {
            "answer": "I couldn't find relevant information in the uploaded documents.",
            "sources": [],
            "num_contexts": 0,
        }

    context_block = "\n\n".join(f"- {c}" for c in found.contexts)
    user_content = build_rag_prompt(question, context_block, chat_history)

    try:
        adapter = ai.openai.Adapter(
            auth_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-4o-mini"
        )

        res = await ctx.step.ai.infer(
            "llm-answer",
            adapter=adapter,
            body={
                "max_tokens": 1024,
                "temperature": 0.2,
                "messages": [
                    {"role": "system", "content": "You answer questions using only the provided context and previous conversation when relevant."},
                    {"role": "user", "content": user_content}
                ]
            }
        )

        answer = res["choices"][0]["message"]["content"].strip()
        return {"answer": answer, "sources": found.sources, "num_contexts": len(found.contexts)}
    except Exception as exc:
        return {
            "answer": _friendly_openai_error(exc),
            "sources": found.sources,
            "num_contexts": len(found.contexts),
            "error": _friendly_openai_error(exc),
        }

app = FastAPI()

inngest.fast_api.serve(app, inngest_client, [rag_ingest_pdf, rag_query_pdf_ai])