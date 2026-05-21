from rank_bm25 import BM25Okapi

from app.models.document_chunk import DocumentChunk


class BM25Service:
    _cache: dict[str, tuple[list[DocumentChunk], BM25Okapi]] = {}

    @staticmethod
    def tokenize(text: str) -> list[str]:
        return text.lower().split()

    @staticmethod
    def build_index(chunks: list[DocumentChunk]):
        tokenized_chunks = [BM25Service.tokenize(chunk.content) for chunk in chunks]
        return BM25Okapi(tokenized_chunks)

    @staticmethod
    def get_or_build_index(
        workspace_id: str,
        chunks: list[DocumentChunk],
    ) -> tuple[list[DocumentChunk], BM25Okapi]:
        if workspace_id not in BM25Service._cache:
            bm25 = BM25Service.build_index(chunks)
            BM25Service._cache[workspace_id] = (chunks, bm25)
        return BM25Service._cache[workspace_id]

    @staticmethod
    def invalidate(workspace_id: str) -> None:
        """Call this when documents are added or deleted from a workspace."""
        BM25Service._cache.pop(workspace_id, None)

    @staticmethod
    def search(
        bm25: BM25Okapi,
        chunks: list[DocumentChunk],
        query: str,
        limit: int = 3,
    ):
        tokenized_query = BM25Service.tokenize(query)
        scores = bm25.get_scores(tokenized_query)
        ranked = sorted(
            zip(chunks, scores),
            key=lambda x: x[1],
            reverse=True,
        )
        return ranked[:limit]
