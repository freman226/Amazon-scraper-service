# app/api/routers/health.py
from fastapi import APIRouter
from datetime import datetime, timezone
from app.core.config import SERVICE_NAME, VERSION

router = APIRouter(tags=["health"])

STARTED_AT = datetime.now(timezone.utc)

@router.get("/health")
def health():
    now = datetime.now(timezone.utc)
    uptime = (now - STARTED_AT).total_seconds()
    return {"status": "ok", "service": SERVICE_NAME, "version": VERSION, "uptime_seconds": int(uptime)}

