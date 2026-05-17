import time

from app.schemas.retrieval import StrategyName
from app.services.ollama_service import ollama_service
from app.services.prompt_service import build_rag_prompt
from app.services.retrieval_service import RetrievalService


class RAGService:
    @staticmethod
    async def generate_answer(
        *,
        db,
        workspace_id,
        query: str,
        strategy: str,
        limit: int = 5,
    ):
        retrieval_start = time.perf_counter()

        if strategy == StrategyName.DENSE:
            retrieval_results = await RetrievalService.dense_search(
                db=db,
                workspace_id=workspace_id,
                query=query,
                limit=limit,
            )

        elif strategy == StrategyName.BM25:
            retrieval_results = await RetrievalService.bm25_search(
                db=db,
                workspace_id=workspace_id,
                query=query,
                limit=limit,
            )

        elif strategy == StrategyName.HYBRID:
            retrieval_results = await RetrievalService.hybrid_search(
                db=db,
                workspace_id=workspace_id,
                query=query,
                limit=limit,
            )

        else:
            raise ValueError("Invalid retrieval strategy")

        retrieval_latency_ms = (time.perf_counter() - retrieval_start) * 1000

        MAX_CHUNKS = 2  # Try 2 instead of 5
        MAX_CHARS_PER_CHUNK = 400

        contexts = []
        for r in retrieval_results[:MAX_CHUNKS]:
            content = r.content
            if len(content) > MAX_CHARS_PER_CHUNK:
                content = content[:MAX_CHARS_PER_CHUNK] + "..."
            contexts.append(content)

        prompt = build_rag_prompt(
            query=query,
            contexts=contexts,
        )

        generation_start = time.perf_counter()
        answer = await ollama_service.generate(prompt)

        generation_latency_ms = (time.perf_counter() - generation_start) * 1000

        total_latency_ms = retrieval_latency_ms + generation_latency_ms

        return {
            "answer": answer,
            "retrieved_chunks": contexts,
            "retrieval_strategy": strategy,
            "generation_latency_ms": generation_latency_ms,
            "retrieval_latency_ms": retrieval_latency_ms,
            "total_latency_ms": total_latency_ms,
        }
