# app/api/routers/ask.py
import json
from fastapi import APIRouter, Depends
from app.schemas.prompt import AskBody
from app.services.gemini import ask_gemini
from app.core.config import DATA_FILE
from app.core.auth import require_verified_user  

router = APIRouter(
    prefix="/prompt",
    tags=["prompt"],
)


@router.post("")
def ask(body: AskBody, current_user: dict = Depends(require_verified_user)):  # 👈
    if not DATA_FILE.exists():
        return {"status": "error", "message": "data.json no existe. Ejecuta primero /scrape."}
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    ans = ask_gemini(data, body.question)
    return {"status": "success", "answer": ans}
