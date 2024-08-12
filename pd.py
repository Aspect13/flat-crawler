from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from constants import Districts


class FlatList(BaseModel):
    id: int
    district: Districts | str
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


class FlatCreate(BaseModel):
    district: Districts | str
    address: Optional[str]
    rooms: Optional[int]
    area: Optional[int]
    floor: Optional[int]
    floors: Optional[int]
    price: Optional[int]
    location: Optional[str]
    link_to_post: Optional[str]
