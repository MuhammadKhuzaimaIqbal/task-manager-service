from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./task_manager.db"

    # This tells Pydantic to look for a .env file to override defaults
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

# Create a global settings instance to use throughout the app
settings = Settings()