from fastapi import APIRouter

api_router = APIRouter(
    prefix="/api",
    tags=["api"]
)
from api import flats
