from pydantic import BaseModel
from datetime import datetime

class MessageBase(BaseModel):
    content: str

class MessageCreate(MessageBase):
    sender_id: int
    room_id: int

class Message(MessageBase):
    id: int
    timestamp: datetime
    sender_id: int
    room_id: int

    class Config:
        orm_mode = True