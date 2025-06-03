from fastapi import Depends
from sqlalchemy import select
from sqlmodel import Session

from api.pd import FlatList, UpdateFlatsRequest, ProviderDetail, UpdateFlatsResponse
from api.routes import api_router
from api.utils import get_session
from main import dump_flats_from_provider
from models import Flat
from providers.abstract import DataProviderFactory


@api_router.get('/providers/', response_model=list[ProviderDetail])
async def get_available_providers():
    """Get list of available data providers"""
    return [
        DataProviderFactory.get_provider(i)
        for i in DataProviderFactory.get_available_providers()
    ]


@api_router.get('/flats/', response_model=list[FlatList])
async def read_items(skip: int = 0, limit: int = None, db: Session = Depends(get_session)):
    q = select(Flat).offset(skip).limit(limit).order_by(Flat.id.desc())
    # Use scalars() to extract model objects directly
    items = db.exec(q).scalars().all()
    return items


@api_router.post('/flats/', response_model=UpdateFlatsResponse)
async def update_flats(request: UpdateFlatsRequest):
    if request.providers is None:
        request.providers = DataProviderFactory.get_available_providers()

    results = {}
    for provider in request.providers:
        provider_results = await dump_flats_from_provider(
            provider_name=provider,
            cities=request.cities,
            districts=request.districts,
        )
        results[provider] = provider_results

    return results
