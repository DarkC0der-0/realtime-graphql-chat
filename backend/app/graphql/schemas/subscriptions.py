import graphene
from app.utils.redis_pubsub import subscribe

class Subscription(graphene.ObjectType):
    count = graphene.Int()

    @staticmethod
    async def resolve_count(root, info):
        pubsub = await subscribe("count_channel")
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True)
            if message:
                yield int(message["data"])

schema = graphene.Schema(subscription=Subscription)