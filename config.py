from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_id: int
    api_hash: str
    db_connection_string: str
    tg_channel_id: Optional[int]
    tg_channel_name: Optional[str]
    max_posts_per_task: int = 100


settings = Settings(_env_file=Path(__file__).parent.joinpath('.env'), _env_file_encoding='utf-8')
