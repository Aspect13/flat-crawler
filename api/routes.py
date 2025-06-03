from fastapi import APIRouter

api_router = APIRouter(
    prefix="/api",
    tags=["api"],
    redirect_slashes=True
)
from api import flats

debug_router = APIRouter(
    prefix="/debug",
    tags=["debug"],
    redirect_slashes=True
)
from api import debug
