from arq.connections import RedisSettings
from core.config import settings

from app.workers.ingestion import ingest_document


class WorkerSettings:
    functions = [ingest_document]

    redis_settings = RedisSettings(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
    )
