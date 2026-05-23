from uuid import UUID

from app.core.s3 import s3_client
from app.crud.documents import DocumentService
from app.db.db import AsyncSessionLocal
from app.models.document import DocumentState
from app.models.document_chunk import DocumentChunk
from app.services.chroma_service import chroma_service
from app.services.chunking import chunk_text, count_tokens
from app.services.embedding_service import generate_embeddings
from app.services.markdown_cleaner import clean_markdown


async def ingest_document(ctx, document_id: UUID):
    async with AsyncSessionLocal() as db:
        try:
            await DocumentService.update_status(
                db=db,
                document_id=document_id,
                status=DocumentState.PROCESSING,
            )

            document = await DocumentService.get_by_id(
                db=db,
                document_id=document_id,
            )

            file_bytes = await s3_client.download_file(document.s3_key)
            text = file_bytes.decode("utf-8")

            cleaned = clean_markdown(text)
            chunks = chunk_text(cleaned)
            embeddings = generate_embeddings(chunks)

            db_chunks = []
            chroma_chunks = []
            total_tokens = 0

            for i, (chunk, embedding) in enumerate(
                zip(chunks, embeddings, strict=False)
            ):
                token_count = count_tokens(chunk)
                total_tokens += token_count
                chroma_id = f"{document.id}_{i}"

                db_chunks.append(
                    DocumentChunk(
                        document_id=document.id,
                        chunk_index=i,
                        content=chunk,
                        token_count=token_count,
                        chroma_id=chroma_id,
                    )
                )

                chroma_chunks.append(
                    {
                        "id": chroma_id,
                        "document": chunk,
                        "embedding": embedding,
                        "metadata": {
                            "document_id": str(document.id),
                            "workspace_id": str(document.workspace_id),
                            "chunk_index": i,
                        },
                    }
                )

            try:
                await chroma_service.add_chunks(
                    workspace_id=str(document.workspace_id),
                    chunks=chroma_chunks,
                )
            except Exception as chroma_error:
                print(f"ChromaDB error: {chroma_error}")
                await db.rollback()
                raise Exception(
                    f"ChromaDB ingestion failed: {chroma_error}"
                ) from chroma_error

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
            print(f"Ingestion failed: {e}")
            await DocumentService.update_status(
                db=db,
                document_id=document_id,
                status=DocumentState.FAILED,
                error_message=str(e),
            )
            await db.rollback()
