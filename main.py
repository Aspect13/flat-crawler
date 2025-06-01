from typing import Optional

from sqlmodel import Session

from config import engine
from constants import TbilisiDistricts
from models import UpdateLog
from providers.abstract import DataProvider, DataProviderFactory


class FlatService:
    def __init__(self, data_provider: DataProvider):
        self.data_provider = data_provider

    async def dump_flats(self, district: str | TbilisiDistricts, limit: Optional[int] = 100) -> int:
        n = 0
        with Session(engine) as session:
            async for flat in self.data_provider.get_messages(session=session, district=district, limit=limit):
                session.add(flat)
                n += 1

            update_log = UpdateLog(
                district=district,
                number_of_flats=n,
                data_provider=self.data_provider.provider_name  # Track source in logs too
            )
            session.add(update_log)
            session.commit()
        return n


async def dump_flats_from_provider(provider_name: str, district: str | TbilisiDistricts | None = None,
                                   limit: Optional[int] = 100) -> int:
    """Helper function to dump flats from a specific provider"""
    data_provider = DataProviderFactory.create_provider(provider_name)
    service: FlatService = FlatService(data_provider)

    try:
        await data_provider.initialize()
        return await service.dump_flats(district, limit)
    finally:
        await data_provider.cleanup()
