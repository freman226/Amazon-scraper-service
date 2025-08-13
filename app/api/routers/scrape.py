# app/api/routers/scrape.py
from fastapi import APIRouter, Depends
from app.schemas.scrape import ScrapeRequest
from app.services.scraper import scrape_amazon
from app.services.purify import normalize_children_text
from app.core.config import DATA_FILE
from app.core.auth import require_verified_user
import json

router = APIRouter(
    prefix="/scrape",
    tags=["scrape"]
)

@router.post("")
async def scrape_and_save(body: ScrapeRequest, current_user: dict = Depends(require_verified_user)):
    # Scrapea la url
    raw_data = await scrape_amazon(body.url)  # 👈 Usa await
    # Normaliza y ordena los datos
    normalized_data = normalize_children_text(raw_data)
    # Guarda directamente en data.json
    DATA_FILE.write_text(json.dumps(normalized_data, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"status": "success", "message": "Datos guardados en data.json"}

