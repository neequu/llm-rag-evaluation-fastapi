import os

import matplotlib.pyplot as plt
import pandas as pd

retrieval_df = pd.read_csv("evaluation/retrieval_metrics.csv")

additional_df = pd.read_csv("evaluation/additional_retrieval_metrics.csv")


df = pd.merge(
    retrieval_df,
    additional_df,
    on=["strategy", "query", "question_type"],
    how="inner",
)


PLOT_DIR = "evaluation/plots"

os.makedirs(PLOT_DIR, exist_ok=True)


summary = (
    df.groupby("strategy")
    .agg(
        {
            "precision_at_k": "mean",
            "recall_at_k": "mean",
            "hit_at_k": "mean",
            "reciprocal_rank": "mean",
            "retrieval_latency_ms": "mean",
            "generation_latency_ms": "mean",
            "total_latency_ms": "mean",
        }
    )
    .rename(columns={"reciprocal_rank": "MRR"})
)

# 1. Precision@k

plt.figure(figsize=(6, 4))

summary["precision_at_k"].plot(kind="bar")

plt.ylabel("Precision@k")
plt.title("Precision@k by Retrieval Strategy")

plt.xticks(rotation=0)

plt.tight_layout()

plt.savefig(f"{PLOT_DIR}/precision_at_k.png")

plt.close()

# 2. Recall@k

plt.figure(figsize=(6, 4))

summary["recall_at_k"].plot(kind="bar")

plt.ylabel("Recall@k")
plt.title("Recall@k by Retrieval Strategy")

plt.xticks(rotation=0)

plt.tight_layout()

plt.savefig(f"{PLOT_DIR}/recall_at_k.png")

plt.close()

# 3. Hit@k

plt.figure(figsize=(6, 4))

summary["hit_at_k"].plot(kind="bar")

plt.ylabel("Hit@k")
plt.title("Hit@k by Retrieval Strategy")

plt.xticks(rotation=0)

plt.tight_layout()

plt.savefig(f"{PLOT_DIR}/hit_at_k.png")

plt.close()

# 4. MRR

plt.figure(figsize=(6, 4))

summary["MRR"].plot(kind="bar")

plt.ylabel("MRR")
plt.title("Mean Reciprocal Rank by Retrieval Strategy")

plt.xticks(rotation=0)

plt.tight_layout()

plt.savefig(f"{PLOT_DIR}/mrr.png")

plt.close()

# 5. Latency breakdown

latency_df = summary[
    [
        "retrieval_latency_ms",
        "generation_latency_ms",
        "total_latency_ms",
    ]
]

latency_df.plot(
    kind="bar",
    figsize=(8, 5),
)

plt.ylabel("Latency (ms)")
plt.title("Latency Breakdown by Retrieval Strategy")

plt.xticks(rotation=0)

plt.tight_layout()

plt.savefig(f"{PLOT_DIR}/latency_breakdown.png")

plt.close()

# 6. Metrics by question type

question_type_summary = (
    df.groupby(["strategy", "question_type"])
    .agg(
        {
            "precision_at_k": "mean",
            "recall_at_k": "mean",
        }
    )
    .reset_index()
)

for metric in ["precision_at_k", "recall_at_k"]:
    pivot_df = question_type_summary.pivot(
        index="question_type",
        columns="strategy",
        values=metric,
    )

    pivot_df.plot(
        kind="bar",
        figsize=(8, 5),
    )

    plt.ylabel(metric)
    plt.title(f"{metric} by Question Type")

    plt.xticks(rotation=0)

    plt.tight_layout()

    plt.savefig(f"{PLOT_DIR}/{metric}_by_question_type.png")

    plt.close()

print("\nSaved plots to:")
print(f"  {PLOT_DIR}/")

print("\nGenerated plots:")
print("- precision_at_k.png")
print("- recall_at_k.png")
print("- hit_at_k.png")
print("- mrr.png")
print("- latency_breakdown.png")
print("- precision_at_k_by_question_type.png")
print("- recall_at_k_by_question_type.png")
