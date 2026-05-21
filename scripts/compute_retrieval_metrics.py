import json

import pandas as pd

with open("evaluation/results.json", "r") as f:
    results = json.load(f)

with open("evaluation/test_queries.json", "r") as f:
    queries = json.load(f)

gt_lookup = {q["query"]: set(q.get("chunk_ids", [])) for q in queries}

rows = []

for r in results:
    gt_ids = gt_lookup.get(r["query"], set())
    retrieved_ids = [c["chunk_id"] for c in r["retrieved_chunks"]]
    k = len(retrieved_ids)

    if gt_ids:
        hits = sum(1 for cid in retrieved_ids if cid in gt_ids)
        precision_at_k = hits / k if k > 0 else 0.0
        recall_at_k = hits / len(gt_ids) if gt_ids else 0.0
    else:
        precision_at_k = None
        recall_at_k = None

    rows.append(
        {
            "strategy": r["strategy"],
            "query": r["query"],
            "question_type": r.get("question_type", "unknown"),
            "precision_at_k": precision_at_k,
            "recall_at_k": recall_at_k,
            "k": k,
            "retrieval_latency_ms": r["retrieval_latency_ms"],
            "generation_latency_ms": r["generation_latency_ms"],
            "total_latency_ms": r["total_latency_ms"],
            "answer_length_chars": len(r["answer"]),
            "answer_length_words": len(r["answer"].split()),
        }
    )

df = pd.DataFrame(rows)
df.to_csv("evaluation/retrieval_metrics.csv", index=False)

print("\n=== Precision@k and Recall@k by strategy ===")
print(df.groupby("strategy")[["precision_at_k", "recall_at_k"]].mean().round(4))

print("\n=== Latency breakdown by strategy (ms) ===")
print(
    df.groupby("strategy")[
        ["retrieval_latency_ms", "generation_latency_ms", "total_latency_ms"]
    ]
    .mean()
    .round(1)
)

print("\n=== By strategy and question type ===")
print(
    df.groupby(["strategy", "question_type"])[["precision_at_k", "recall_at_k"]]
    .mean()
    .round(4)
)
