from sqlalchemy import select

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.bm25_service import BM25Service
from app.services.chroma_service import chroma_service
from app.services.embedding_service import generate_embeddings
from app.services.hybrid_service import reciprocal_rank_fusion
from app.services.reranker_service import RerankerService


class RetrievalService:
    @staticmethod
    async def dense_search(
        db,
        workspace_id: str,
        query: str,
        limit: int = 3,
    ):

        embedding = generate_embeddings([query])[0]

        results = await chroma_service.query(
            workspace_id=workspace_id,
            embedding=embedding,
            limit=limit,
        )

        chunk_ids = results["ids"][0]

        stmt = select(DocumentChunk).where(DocumentChunk.chroma_id.in_(chunk_ids))

        result = await db.execute(stmt)

        return list(result.scalars())

    @staticmethod
    async def bm25_search(
        db,
        workspace_id: str,
        query: str,
        limit: int = 3,
    ):

        stmt = (
            select(DocumentChunk)
            .join(DocumentChunk.document)
            .where(Document.workspace_id == workspace_id)
        )

        result = await db.execute(stmt)

        chunks = list(result.scalars())

        bm25 = BM25Service.build_index(chunks)

        ranked = BM25Service.search(
            bm25=bm25,
            chunks=chunks,
            query=query,
            limit=limit,
        )

        return [chunk for chunk, _score in ranked]

    @staticmethod
    async def hybrid_search(
        db,
        workspace_id: str,
        query: str,
        limit: int = 3,
    ):

        bm25_chunks = await RetrievalService.bm25_search(
            db=db,
            workspace_id=workspace_id,
            query=query,
            limit=20,
        )

        dense_chunks = await RetrievalService.dense_search(
            db=db,
            workspace_id=workspace_id,
            query=query,
            limit=20,
        )

        bm25_ids = [str(chunk.id) for chunk in bm25_chunks]

        dense_ids = [str(chunk.id) for chunk in dense_chunks]

        fused = reciprocal_rank_fusion(
            [
                bm25_ids,
                dense_ids,
            ]
        )

        fused_ids = [doc_id for doc_id, _score in fused[:20]]

        all_chunks = {str(chunk.id): chunk for chunk in (bm25_chunks + dense_chunks)}

        rerank_candidates = [
            all_chunks[doc_id] for doc_id in fused_ids if doc_id in all_chunks
        ]

        reranked = RerankerService.rerank(
            query=query,
            chunks=[chunk.content for chunk in rerank_candidates],
        )

        final_chunks = []

        for content, _score in reranked[:limit]:
            for chunk in rerank_candidates:
                if chunk.content == content:
                    final_chunks.append(chunk)
                    break

        return final_chunks
