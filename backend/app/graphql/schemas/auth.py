import graphene
from datetime import datetime, timedelta
from jose import jwt
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User as UserModel
from app.schemas.user import User as UserSchema
from app.core.config import settings
from app.utils.security import verify_password
from app.db.session import SessionLocal

class AuthLogin(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    access_token = graphene.String()
    user = graphene.Field(lambda: UserSchema)

    def mutate(self, info, email: str, password: str):
        session = SessionLocal()
        try:
            user = session.query(UserModel).filter(UserModel.email == email).first()
            if not user or not verify_password(password, user.password_hash):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password",
                )

            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": user.email}, expires_delta=access_token_expires
            )
            return AuthLogin(access_token=access_token, user=user)
        finally:
            session.close()

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

class Mutation(graphene.ObjectType):
    auth_login = AuthLogin.Field()