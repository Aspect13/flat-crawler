from fastapi import APIRouter

api_router = APIRouter(
    prefix="/api",
    tags=["api"],
    redirect_slashes=True
)
from api import flats
