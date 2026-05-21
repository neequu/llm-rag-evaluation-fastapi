import json

import pandas as pd

TOP_K = 3

with open("evaluation/results.json", "r") as f:
    results = json.load(f)

with open("evaluation/test_queries.json", "r") as f:
    queries = json.load(f)

gt_lookup = {q["query"]: set(q.get("chunk_ids", [])) for q in queries}

rows = []

for r in results:
    gt_ids = gt_lookup.get(r["query"], set())

    retrieved_ids = [c["chunk_id"] for c in r["retrieved_chunks"]]

    # Hit@k
    hit_at_k = int(any(cid in gt_ids for cid in retrieved_ids[:TOP_K]))

    # Reciprocal Rank

    reciprocal_rank = 0.0

    for rank, cid in enumerate(retrieved_ids, start=1):
        if cid in gt_ids:
            reciprocal_rank = 1.0 / rank
            break

    rows.append(
        {
            "strategy": r["strategy"],
            "query": r["query"],
            "question_type": r.get("question_type", "unknown"),
            "hit_at_k": hit_at_k,
            "reciprocal_rank": reciprocal_rank,
        }
    )

df = pd.DataFrame(rows)

summary = (
    df.groupby("strategy")
    .agg(
        {
            "hit_at_k": "mean",
            "reciprocal_rank": "mean",
        }
    )
    .rename(columns={"reciprocal_rank": "MRR"})
)

df.to_csv("evaluation/additional_retrieval_metrics.csv", index=False)

summary.to_csv("evaluation/additional_retrieval_metrics_summary.csv")

print("\n=== Additional Retrieval Metrics ===")
print(summary.round(4))

print("\nSaved:")
print("- evaluation/additional_retrieval_metrics.csv")
print("- evaluation/additional_retrieval_metrics_summary.csv")
