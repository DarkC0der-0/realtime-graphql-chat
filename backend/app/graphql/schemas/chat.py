import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType
from sqlalchemy.orm.exc import NoResultFound
from app.models.user import UserModel
from app.models.room import RoomModel
from app.models.message import MessageModel
from app.db.session import SessionLocal
from app.utils.redis_pubsub import publish, subscribe
from datetime import datetime

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


class Query(graphene.ObjectType):
    node = relay.Node.Field()
    all_users = graphene.List(User)
    all_rooms = graphene.List(Room)
    messages_by_user = graphene.List(Message, user_id=graphene.Int())
    messages_by_room = graphene.List(Message, room_id=graphene.Int())

    def resolve_all_users(self, info):
        session = SessionLocal()
        try:
            return session.query(UserModel).all()
        except Exception as e:
            raise Exception(f"Error fetching users: {str(e)}")
        finally:
            session.close()

    def resolve_all_rooms(self, info):
        session = SessionLocal()
        try:
            return session.query(RoomModel).all()
        except Exception as e:
            raise Exception(f"Error fetching rooms: {str(e)}")
        finally:
            session.close()

    def resolve_messages_by_user(self, info, user_id):
        session = SessionLocal()
        try:
            return session.query(MessageModel).filter(MessageModel.user_id == user_id).all()
        except NoResultFound:
            return []
        except Exception as e:
            raise Exception(f"Error fetching messages for user {user_id}: {str(e)}")
        finally:
            session.close()

    def resolve_messages_by_room(self, info, room_id):
        session = SessionLocal()
        try:
            return session.query(MessageModel).filter(MessageModel.room_id == room_id).all()
        except NoResultFound:
            return []
        except Exception as e:
            raise Exception(f"Error fetching messages for room {room_id}: {str(e)}")
        finally:
            session.close()


class CreateUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)

    user = graphene.Field(lambda: User)

    def mutate(self, info, username):
        session = SessionLocal()
        try:
            if session.query(UserModel).filter(UserModel.username == username).first():
                raise Exception("Username already exists")
            user = UserModel(username=username)
            session.add(user)
            session.commit()
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

    def mutate(self, info, content, user_id, room_id):
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