from sqlalchemy import func, select

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.schemas.retrieval import RetrievalResult
from app.services.chroma_service import chroma_service
from app.services.embedding_service import generate_embeddings


class RetrievalService:
    @staticmethod
    async def dense_search(
        *,
        db,
        workspace_id: str,
        query: str,
        limit: int = 5,
    ) -> list[RetrievalResult]:

        query_embedding = generate_embeddings([query])[0]

        chroma_result = await chroma_service.query(
            workspace_id=workspace_id,
            embedding=query_embedding,
            limit=limit,
        )

        ids = chroma_result["ids"][0]
        documents = chroma_result["documents"][0]
        metadatas = chroma_result["metadatas"][0]
        distances = chroma_result["distances"][0]

        results = []

        for chunk_id, content, metadata, distance in zip(
            ids,
            documents,
            metadatas,
            distances,
            strict=False,
        ):
            db_query = select(DocumentChunk).where(DocumentChunk.chroma_id == chunk_id)

            db_result = await db.execute(db_query)

            chunk = db_result.scalar_one()

            results.append(
                RetrievalResult(
                    chunk_id=chunk.id,
                    document_id=chunk.document_id,
                    content=content,
                    score=float(distance),
                    strategy="dense",
                )
            )

        return results

    @staticmethod
    async def bm25_search(
        *,
        db,
        workspace_id,
        query: str,
        limit: int = 5,
    ) -> list[RetrievalResult]:

        ts_query = func.plainto_tsquery("english", query)

        rank = func.ts_rank_cd(
            func.to_tsvector("english", DocumentChunk.content),
            ts_query,
        )

        stmt = (
            select(DocumentChunk, rank)
            .join(Document)
            .where(
                Document.workspace_id == workspace_id,
                func.to_tsvector(
                    "english",
                    DocumentChunk.content,
                ).op("@@")(ts_query),
            )
            .order_by(rank.desc())
            .limit(limit)
        )

        result = await db.execute(stmt)

        rows = result.all()

        retrieval_results = []

        for chunk, score in rows:
            retrieval_results.append(
                RetrievalResult(
                    chunk_id=chunk.id,
                    document_id=chunk.document_id,
                    content=chunk.content,
                    score=float(score),
                    strategy="bm25",
                )
            )

        return retrieval_results

    @staticmethod
    async def hybrid_search(
        *,
        db,
        workspace_id,
        query: str,
        limit: int = 5,
    ) -> list[RetrievalResult]:

        dense_results = await RetrievalService.dense_search(
            db=db,
            workspace_id=workspace_id,
            query=query,
            limit=limit,
        )

        bm25_results = await RetrievalService.bm25_search(
            db=db,
            workspace_id=workspace_id,
            query=query,
            limit=limit,
        )

        merged = {}

        for result in dense_results + bm25_results:
            key = str(result.chunk_id)

            if key not in merged:
                merged[key] = result
            else:
                merged[key].score += result.score

        ranked = sorted(
            merged.values(),
            key=lambda x: x.score,
            reverse=True,
        )

        return ranked[:limit]
