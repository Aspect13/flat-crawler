import logging
import re
from datetime import datetime, UTC, timedelta
from typing import Optional, AsyncIterator, Literal

from pydantic import ConfigDict
from pydantic_settings import BaseSettings
from sqlalchemy import func
from sqlmodel import Session, desc, select, asc
from telethon import TelegramClient
from telethon.tl.types import Channel, PeerChannel

from config import settings
from constants import TbilisiDistricts, Cities
from exceptions import RateLimitError
from models import Flat, UpdateLog
from providers.abstract import DataProvider, DataProviderFactory


class FlipFlatSettings(BaseSettings):
    model_config = ConfigDict(
        extra='ignore',
        env_prefix='flip_flat_',
        env_file=settings.model_config['env_file']
    )

    app_id: int
    api_hash: str
    channel_id: Optional[int]
    channel_name: Optional[str]
    max_posts_per_task: int = 100


settings.register_provider('flip_flat', FlipFlatSettings())

parser_regexp = {
    'district': re.compile(r".*#([^\s]*)"),
    'address': re.compile(r"\n(.*)\n\n"),
    'rooms': re.compile(r"Комнат.*(\d+)"),
    'area': re.compile(r"Площадь.* (\d+)"),
    'floors': re.compile(r"Этаж.* ((\d+)/?(\d*))"),
    'price': re.compile(r"Цена.* (\d+)\$"),
    'location': re.compile(r"Локация.*\((.*)\)"),
    'description': re.compile(r"__(.*)__", flags=re.MULTILINE | re.DOTALL)
}


class FlipFlatDataProvider(DataProvider):
    provider_name = 'flip_flat'
    available_districts: set = set(TbilisiDistricts)
    available_cities: set = {Cities.tbilisi}

    @property
    def settings(self) -> FlipFlatSettings:
        return settings.provider_settings[self.provider_name]

    def __init__(self):
        self.client: TelegramClient = TelegramClient('anon', self.settings.app_id, self.settings.api_hash)
        self.channel: Optional[Channel] = None

    async def initialize(self) -> None:
        await self.client.start()
        # await self.client.connect()
        self.channel = await self._get_channel()

    async def cleanup(self) -> None:
        await self.client.disconnect()

    async def _get_channel(self) -> Channel:
        if self.settings.channel_id:
            return await self.client.get_entity(PeerChannel(self.settings.channel_id))
        elif self.settings.channel_name:
            return await self.client.get_entity(f't.me/{self.settings.channel_name}')
        raise ValueError("No Telegram channel configured")

    async def check_rate_limit(self, session: Session, city: str, district: TbilisiDistricts, **kwargs) -> bool:
        rate_limit = session.exec(
            select(
                # UpdateLog.data_provider,
                # UpdateLog.city,
                # UpdateLog.district,
                func.max(UpdateLog.updated_at)
            ).filter(
                # UpdateLog.updated_at > (datetime.now(UTC) - timedelta(hours=1)),
                UpdateLog.data_provider == self.provider_name,
                UpdateLog.city == city,
                UpdateLog.district == district,
            ).order_by(
                asc(UpdateLog.updated_at)
            ).group_by(
                UpdateLog.data_provider,
                # UpdateLog.city,
                # UpdateLog.district
            )
        ).first()
        if rate_limit:
            logging.warning(f"Rate limit reached for {self.provider_name}/{city}/{district} ({rate_limit})")
            raise RateLimitError(f"Rate limit reached for {self.provider_name}/{city}/{district} ({rate_limit})")
        return True

    async def get_messages(self,
                           session: Session,
                           district: TbilisiDistricts,
                           city: Literal[Cities.tbilisi] = Cities.tbilisi.value,
                           limit: int = 100) -> AsyncIterator[Flat]:
        if not self.channel:
            raise RuntimeError("Data source not initialized")

        if city and city not in self.available_cities:
            raise ValueError(f"City {city} is not supported by this data provider")

        if district not in self.available_districts:
            raise ValueError(f"District {district} is not supported by this data provider")

        last_message_id = session.exec(
            select(Flat.provider_message_id).where(
                Flat.city == city,
                Flat.district == district,
                Flat.data_provider == self.provider_name
            ).order_by(
                desc(Flat.provider_message_id)
            )
        ).first()

        min_id = int(last_message_id) if last_message_id else 0

        async for message in self.client.iter_messages(
                self.channel,
                search=f'#{district}',
                min_id=min_id,
                limit=limit
        ):
            flat: Flat = self.parse_message(message.text)
            flat.city = Cities.tbilisi
            flat.data_provider = self.provider_name
            flat.provider_message_id = message.id
            flat.created_at = message.date
            flat.edit_date = message.edit_date
            flat.link_to_post = f'https://t.me/{self.channel.username}/{message.id}'
            flat.district = district.lower()
            flat.raw_text = message.text
            yield flat

    @staticmethod
    def parse_message(message_text: str, flat_object: Optional[Flat] = None) -> Flat:
        if flat_object is None:
            flat_object = Flat()
        flat_object.rooms = parser_regexp['rooms'].search(message_text).group(1)
        flat_object.area = parser_regexp['area'].search(message_text).group(1)
        floors = parser_regexp['floors'].search(message_text)
        flat_object.floor = floors.group(2)
        flat_object.floors = floors.group(3)
        flat_object.price = parser_regexp['price'].search(message_text).group(1)
        try:
            flat_object.location = parser_regexp['location'].search(message_text).group(1)
        except AttributeError:
            flat_object.location = ''
        try:
            flat_object.description = parser_regexp['description'].search(message_text).group(1)
        except AttributeError:
            flat_object.description = ''
        flat_object.address = parser_regexp['address'].search(message_text).group(1)

        if not flat_object.district:
            flat_object.district = parser_regexp['district'].search(message_text).group(1).lower()
        return flat_object


DataProviderFactory.register_provider(
    FlipFlatDataProvider.provider_name,
    FlipFlatDataProvider
)
