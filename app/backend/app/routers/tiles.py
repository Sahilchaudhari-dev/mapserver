from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
import httpx

router = APIRouter()

APACHE_TILE_URL = "http://localhost/osm_tiles"

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
        if response.status_code == 200:
            return Response(
                content=response.content,
                media_type="image/png",
                headers={"Cache-Control": "public, max-age=86400"}
            )
        raise HTTPException(status_code=404, detail="Tile not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))