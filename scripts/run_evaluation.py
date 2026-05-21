import asyncio
import json

from app.db.db import AsyncSessionLocal
from app.services.rag_service import RAGService

WORKSPACE_ID = "a09ce400-7ba9-45c1-8e4a-f4b10b5fc008"


async def run():
    with open("evaluation/test_queries.json", "r") as f:
        questions = json.load(f)

    results = []
    strategies = ["bm25", "dense", "hybrid"]

    async with AsyncSessionLocal() as db:
        for strategy in strategies:
            print(f"\nRunning strategy: {strategy}")
            for i, item in enumerate(questions):
                print(f"  [{i + 1}/{len(questions)}] {item['query'][:60]}...")
                result = await RAGService.generate_answer(
                    db=db,
                    workspace_id=WORKSPACE_ID,
                    query=item["query"],
                    strategy=strategy,
                    limit=3,
                )
                results.append(
                    {
                        "strategy": strategy,
                        "query": item["query"],
                        "ground_truth": item["ground_truth"],
                        "question_type": item.get("question_type", "unknown"),
                        "answer": result["answer"],
                        "retrieved_chunks": result["retrieved_chunks"],
                        "retrieval_latency_ms": result["retrieval_latency_ms"],
                        "generation_latency_ms": result["generation_latency_ms"],
                        "total_latency_ms": result["total_latency_ms"],
                    }
                )

    with open("evaluation/results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nDone. {len(results)} results saved to evaluation/results.json")


if __name__ == "__main__":
    asyncio.run(run())
