from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator

from constants import TbilisiDistricts


class FlatList(BaseModel):
    id: int
    city: str
    district: str | TbilisiDistricts
    address: Optional[str]
    rooms: Optional[int]
    area: Optional[int]
    floor: Optional[int]
    floors: Optional[int]
    price: Optional[int]
    location: Optional[str]
    link_to_post: Optional[str]
    created_at: datetime
    added_to_db: datetime
    data_provider: str

    @field_validator('city')
    @classmethod
    def capitalize_city(cls, v: str) -> str:
        return v.capitalize()

    @field_validator('district')
    @classmethod
    def lowercase_district(cls, v):
        return v.lower() if isinstance(v, str) else v

    @field_validator('floor', 'floors', mode='before')
    @classmethod
    def fix_floors(cls, v: int | str | None) -> Optional[int]:
        if v:
            return int(v)
        return None


class UpdateFlatsRequest(BaseModel):
    provider_name: str
    district: Optional[str | TbilisiDistricts] = None