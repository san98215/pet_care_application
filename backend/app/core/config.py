from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # set fallback attributes for local testing
    database_url: str = "postgresql+asyncpg://tend:tend@localhost:5432/tend"
    secret_key: str = "change-me-to-a-random-secret"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 10080
    cors_origins: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
