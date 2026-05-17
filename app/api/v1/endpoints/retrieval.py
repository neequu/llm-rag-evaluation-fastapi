from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.db.db import AsyncSession
from app.schemas.retrieval import RetrievalRequest, RetrievalResponse, StrategyName
from app.services.retrieval_service import RetrievalService

router = APIRouter(
    prefix="/retrieval",
    tags=["retrieval"],
)


@router.post(
    "/{workspace_id}",
    response_model=RetrievalResponse,
)
async def retrieve(
    workspace_id: UUID,
    payload: RetrievalRequest,
    db: AsyncSession,
):
    if payload.strategy == StrategyName.DENSE:
        results = await RetrievalService.dense_search(
            db=db,
            workspace_id=str(workspace_id),
            query=payload.query,
            limit=payload.limit,
        )

    elif payload.strategy == StrategyName.BM25:
        results = await RetrievalService.bm25_search(
            db=db,
            workspace_id=str(workspace_id),
            query=payload.query,
            limit=payload.limit,
        )

    elif payload.strategy == StrategyName.HYBRID:
        results = await RetrievalService.hybrid_search(
            db=db,
            workspace_id=str(workspace_id),
            query=payload.query,
            limit=payload.limit,
        )

    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid strategy",
        )

    return RetrievalResponse(results=results)
