import httpx

from app.core.config import settings


class OllamaService:
    async def generate(
        self,
        prompt: str,
    ) -> str:
        try:
            async with httpx.AsyncClient(timeout=600) as client:
                response = await client.post(
                    f"{settings.OLLAMA_URL}/api/generate",
                    json={
                        "model": settings.OLLAMA_MODEL,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "num_predict": 256,
                            "temperature": 0.1,
                        },
                    },
                )

            response.raise_for_status()
            data = response.json()
            return data["response"]

        except httpx.TimeoutException:
            raise TimeoutError(
                f"Ollama generation timed out after 600 seconds for model {settings.OLLAMA_MODEL}"
            )


ollama_service = OllamaService()
