from contextlib import asynccontextmanager
from http.client import NOT_FOUND, MOVED_PERMANENTLY

from fastapi import FastAPI, Request, Response
from sqlmodel import Session
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles

from api.routes import api_router
from config import engine
from models import RequestLog


@asynccontextmanager
async def lifespan(app: FastAPI):
    # better run alembic upgrade head

    yield


app = FastAPI(lifespan=lifespan)
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
app.include_router(api_router)


@app.get('/')
async def redirect_to_index():
    return RedirectResponse('/index.html')


@app.get('/favicon.ico')
async def redirect_favicon():
    return RedirectResponse('/paws.ico', status_code=MOVED_PERMANENTLY)


@app.exception_handler(NOT_FOUND)
async def dump_mums_hackers(
        request: Request,
        exc: Exception,
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

    return Response("oops: 404")

    return RedirectResponse('https://youtu.be/dQw4w9WgXcQ')


app.mount('/', StaticFiles(directory='dist', check_dir=False), name='ui')
