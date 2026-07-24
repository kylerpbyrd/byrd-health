from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./byrd_health.db"
    cors_origins: list[str] = ["*"]
    debug: bool = False

    model_config = {"env_prefix": "BYRD_", "extra": "ignore"}


settings = Settings()
