from uuid import UUID

from fastapi import APIRouter

from app.db.db import AsyncSession
from app.schemas.rag import (
    RAGRequest,
    RAGResponse,
)
from app.services.rag_service import RAGService

router = APIRouter(
    prefix="/rag",
    tags=["rag"],
)


@router.post(
    "/{workspace_id}",
    response_model=RAGResponse,
)
async def ask_question(
    workspace_id: UUID,
    payload: RAGRequest,
    db: AsyncSession,
):

    result = await RAGService.generate_answer(
        db=db,
        workspace_id=str(workspace_id),
        query=payload.query,
        strategy=payload.strategy,
        limit=payload.limit,
    )

    return RAGResponse(**result)
