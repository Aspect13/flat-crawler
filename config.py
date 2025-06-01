import logging
from pathlib import Path

from pydantic import Field, ConfigDict
from pydantic_settings import BaseSettings
from sqlalchemy import create_engine


class Settings(BaseSettings):
    model_config = ConfigDict(
        extra='ignore',
        env_file=Path(__file__).parent.joinpath('.env'),
        env_file_encoding='utf-8'
    )
    db_connection_string: str

    provider_settings: dict[str, BaseSettings] = Field(default_factory=dict)

    def register_provider(self, provider_name: str, provider_settings: BaseSettings) -> None:
        if provider_name in self.provider_settings:
            logging.warning(f'Provider {provider_name} already registered')
        self.provider_settings[provider_name] = provider_settings


settings = Settings()
engine = create_engine(settings.db_connection_string)
