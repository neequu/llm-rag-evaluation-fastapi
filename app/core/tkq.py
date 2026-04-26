import taskiq_fastapi
from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend

from app.core.config import settings

broker = ListQueueBroker(f"redis://redis:{settings.REDIS_PORT}/0")
result_backend = RedisAsyncResultBackend(f"redis://redis:{settings.REDIS_PORT}/0")
broker.with_result_backend(result_backend)

taskiq_fastapi.init(broker, "app.main:app")


@broker.task
async def process_document_rag(document_id: str):
    """
    This is where the RAG magic happens:
    1. Download from MinIO
    2. Chunk Text
    3. Generate Embeddings
    4. Save to pgvector
    """
    print(f"Starting AI processing for {document_id}...")

    # Optionally add MinIO client here
    from minio import Minio

    minio_client = Minio(
        f"{settings.MINIO_HOST}:{settings.MINIO_API_PORT}",
        access_key=settings.MINIO_ROOT_USER,
        secret_key=settings.MINIO_ROOT_PASSWORD,
        secure=settings.MINIO_SECURE,
    )

    # Download file from MinIO
    try:
        response = minio_client.get_object(
            settings.MINIO_BUCKET_NAME, f"documents/{document_id}.pdf"
        )
        file_content = response.read()
        response.close()
        response.release_conn()

        print(f"Successfully processed {document_id}")
        return {"status": "success", "document_id": document_id}
    except Exception as e:
        print(f"Error processing {document_id}: {e}")
        return {"status": "error", "error": str(e)}
