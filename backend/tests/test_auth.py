import pytest
from httpx import AsyncClient
from app.main import app
from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.models.user import User
from app.utils.security import get_password_hash, verify_password
from app.core.config import settings
from jose import jwt

@pytest.fixture(scope="module")
async def client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture(scope="module")
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def test_user():
    session = SessionLocal()
    user = User(name="testuser", email="test@example.com", password_hash=get_password_hash("password"))
    session.add(user)
    session.commit()
    session.refresh(user)
    session.close()
    return user

@pytest.mark.asyncio
async def test_login(client, setup_db, test_user):
    query = """
    mutation {
        authLogin(email: "test@example.com", password: "password") {
            accessToken
            user {
                id
                name
            }
        }
    }
    """
    response = await client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    data = response.json()
    assert "errors" not in data
    token = data["data"]["authLogin"]["accessToken"]
    decoded_token = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    assert decoded_token["sub"] == "test@example.com"
    assert verify_password("password", test_user.password_hash)