from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base import Base

class Room(Base):
    __tablename__ = 'rooms'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    messages = relationship("Message", back_populates="room")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }