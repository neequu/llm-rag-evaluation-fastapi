from uuid import UUID

from app.core.s3 import s3_client
from app.crud.documents import DocumentService
from app.db.db import AsyncSessionLocal
from app.models.document import DocumentState


async def ingest_document(ctx, document_id: str):
    async with AsyncSessionLocal() as db:
        try:
            await DocumentService.update_status(
                db=db,
                document_id=UUID(document_id),
                status=DocumentState.PROCESSING,
            )

            document = await DocumentService.get_by_id(
                db=db,
                document_id=UUID(document_id),
            )

            file_bytes = await s3_client.download_file(document.s3_key)

            print(f"Downloaded {len(file_bytes)} bytes")

            await DocumentService.update_status(
                db=db,
                document_id=UUID(document_id),
                status=DocumentState.COMPLETED,
            )

        except Exception as e:
            await DocumentService.update_status(
                db=db,
                document_id=UUID(document_id),
                status=DocumentState.FAILED,
                error_message=str(e),
            )
