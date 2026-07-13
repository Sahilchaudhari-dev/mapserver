import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
import httpx
from app.config import settings
logger = logging.getLogger(__name__)
router = APIRouter()

APACHE_TILE_URL = settings.tile_server_url
client = httpx.AsyncClient(
    timeout=60,
    limits=httpx.Limits(
        max_connections=200,
        max_keepalive_connections=100
    )
)


@router.get("/tiles/{z}/{x}/{y}.png")
async def get_tile(z: int, x: int, y: int):
    url = f"{APACHE_TILE_URL}/{z}/{x}/{y}.png"
    try:
        response = await client.get(url)
    except httpx.RequestError:
        logger.exception(f"Tile server unreachable for {z}/{x}/{y}")
        raise HTTPException(status_code=502, detail="Tile server unavailable")

    if response.status_code == 200:
        return Response(
            content=response.content,
            media_type="image/png",
            headers={"Cache-Control": "public, max-age=86400"}
        )
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Tile not found")

    logger.error(f"Unexpected tile server response {response.status_code} for {z}/{x}/{y}")
    raise HTTPException(status_code=502, detail="Tile server error")


async def close_tile_client():
    await client.aclose()