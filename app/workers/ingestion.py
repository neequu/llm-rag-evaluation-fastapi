from uuid import UUID

from app.core.s3 import s3_client
from app.crud.chunking import chunk_text
from app.crud.documents import DocumentService
from app.db.db import AsyncSessionLocal
from app.models.document import DocumentState
from app.models.document_chunk import DocumentChunk


async def ingest_document(ctx, document_id: UUID, workspace_id: UUID, owner_id: UUID):
    async with AsyncSessionLocal() as db:
        try:
            await DocumentService.update_status(
                db=db,
                document_id=document_id,
                status=DocumentState.PROCESSING,
            )

            document = await DocumentService.get_document(
                db=db,
                document_id=document_id,
                owner_id=owner_id,
                workspace_id=workspace_id,
            )

            file_bytes = await s3_client.download_file(document.s3_key)

            text = file_bytes.decode("utf-8")

            chunks = chunk_text(text)

            total_tokens = 0
            db_chunks = []

            for i, chunk in enumerate(chunks):
                chunk_tokens = len(chunk.split())
                total_tokens += chunk_tokens

                db_chunks.append(
                    DocumentChunk(
                        document_id=document.id,
                        chunk_index=i,
                        content=chunk,
                        token_count=chunk_tokens,
                        chroma_id=None,
                    )
                )

            db.add_all(db_chunks)

            document.chunk_count = len(chunks)
            document.token_count = total_tokens

            await db.commit()

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
            await db.rollback()
