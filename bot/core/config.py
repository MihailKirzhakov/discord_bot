from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: Optional[str] = None
    token: Optional[str] = None
    debug_server_id: Optional[int] = None

    class Config:
        env_file = '.env'


settings = Settings()
