import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import asc, desc
from app.models.user import UserModel
from app.models.room import RoomModel
from app.models.message import MessageModel
from app.db.session import SessionLocal
from app.utils.redis_pubsub import publish, subscribe
from app.utils.cache import get_cache, set_cache, delete_cache
from datetime import datetime
import json

class User(SQLAlchemyObjectType):
    class Meta:
        model = UserModel
        interfaces = (relay.Node,)

class Room(SQLAlchemyObjectType):
    class Meta:
        model = RoomModel
        interfaces = (relay.Node,)

class Message(SQLAlchemyObjectType):
    class Meta:
        model = MessageModel
        interfaces = (relay.Node,)

class MessageEdge(graphene.ObjectType):
    cursor = graphene.String()
    node = graphene.Field(Message)

class PageInfo(graphene.ObjectType):
    end_cursor = graphene.String()
    has_next_page = graphene.Boolean()

class MessageConnection(graphene.ObjectType):
    edges = graphene.List(MessageEdge)
    page_info = graphene.Field(PageInfo)

class Query(graphene.ObjectType):
    node = relay.Node.Field()
    all_users = graphene.List(User)
    all_rooms = graphene.List(Room)
    messages_by_room = graphene.Field(
        MessageConnection,
        room_id=graphene.Int(required=True),
        first=graphene.Int(),
        after=graphene.String()
    )

    async def resolve_all_users(self, info):
        cache_key = "all_users"
        cached_users = await get_cache(cache_key)
        if cached_users:
            return [UserModel(**json.loads(user)) for user in json.loads(cached_users)]

        session = SessionLocal()
        try:
            users = session.query(UserModel).all()
            await set_cache(cache_key, json.dumps([user.to_dict() for user in users]))
            return users
        except Exception as e:
            raise Exception(f"Error fetching users: {str(e)}")
        finally:
            session.close()

    async def resolve_all_rooms(self, info):
        cache_key = "all_rooms"
        cached_rooms = await get_cache(cache_key)
        if cached_rooms:
            return [RoomModel(**json.loads(room)) for room in json.loads(cached_rooms)]

        session = SessionLocal()
        try:
            rooms = session.query(RoomModel).all()
            await set_cache(cache_key, json.dumps([room.to_dict() for room in rooms]))
            return rooms
        except Exception as e:
            raise Exception(f"Error fetching rooms: {str(e)}")
        finally:
            session.close()

    async def resolve_messages_by_room(self, info, room_id, first=None, after=None):
        cache_key = f"messages_by_room_{room_id}_{first}_{after}"
        cached_messages = await get_cache(cache_key)
        if cached_messages:
            messages_data = json.loads(cached_messages)
            edges = [MessageEdge(cursor=message["cursor"], node=MessageModel(**message["node"])) for message in messages_data["edges"]]
            page_info = PageInfo(**messages_data["page_info"])
            return MessageConnection(edges=edges, page_info=page_info)

        session = SessionLocal()
        try:
            query = session.query(MessageModel).filter(MessageModel.room_id == room_id).order_by(asc(MessageModel.timestamp))
            if after:
                after_timestamp = datetime.strptime(after, "%Y-%m-%dT%H:%M:%S")
                query = query.filter(MessageModel.timestamp > after_timestamp)
            if first:
                query = query.limit(first)
            
            messages = query.all()
            edges = [
                MessageEdge(
                    cursor=message.timestamp.strftime("%Y-%m-%dT%H:%M:%S"),
                    node=message
                ) for message in messages
            ]
            end_cursor = edges[-1].cursor if edges else None
            has_next_page = len(messages) == first
            
            connection_data = {
                "edges": [{"cursor": edge.cursor, "node": edge.node.to_dict()} for edge in edges],
                "page_info": {"end_cursor": end_cursor, "has_next_page": has_next_page}
            }
            await set_cache(cache_key, json.dumps(connection_data))
            
            return MessageConnection(edges=edges, page_info=PageInfo(end_cursor=end_cursor, has_next_page=has_next_page))
        except NoResultFound:
            return MessageConnection(edges=[], page_info=PageInfo(end_cursor=None, has_next_page=False))
        except Exception as e:
            raise Exception(f"Error fetching messages for room {room_id}: {str(e)}")
        finally:
            session.close()

class CreateUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)

    user = graphene.Field(lambda: User)

    async def mutate(self, info, username):
        session = SessionLocal()
        try:
            if session.query(UserModel).filter(UserModel.username == username).first():
                raise Exception("Username already exists")
            user = UserModel(username=username)
            session.add(user)
            session.commit()
            await delete_cache("all_users")  # Invalidate cache
            return CreateUser(user=user)
        except Exception as e:
            session.rollback()
            raise Exception(f"Error creating user: {str(e)}")
        finally:
            session.close()

class CreateMessage(graphene.Mutation):
    class Arguments:
        content = graphene.String(required=True)
        user_id = graphene.Int(required=True)
        room_id = graphene.Int(required=True)

    message = graphene.Field(lambda: Message)

    async def mutate(self, info, content, user_id, room_id):
        session = SessionLocal()
        try:
            user = session.query(UserModel).filter(UserModel.id == user_id).first()
            if not user:
                raise Exception("Invalid user ID")
            room = session.query(RoomModel).filter(RoomModel.id == room_id).first()
            if not room:
                raise Exception("Invalid room ID")
            message = MessageModel(content=content, user_id=user_id, room_id=room_id)
            session.add(message)
            session.commit()
            await delete_cache(f"messages_by_room_{room_id}_*")  # Invalidate cache
            publish("room_{}".format(room_id), content)
            return CreateMessage(message=message)
        except Exception as e:
            session.rollback()
            raise Exception(f"Error creating message: {str(e)}")
        finally:
            session.close()

class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    create_message = CreateMessage.Field()

class Subscription(graphene.ObjectType):
    message_created = graphene.String(room_id=graphene.Int())

    async def resolve_message_created(self, info, room_id):
        pubsub = await subscribe("room_{}".format(room_id))
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True)
            if message:
                yield message["data"]

schema = graphene.Schema(query=Query, mutation=Mutation, subscription=Subscription)