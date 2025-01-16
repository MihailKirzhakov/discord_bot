from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str | None = 'sqlite+aiosqlite:///./discord_bot.db'
    token: str | None = None
    debug_server_id: int | None = None

    class Config:
        env_file = '.env'


settings = Settings()
