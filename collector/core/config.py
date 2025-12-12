# collector/app/core/config.py

from pydantic import BaseSettings


class Settings(BaseSettings):
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379

    RATE_LIMIT_REQUESTS: int = 50       # allow 50 logs
    RATE_LIMIT_WINDOW: int = 10         # per 10 seconds

    class Config:
        env_file = ".env"


settings = Settings()
