import aioredis
from app.core.config import settings

redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)

async def publish(channel: str, message: str):
    await redis.publish(channel, message)

async def subscribe(channel: str):
    pubsub = redis.pubsub()
    await pubsub.subscribe(channel)
    return pubsub