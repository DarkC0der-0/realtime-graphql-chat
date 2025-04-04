from pydantic import BaseModel

class UserBase(BaseModel):
    name: str
    email: str

class UserCreate(UserBase):
    password_hash: str

class UserUpdate(UserBase):
    password_hash: str

class User(UserBase):
    id: int

    class Config:
        orm_mode = True