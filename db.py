from sqlalchemy import create_engine
from sqlmodel import SQLModel

from config import settings

engine = create_engine(settings.db_connection_string)


def create_db_and_tables():
    from models import Flat, UpdateLog, RequestLog
    SQLModel.metadata.create_all(engine)
