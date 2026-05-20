import asyncio
import json
from dataclasses import dataclass

from app.db.db import AsyncSessionLocal
from app.services.rag_service import RAGService

WORKSPACE_ID = "a09ce400-7ba9-45c1-8e4a-f4b10b5fc008"


@dataclass
class EvaluationResult:
    strategy: str
    query: str
    ground_truth: str
    answer: str
    contexts: list[str]
    retrieval_latency_ms: float
    generation_latency_ms: float
    total_latency_ms: float


async def run():

    with open("evaluation/test_queries.json", "r") as f:
        questions = json.load(f)

    results = []

    strategies = [
        "bm25",
        "dense",
        "hybrid",
    ]

    async with AsyncSessionLocal() as db:
        for strategy in strategies:
            print(f"Running strategy: {strategy}")

            for item in questions:
                query = item["query"]
                ground_truth = item["ground_truth"]

                result = await RAGService.generate_answer(
                    db=db,
                    workspace_id=WORKSPACE_ID,
                    query=query,
                    strategy=strategy,
                    limit=5,
                )

                results.append(
                    {
                        "strategy": strategy,
                        "query": query,
                        "ground_truth": ground_truth,
                        "answer": result["answer"],
                        "contexts": result["retrieved_chunks"],
                        "retrieval_latency_ms": result["retrieval_latency_ms"],
                        "generation_latency_ms": result["generation_latency_ms"],
                        "total_latency_ms": result["total_latency_ms"],
                    }
                )

    with open("evaluation/results.json", "w") as f:
        json.dump(results, f, indent=2)


if __name__ == "__main__":
    asyncio.run(run())
