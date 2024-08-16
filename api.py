from datetime import timedelta, datetime, UTC
from http.client import NOT_FOUND, MOVED_PERMANENTLY
from typing import List

from fastapi import FastAPI, Depends, Request
from sqlalchemy import func
from sqlmodel import Session, select
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles

from config import settings
from constants import Districts
from db import engine, create_db_and_tables
from main import aget_client, get_channel, dump_flats
from models import Flat, UpdateLog, RequestLog
from pd import FlatList

app = FastAPI()
origins = [
    "http://localhost",
    "http://127.0.0.1",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency
def get_session():
    with Session(engine) as session:
        yield session


@app.on_event('startup')
def on_startup():
    create_db_and_tables()


@app.get('/api/flats/', response_model=List[FlatList])
async def read_items(skip: int = 0, limit: int = None, db: Session = Depends(get_session)):
    items = db.exec(select(Flat).offset(skip).limit(limit).order_by(Flat.id.desc())).fetchall()
    return items


@app.post('/api/flats/')
async def update_flats(districts: List[Districts],
                       s: Session = Depends(get_session),
                       client: 'TelegramClient' = Depends(aget_client)
                       ):
    limits = s.exec(
        select(
            UpdateLog.district, func.max(UpdateLog.updated_at)
        ).filter(
            UpdateLog.district.in_(set(districts)),
            UpdateLog.updated_at > (datetime.now(UTC) - timedelta(hours=1))
        ).order_by(
            UpdateLog.updated_at.asc()
        ).group_by(
            UpdateLog.district
        )
    ).all()
    limits = set(i[0] for i in limits)
    print(f'{limits=}')
    tasks = [i for i in districts if i not in limits]
    resp = {i: None for i in districts if i in limits}
    print(f'{tasks=}')
    print(f'{resp=}')
    async with client:
        channel = await get_channel(client)
        for district in tasks:
            resp[district] = await dump_flats(client, channel, district, limit=settings.max_posts_per_task)
    return resp


@app.get('/')
async def redirect_to_index():
    return RedirectResponse('/index.html')


@app.get('/favicon.ico')
async def redirect_favicon():
    return RedirectResponse('/paws.ico', status_code=MOVED_PERMANENTLY)


@app.exception_handler(NOT_FOUND)
async def dump_mums_hackers(
        request: Request,
        exc: Exception
):
    log = RequestLog(
        client_ip=request.client.host,
        method=request.method,
        path=request.url.path,
        query_params=dict(request.query_params),
        user_agent=request.headers.get('user-agent')
    )

    with Session(engine) as s:
        s.add(log)
        s.commit()

    return RedirectResponse('https://youtu.be/dQw4w9WgXcQ')


app.mount('/', StaticFiles(directory='dist'), name='ui')
