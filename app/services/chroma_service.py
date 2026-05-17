import anyio
import chromadb

from app.core.config import settings


class ChromaService:
    def __init__(self):
        self._client = None

    @property
    def client(self):
        if self._client is None:
            self._client = chromadb.HttpClient(
                host=settings.CHROMA_HOST,
                port=settings.CHROMA_PORT,
            )
        return self._client

    def get_collection(self, workspace_id: str):
        collection_name = f"workspace_{workspace_id}"
        return self.client.get_or_create_collection(
            name=collection_name,
            metadata={
                "hnsw:space": "cosine",
            },
        )

    async def add_chunks(
        self,
        workspace_id: str,
        chunks: list[dict],
    ):
        if not chunks:
            print("No chunks to add, returning early")
            return

        collection = self.get_collection(workspace_id)

        def get_count():
            return collection.count()

        ids = [c["id"] for c in chunks]
        documents = [c["document"] for c in chunks]
        embeddings = [c["embedding"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]

        try:

            def add_to_chroma():
                collection.add(
                    ids=ids,
                    documents=documents,
                    embeddings=embeddings,
                    metadatas=metadatas,
                )
                return collection.count()

            after_count = await anyio.to_thread.run_sync(add_to_chroma)

            print(f"After add - collection has {after_count} chunks")
            print(f"Expected to add {len(chunks)}")

            def check_chunk_exists(chunk_id):
                try:
                    result = collection.get(ids=[chunk_id])
                    return len(result["ids"]) > 0
                except Exception:
                    return False

            first_id = ids[0]
            exists = await anyio.to_thread.run_sync(
                lambda: check_chunk_exists(first_id)
            )
            print(f"First chunk '{first_id}' exists in ChromaDB: {exists}")

        except Exception as e:
            print(f"ChromaDB add failed: {type(e).__name__}: {e}")
            import traceback

            traceback.print_exc()
            raise

    async def query(
        self,
        workspace_id: str,
        embedding: list[float],
        limit: int = 5,
    ):
        collection = self.get_collection(workspace_id)

        result = await anyio.to_thread.run_sync(
            lambda: collection.query(
                query_embeddings=[embedding],
                n_results=limit,
            )
        )

        return result


chroma_service = ChromaService()
