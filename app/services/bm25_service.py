from rank_bm25 import BM25Okapi

from app.models.document_chunk import DocumentChunk


class BM25Service:
    @staticmethod
    def tokenize(text: str) -> list[str]:
        return text.lower().split()

    @staticmethod
    def build_index(chunks: list[DocumentChunk]):
        tokenized_chunks = [BM25Service.tokenize(chunk.content) for chunk in chunks]

        bm25 = BM25Okapi(tokenized_chunks)

        return bm25

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
