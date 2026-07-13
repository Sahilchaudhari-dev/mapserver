import logging
from fastapi import APIRouter, HTTPException
from app.database import test_connection

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health")
def health_check():
    return {"status": "ok"}


@router.get("/db-check")
def db_check():
    result = test_connection()
    if "error" in result:
        logger.error(f"Database health check failed: {result['error']}")
        raise HTTPException(status_code=503, detail="Database unavailable")
    return result