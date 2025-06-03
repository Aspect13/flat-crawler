from abc import ABC, abstractmethod
from typing import AsyncIterator, AsyncIterable
from typing import Dict, Type, List

from sqlmodel import Session

from models import Flat


class DataProvider(ABC):
    """Abstract base class for flat data providers"""

    @abstractmethod
    async def get_messages(self, session: Session, city: str = None, district: str = None, limit: int = None) -> \
    AsyncIterator[Flat] | AsyncIterable[Flat]:
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

    @property
    @abstractmethod
    def available_cities(self) -> set:
        """Supported cities"""
        pass

    @property
    @abstractmethod
    def available_districts(self) -> set:
        """Supported districts"""
        pass

    @abstractmethod
    async def check_rate_limit(self, session: Session, city: str, district: str, **kwargs) -> bool:
        """Check if rate limit is reached for a specific district"""
        pass


class DataProviderFactory:
    _providers: Dict[str, Type[DataProvider]] = {}

    @classmethod
    def register_provider(cls, name: str, provider_class: Type[DataProvider]):
        """Register a new data provider"""
        cls._providers[name] = provider_class

    @classmethod
    def get_provider(cls, provider_name: str) -> Type[DataProvider]:
        """Get a data provider class by name"""
        try:
            return cls._providers[provider_name]
        except KeyError:
            raise ValueError(f"Unknown data provider: {provider_name}")

    @classmethod
    def create_provider(cls, provider_name: str) -> DataProvider:
        """Create a data provider instance"""
        return cls.get_provider(provider_name)()

    @classmethod
    def get_available_providers(cls) -> List[str]:
        """Get list of available data providers"""
        return list(cls._providers.keys())
