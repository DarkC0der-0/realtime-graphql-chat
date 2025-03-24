import graphene
from graphene import ObjectType
from graphene_sqlalchemy import SQLAlchemyObjectType
from app.models.user import User as UserModel

class User(SQLAlchemyObjectType):
    class Meta:
        model = UserModel

class Query(ObjectType):
    all_users = graphene.List(User)

    async def resolve_all_users(self, info):
        query = User.get_query(info)
        return await query.all()

schema = graphene.Schema(query=Query)