from arq import create_pool
from arq.connections import RedisSettings

redis = None


async def get_redis():
    global redis

    if redis is None:
        redis = await create_pool(
            RedisSettings(
                host="localhost",
                port=6379,
            )
        )

    return redis
