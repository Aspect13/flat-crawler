from abc import ABC, abstractmethod
from typing import AsyncIterator
from typing import Dict, Type, List

from sqlmodel import Session

from constants import TbilisiDistricts
from models import Flat


class DataProvider(ABC):
    """Abstract base class for flat data providers"""

    @abstractmethod
    async def get_messages(self, session: Session, district: str | TbilisiDistricts | None = None, limit: int = None) -> \
    AsyncIterator[Flat]:
        """Fetch messages for a specific district"""
        pass

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the data provider (connect, authenticate, etc.)"""
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup resources"""
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the data provider"""
        pass


class DataProviderFactory:
    _providers: Dict[str, Type[DataProvider]] = {}

    @classmethod
    def register_provider(cls, name: str, provider_class: Type[DataProvider]):
        """Register a new data provider"""
        cls._providers[name] = provider_class

    @classmethod
    def create_provider(cls, provider_name: str) -> DataProvider:
        """Create a data provider instance"""
        if provider_name not in cls._providers:
            raise ValueError(f"Unknown data provider: {provider_name}")
        return cls._providers[provider_name]()

    @classmethod
    def get_available_providers(cls) -> List[str]:
        """Get list of available data providers"""
        return list(cls._providers.keys())
