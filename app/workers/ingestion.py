from uuid import UUID

from app.core.s3 import s3_client
from app.crud.chunking import chunk_text
from app.crud.documents import DocumentService
from app.db.db import AsyncSessionLocal
from app.models.document import DocumentState


async def ingest_document(ctx, document_id: UUID, workspace_id: UUID, owner_id: UUID):
    print("HELLO")
    async with AsyncSessionLocal() as db:
        try:
            await DocumentService.update_status(
                db=db,
                document_id=document_id,
                status=DocumentState.PROCESSING,
            )
            print("HELLO", document_id)

            document = await DocumentService.get_document(
                db=db,
                document_id=document_id,
                owner_id=owner_id,
                workspace_id=workspace_id,
            )

            file_bytes = await s3_client.download_file(document.s3_key)

            text = file_bytes.decode("utf-8")
            chunks = chunk_text(text)
            print(f"Created {len(chunks)} chunks")

            print("Markdown loaded:", len(text))

            await DocumentService.update_status(
                db=db,
                document_id=document_id,
                status=DocumentState.COMPLETED,
            )

        except Exception as e:
            await DocumentService.update_status(
                db=db,
                document_id=document_id,
                status=DocumentState.FAILED,
                error_message=str(e),
            )
