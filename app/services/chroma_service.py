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
                host="localhost",
                port=8002,
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
        collection = self.get_collection(workspace_id)

        ids = [c["id"] for c in chunks]
        documents = [c["document"] for c in chunks]
        embeddings = [c["embedding"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]

        await anyio.to_thread.run_sync(
            lambda: collection.add(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
            )
        )

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
