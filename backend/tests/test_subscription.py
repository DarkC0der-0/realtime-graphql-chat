import pytest
import asyncio
from httpx import AsyncClient
from fastapi import WebSocket
from app.main import app
from unittest.mock import patch
from app.utils.redis_pubsub import redis

@pytest.fixture(scope="module")
async def client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_subscription(client):
    async def mock_subscribe(channel):
        class MockPubSub:
            async def get_message(self, ignore_subscribe_messages=True):
                await asyncio.sleep(0.1)
                return {"data": "New message in room"}

        return MockPubSub()

    with patch("app.utils.redis_pubsub.subscribe", new=mock_subscribe):
        async with client.websocket_connect("/subscriptions/1") as websocket:
            data = await websocket.receive_json()
            assert data == "New message in room"