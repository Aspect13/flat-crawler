from datetime import datetime, timedelta, UTC
from typing import List

from fastapi import Depends
from sqlalchemy import func, asc, select
from sqlmodel import Session

from api.pd import FlatList, UpdateFlatsRequest
from api.routes import api_router
from api.utils import get_session
from constants import TbilisiDistricts
from main import dump_flats_from_provider
from models import Flat, UpdateLog
from providers.abstract import DataProviderFactory


@api_router.get('/providers/')
async def get_available_providers():
    """Get list of available data providers"""
    return {"providers": DataProviderFactory.get_available_providers()}


@api_router.get('/flats/', response_model=List[FlatList])
async def read_items(skip: int = 0, limit: int = None, db: Session = Depends(get_session)):
    q = select(Flat).offset(skip).limit(limit).order_by(Flat.id.desc())
    # Use scalars() to extract model objects directly
    items = db.exec(q).scalars().all()
    return items


@api_router.post('/flats/')
async def update_flats(request: UpdateFlatsRequest, s: Session = Depends(get_session)):
    # todo: finish this api

    # Check rate limits per source
    limits = s.exec(
        select(
            UpdateLog.data_provider,
            func.max(UpdateLog.updated_at)
        ).filter(
            # UpdateLog.data_provider in DataProviderFactory.get_available_providers(),  # Filter by source
            UpdateLog.data_provider == request.provider_name,
            UpdateLog.updated_at > (datetime.now(UTC) - timedelta(hours=1))
        ).order_by(
            asc(UpdateLog.updated_at)
        ).group_by(
            UpdateLog.data_provider
        )
    ).all()

    limits = set(i[0] for i in limits)
    tasks = [i for i in TbilisiDistricts if i not in limits]
    resp = {i: None for i in TbilisiDistricts if i in limits}
    resp['limits'] = list(limits)

    # Process each district
    for district in tasks:
        resp[district] = await dump_flats_from_provider(request.provider_name, district, 100)

    return resp
