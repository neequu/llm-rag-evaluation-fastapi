from dataclasses import dataclass

from pydantic import BaseModel

from .retrieval import StrategyName


class RAGRequest(BaseModel):
    query: str
    strategy: StrategyName = StrategyName.DENSE
    limit: int = 5


@dataclass
class ChunkContext:
    chunk_id: str
    document_id: str
    content: str


class RAGResponse(BaseModel):
    answer: str
    retrieved_chunks: list[ChunkContext]
    retrieval_strategy: str
    generation_latency_ms: float
    retrieval_latency_ms: float
    total_latency_ms: float
