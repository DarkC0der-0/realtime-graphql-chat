import os
from app.core.config import Settings

class TestSettings(Settings):
    DATABASE_URL = "sqlite:///./test.db"
    REDIS_URL = "redis://localhost:6379/1"
    JWT_SECRET_KEY = "test_secret"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

os.environ["DATABASE_URL"] = TestSettings().DATABASE_URL
os.environ["REDIS_URL"] = TestSettings().REDIS_URL
os.environ["JWT_SECRET_KEY"] = TestSettings().JWT_SECRET_KEY