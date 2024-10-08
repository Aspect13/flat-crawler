from datetime import datetime, UTC
from typing import Optional

from pydantic import field_validator
from sqlalchemy import JSON
from sqlmodel import Field, SQLModel


class Flat(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    ff_id: int = Field(unique=True, index=True)
    district: str
    address: str
    rooms: Optional[int] = None
    area: Optional[int] = None
    floor: Optional[int] = None
    floors: Optional[int] = None
    price: Optional[int] = None
    description: Optional[str] = None
    location: Optional[str] = None
    original_text: Optional[str] = None
    link_to_post: str
    created_at: datetime
    edit_date: Optional[datetime] = None
    added_to_db: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator('district', mode='before')
    @classmethod
    def lowercase_district(cls, v):
        return v.lower() if isinstance(v, str) else v


class UpdateLog(SQLModel, table=True):
    __tablename__ = 'update_log'
    id: Optional[int] = Field(default=None, primary_key=True)
    district: str
    number_of_flats: int
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class RequestLog(SQLModel, table=True):
    __tablename__ = 'request_log'
    id: Optional[int] = Field(default=None, primary_key=True)
    client_ip: str
    method: str
    path: str
    query_params: Optional[dict] = Field(default_factory=dict, sa_type=JSON)
    user_agent: Optional[str] = None
    confirmed_piece_of_shit: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))