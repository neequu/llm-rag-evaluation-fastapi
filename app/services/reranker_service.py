from sentence_transformers import CrossEncoder

reranker_model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


class RerankerService:
    @staticmethod
    def rerank(
        query: str,
        chunks: list[str],
    ):
        pairs = [(query, chunk) for chunk in chunks]

        scores = reranker_model.predict(pairs)

        ranked = sorted(
            zip(chunks, scores),
            key=lambda x: x[1],
            reverse=True,
        )

        return ranked
