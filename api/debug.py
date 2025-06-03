import platform
import sys
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator, Field
from sqlmodel import Session, select, func

from config import engine
from models import Flat, UpdateLog

from api.pd import ProviderDetail
from api.routes import debug_router
from config import settings
from providers.abstract import DataProviderFactory


class ProviderDetailDebug(ProviderDetail):
    settings: BaseModel | dict

    @field_validator('settings')
    @classmethod
    def validate_settings(cls, v):
        return v.model_dump() if isinstance(v, BaseModel) else v


class SystemInfo(BaseModel):
    python_version: str
    os_platform: str
    memory_usage: Optional[float] | None = None
    timestamp: datetime = Field(default_factory=datetime.now)

class DatabaseStats(BaseModel):

    district_stats: dict[str, int]
    recent_updates: list[dict]

class DebugResponse(BaseModel):

    providers: list[ProviderDetailDebug]
    settings: BaseModel | dict
    system: SystemInfo
    database: DatabaseStats

    @field_validator('settings')
    @classmethod
    def validate_settings(cls, v):
        return v.model_dump() if isinstance(v, BaseModel) else v


@debug_router.get('/', response_model=DebugResponse)
async def get_app_state():
    resp = dict()
    resp['providers'] = [
        DataProviderFactory.get_provider(i)
        for i in DataProviderFactory.get_available_providers()
    ]
    resp['settings'] = settings

    resp['system'] = SystemInfo(
        python_version=sys.version,
        os_platform=platform.platform(),
    )
    try:
        import psutil
        resp['system'].memory_usage = psutil.Process().memory_info().rss / 1024 / 1024
    except ImportError:
        ...
    
    with Session(engine) as session:
        district_counts = session.exec(
            select(Flat.district, func.count()).group_by(Flat.district)
        ).all()
        recent_updates = session.exec(
            select(UpdateLog).order_by(UpdateLog.updated_at.desc()).limit(5)
        ).all()

        resp['database'] = DatabaseStats(
            district_stats={district: count for district, count in district_counts},
            recent_updates=[{
                'city': log.city,
                'district': log.district,
                'number_of_flats': log.number_of_flats,
                'data_provider': log.data_provider,
                'updated_at': log.updated_at,
            } for log in recent_updates]
        )

    return resp
