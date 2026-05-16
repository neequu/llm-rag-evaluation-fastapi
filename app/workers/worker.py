from arq.connections import RedisSettings

from app.workers.ingestion import ingest_document


class WorkerSettings:
    functions = [ingest_document]

    redis_settings = RedisSettings(
        host="localhost",
        port=6379,
    )
