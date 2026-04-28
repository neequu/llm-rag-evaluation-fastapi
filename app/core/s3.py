from contextlib import asynccontextmanager

import aioboto3

from app.core.config import settings


class S3Client:
    def __init__(self):
        self.session = aioboto3.Session()
        self.endpoint_url = f"{'https' if settings.MINIO_USE_SSL else 'http'}://{settings.MINIO_ENDPOINT}"

    @asynccontextmanager
    async def get_client(self):
        async with self.session.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=settings.MINIO_ACCESS_KEY,
            aws_secret_access_key=settings.MINIO_SECRET_KEY,
        ) as client:
            yield client


s3_client = S3Client()
