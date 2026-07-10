from fastapi import APIRouter, HTTPException
from app.services.boundary_service import fetch_india_boundary

router = APIRouter()

_boundary_cache = None


@router.get("/map-init")
def get_map_init():
    """
    Single endpoint for frontend map initialization.
    Returns tile URL template + India boundary together.
    """
    global _boundary_cache
    try:
        if _boundary_cache is None:
            _boundary_cache = fetch_india_boundary()
            if _boundary_cache is None:
                raise HTTPException(status_code=404, detail="Boundary not found")

        return {
            "tile_url_template": "/api/tiles/{z}/{x}/{y}.png",
            "boundary": _boundary_cache,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))