import logging
from fastapi import APIRouter, HTTPException
from app.services.boundary_service import fetch_india_boundary

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/map-init")
def get_map_init():
    """
    Single endpoint for frontend map initialization.
    Returns tile URL template + India boundary together.
    """
    try:
        boundary = fetch_india_boundary()
        if boundary is None:
            raise HTTPException(status_code=404, detail="Boundary not found")
        return {
            "tile_url_template": "/api/tiles/{z}/{x}/{y}.png",
            "boundary": boundary,
        }
    except HTTPException:
        raise
    except Exception:
        logger.exception("Unexpected error in get_map_init")
        raise HTTPException(status_code=500, detail="Internal server error")