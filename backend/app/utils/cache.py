from app.utils.redis_client import redis
from app.utils.logger import log_event

async def get_cache(key: str):
    value = await redis.get(key)
    if value:
        log_event(f"Cache hit for key: {key}")
    else:
        log_event(f"Cache miss for key: {key}")
    return value

async def set_cache(key: str, value: str, expire: int = 3600):
    await redis.set(key, value, ex=expire)
    log_event(f"Cache set for key: {key}")

async def delete_cache(key: str):
    await redis.delete(key)
    log_event(f"Cache deleted for key: {key}")