import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routers import health, boundaries, tiles, map_init
from app.database import connection_pool
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.gzip import GZipMiddleware

app = FastAPI()
app.add_middleware(GZipMiddleware, minimum_size=1000)
class ForceHTTPSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request.scope["scheme"] = "https"
        response = await call_next(request)
        return response

app.add_middleware(ForceHTTPSMiddleware)
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("App starting — connection pool ready")
    yield
    connection_pool.closeall()
    print("App shutting down — connections closed")

app = FastAPI(title="Geo Module API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(boundaries.router, prefix="/api", tags=["boundaries"])
app.include_router(tiles.router, prefix="/api", tags=["tiles"])
app.include_router(map_init.router, prefix="/api", tags=["map_init"])

static_path = os.path.join(os.path.dirname(__file__), "static")
app.mount("/", StaticFiles(directory=static_path, html=True), name="static")