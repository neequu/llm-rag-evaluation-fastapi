import json

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    answer_relevancy,
    faithfulness,
)

with open("evaluation/results.json", "r") as f:
    results = json.load(f)
    dataset = Dataset.from_dict(
        {
            "question": [r["query"] for r in results],
            "answer": [r["answer"] for r in results],
            "contexts": [r["contexts"] for r in results],
            "ground_truth": [r["ground_truth"] for r in results],
        }
    )
    dataset = Dataset.from_dict(
        {
            "question": [r["query"] for r in results],
            "answer": [r["answer"] for r in results],
            "contexts": [r["contexts"] for r in results],
            "ground_truth": [r["ground_truth"] for r in results],
        }
    )

    scores = evaluate(
        dataset=dataset,
        metrics=[
            faithfulness,
            answer_relevancy,
        ],
    )

    df = scores.to_pandas()

    df.to_csv(
        "evaluation/ragas_results.csv",
        index=False,
    )
