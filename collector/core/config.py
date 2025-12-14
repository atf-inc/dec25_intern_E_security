# collector/app/core/config.py

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # REDIS_HOST: str = "redis"     # Use "redis" when running via docker-compose (service name resolves via Docker network)
    REDIS_HOST: str = "host.docker.internal"      #for running containers manually with `docker run`
    REDIS_PORT: int = 6379

    RATE_LIMIT_REQUESTS: int = 50       # allow 50 logs
    RATE_LIMIT_WINDOW: int = 10         # per 10 seconds

    class Config:
        env_file = ".env"


settings = Settings()
