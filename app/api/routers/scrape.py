# app/api/routers/scrape.py
from fastapi import APIRouter, Depends
from app.schemas.scrape import ScrapeRequest
from scraper import scrape_amazon
import json
import subprocess

router = APIRouter(
    prefix="/scrape",
    tags=["scrape"]
)

@router.post("")
def scrape_and_purify(body: ScrapeRequest):
    # 1. Scraping
    data = scrape_amazon(body.url)
    with open("scrapped_info.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    # 2. Purificación (ejecuta purify.py)
    subprocess.run(["python", "purify.py"])
    # 3. Retorna el resultado
    with open("data.json", "r", encoding="utf-8") as f:
        result = json.load(f)
    return {"status": "success", "items": len(result)}

