import pytest
from httpx import AsyncClient
from app.main import app
from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.models.user import User
from app.utils.security import get_password_hash

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
async def test_create_user(client, setup_db):
    query = """
    mutation {
        createUser(username: "testuser") {
            user {
                id
                username
            }
        }
    }
    """
    response = await client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    data = response.json()
    assert "errors" not in data
    assert data["data"]["createUser"]["user"]["username"] == "testuser"

@pytest.mark.asyncio
async def test_create_message(client, setup_db, test_user):
    query = """
    mutation {
        createMessage(content: "Hello, world!", userId: 1, roomId: 1) {
            message {
                id
                content
            }
        }
    }
    """
    response = await client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    data = response.json()
    assert "errors" not in data
    assert data["data"]["createMessage"]["message"]["content"] == "Hello, world!"