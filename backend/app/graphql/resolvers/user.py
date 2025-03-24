from app.models.user import User
from app.db.session import SessionLocal

async def get_user_by_id(user_id: int):
    async with SessionLocal() as session:
        result = await session.execute(select(User).filter_by(id=user_id))
        return result.scalars().first()