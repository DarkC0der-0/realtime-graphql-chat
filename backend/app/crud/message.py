from sqlalchemy.orm import Session
from app.models.message import Message
from app.schemas.message import MessageCreate

def get_message(db: Session, message_id: int):
    return db.query(Message).filter(Message.id == message_id).first()

def get_messages_by_room(db: Session, room_id: int):
    return db.query(Message).filter(Message.room_id == room_id).all()

def create_message(db: Session, message: MessageCreate):
    db_message = Message(content=message.content, sender_id=message.sender_id, room_id=message.room_id)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def delete_message(db: Session, message_id: int):
    db_message = db.query(Message).filter(Message.id == message_id).first()
    if db_message:
        db.delete(db_message)
        db.commit()
    return db_message