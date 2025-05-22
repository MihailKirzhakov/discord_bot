from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = 'sqlite+aiosqlite:///./discord_bot.db'
    token: str
    debug_server_id: int
    application_channel_id: int
    rcd_application_channel_id: int

    class Config:
        env_file = '.env'


settings = Settings()
