from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel


class StrategyName(StrEnum):
    DENSE = "dense"
    HYBRID = "hybrid"
    BM25 = "bm25"


class RetrievalRequest(BaseModel):
    query: str
    strategy: StrategyName = StrategyName.DENSE
    limit: int = 5


class RetrievalResult(BaseModel):
    chunk_id: UUID
    document_id: UUID
    content: str
    score: float
    strategy: str


class RetrievalResponse(BaseModel):
    results: list[RetrievalResult]
