from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./task_manager.db"

    jwt_secret_key: str = "Khuzaima_secret_key"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 60 * 24 * 7  

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()