from fastapi import APIRouter, HTTPException
from app.database import test_connection

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.get("/db-check")
def db_check():
    result = test_connection()
    if "error" in result:
        raise HTTPException(
            status_code=500,
            detail=result["error"]
        )
    return result