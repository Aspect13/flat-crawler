import asyncio
from collections import defaultdict
from typing import Optional

from sqlmodel import Session

from config import engine
from exceptions import RateLimitError
from models import UpdateLog
from providers.abstract import DataProvider, DataProviderFactory


class FlatService:
    def __init__(self, data_provider: DataProvider):
        self.data_provider = data_provider

    async def dump_flats(self, city: str, district: str, limit: Optional[int] = 100, bulk_commit: bool = True) -> int:
        n = 0
        with Session(engine) as s:
            if await self.data_provider.check_rate_limit(
                    session=s, city=city, district=district
            ):
                async for flat in self.data_provider.get_messages(
                        session=s,
                        city=city,
                        district=district,
                        limit=limit
                ):
                    flat.data_provider = self.data_provider.provider_name
                    s.add(flat)
                    n += 1
                    if not bulk_commit:
                        s.commit()

                update_log = UpdateLog(
                    city=city,
                    district=district,
                    number_of_flats=n,
                    data_provider=self.data_provider.provider_name  # Track source in logs too
                )
                s.add(update_log)
                s.commit()
        return n


async def dump_flats_from_provider(provider_name: str,
                                   cities: list[str] | None = None,
                                   districts: list[str] | None = None,
                                   limit: Optional[int] = 100) -> dict[str, dict]:
    """Helper function to dump flats from a specific provider"""
    data_provider = DataProviderFactory.create_provider(provider_name)
    service: FlatService = FlatService(data_provider)

    if cities is None:
        cities = data_provider.available_cities
    else:
        cities = data_provider.available_cities.intersection(cities)

    if districts is None:
        districts = data_provider.available_districts
    else:
        districts = data_provider.available_districts.intersection(districts)

    try:
        await data_provider.initialize()

        async def dump_district(city: str, district: str) -> tuple[str, str, int, str | None]:
            try:
                count = await service.dump_flats(city=city, district=district, limit=limit)
            except (RateLimitError, ValueError) as e:
                return city, district, 0, str(e)
            return city, district, count, None

        results_list = await asyncio.gather(
            *[
                dump_district(city, district)
                for district in districts
                for city in cities
            ]
        )
        result_dict = defaultdict(dict)
        for city, district, new_entries, error in results_list:
            result_dict[city][district] = {
                'new_entries': new_entries,
                'error': error,
            }
        return result_dict

    finally:
        await data_provider.cleanup()
