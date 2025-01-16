from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: Optional[str] = 'sqlite+aiosqlite:///./discord_bot.db'
    token: Optional[str] = None
    debug_server_id: Optional[int] = None
    application_channel_id: Optional[int] = None
    rcd_application_channel_id: Optional[int] = None

    class Config:
        env_file = '.env'


settings = Settings()
