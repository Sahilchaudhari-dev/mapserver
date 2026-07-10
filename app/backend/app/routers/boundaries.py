from fastapi import APIRouter, HTTPException
from app.services.boundary_service import fetch_india_boundary

router = APIRouter()

@router.get("/boundaries/india")
def get_india_boundary():
    try:
        result = fetch_india_boundary()
        if result is None:
            raise HTTPException(status_code=404, detail="Boundary not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))