from arq import create_pool
from arq.connections import RedisSettings

from app.core.config import settings

redis = None


async def get_redis():
    global redis

    if redis is None:
        redis = await create_pool(
            RedisSettings(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
            )
        )

    return redis
