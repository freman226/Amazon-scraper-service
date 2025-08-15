# purify.py
import json
import re
from pathlib import Path

INPUT_SCRAP = Path("scrapped_info.json")  # archivo generado por /scrape
OUTPUT_STRUCT = Path("data.json")         # salida estructurada
OUTPUT_FILE = Path("data/data.json")

TITLE_REGEX = re.compile(r'<h2[^>]*aria-label="([^"]+)"')
PRICE_REGEX = re.compile(r'US\$([\d.,]+)')
RATING_REGEX = re.compile(r'(\d+(?:\.\d+)?)\s+de\s+5\s+estrellas')

# ------- Reglas/heurísticas -------

DELIVERY_REGEX = re.compile(r"(FREE delivery.*|delivery .*|Arrives .*|Get it .*)", re.IGNORECASE)

BADGE_KEYWORDS = [
    "Add to cart", "See options", "More Buying Choices", "Only",
    "List:", "Exclusively for Prime Members"
]

def join_lines(lines):
    return [l.strip() for l in lines if l and l.strip()]

def find_rating(lines):
    for line in lines:
        m = RATING_REGEX.search(line)
        if m:
            try:
                return float(m.group(1))
            except:
                return m.group(1)
    return None

def find_reviews(lines):
    # normalmente la línea siguiente al rating es el n° de reseñas
    for i, line in enumerate(lines):
        if RATING_REGEX.search(line) and i + 1 < len(lines):
            nxt = lines[i+1].strip()
            if REVIEWS_REGEX.match(nxt):
                return nxt.replace(' ', '')
    # fallback
    for line in lines:
        if REVIEWS_REGEX.match(line.strip()):
            return line.strip().replace(' ', '')
    return None

def reconstruct_split_price(lines, idx):
    # Reconstruye precios partidos en 3 líneas: $199 / . / 99
    try:
        p1 = lines[idx].strip()
        p2 = lines[idx + 1].strip()
        p3 = lines[idx + 2].strip()
        if p1.startswith("$") and p2 == "." and p3.isdigit() and len(p3) == 2:
            return f"{p1.replace(' ', '')}.{p3}"
    except IndexError:
        pass
    return None

def find_price(lines):
    # 1) $xxx.xx directo
    for line in lines:
        m = PRICE_REGEX.search(line.replace(" ", ""))  # tolera espacios dentro
        if m:
            return m.group(0)
    # 2) Reconstrucción $199 \n . \n 99
    for idx, line in enumerate(lines):
        if line.strip().startswith("$"):
            rec = reconstruct_split_price(lines, idx)
            if rec:
                return rec
    # 3) "List: $xxx.xx"
    for line in lines:
        if "List:" in line:
            m = PRICE_REGEX.search(line)
            if m:
                return m.group(0)
    return None

def find_delivery(lines):
    for line in lines:
        m = DELIVERY_REGEX.search(line)
        if m:
            return m.group(0).strip()
    return None

def find_badges(lines):
    badges = []
    for line in lines:
        for kw in BADGE_KEYWORDS:
            if kw.lower() in line.lower():
                # si es "List: $..." guardamos la línea completa
                if kw.lower().startswith("list"):
                    badges.append(line.strip())
                else:
                    badges.append(kw)
    # dedup preservando orden
    seen, out = set(), []
    for b in badges:
        if b not in seen:
            seen.add(b)
            out.append(b)
    return out

def find_title(lines):
    """
    Heurística para el título:
    - Toma desde el inicio hasta la línea previa al rating o al primer precio.
    - Filtra textos obvios tipo "Price, product page".
    """
    rating_idx = None
    price_idx = None
    for i, line in enumerate(lines):
        if rating_idx is None and RATING_REGEX.search(line):
            rating_idx = i
        if price_idx is None and PRICE_REGEX.search(line.replace(" ", "")):
            price_idx = i

    cut_idx = None
    if rating_idx is not None and price_idx is not None:
        cut_idx = min(rating_idx, price_idx)
    elif rating_idx is not None:
        cut_idx = rating_idx
    elif price_idx is not None:
        cut_idx = price_idx

    if cut_idx is None:
        return lines[0].strip() if lines else None

    title_lines = lines[:cut_idx]
    title_lines = [l for l in title_lines if not l.lower().startswith("price, product page")]
    title = " ".join(title_lines).strip()
    title = re.sub(r"\s{2,}", " ", title)
    return title if title else (lines[0].strip() if lines else None)

def normalize_children_text(children_text_obj):
    """
    children_text_obj: dict con claves de tags (p.ej. {"div": "...", "span.xyz": "..."})
    Junta todos los valores a un solo texto y lo parsea.
    """
    if not isinstance(children_text_obj, dict):
        return None
    # concatenar valores string
    text = "\n".join([v for v in children_text_obj.values() if isinstance(v, str)])
    lines = join_lines(text.splitlines())
    return {
        "title": find_title(lines),
        "rating": find_rating(lines),
        "reviews": find_reviews(lines),
        "price": find_price(lines),
        "delivery": find_delivery(lines),
        "badges": find_badges(lines)
    }

def extract_title(html):
    match = TITLE_REGEX.search(html)
    return match.group(1) if match else None

def extract_price(html):
    match = PRICE_REGEX.search(html)
    return match.group(1) if match else None

def extract_rating(html):
    match = RATING_REGEX.search(html)
    return float(match.group(1)) if match else None

def purify():
    with open(INPUT_SCRAP, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    result = []
    for idx, item in enumerate(raw_data):
        html = item.get("raw_html", "")
        purified = {
            "id": idx + 1,
            "title": extract_title(html),
            "price": extract_price(html),
            "rating": extract_rating(html),
        }
        result.append(purified)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

def main():
    if not INPUT_SCRAP.exists():
        raise FileNotFoundError(f"No se encontró {INPUT_SCRAP}. Ejecuta primero el scraping.")

    # 1) leer scrapped_info.json (lista de productos)
    raw = json.loads(INPUT_SCRAP.read_text(encoding="utf-8"))

    # 2) extraer children_text y normalizar
    result = []
    for idx, prod in enumerate(raw, start=1):
        if isinstance(prod, dict) and "children_text" in prod:
            clean = normalize_children_text(prod["children_text"])
            if clean:
                clean["id"] = idx
                result.append(clean)

    # 3) guardar salida
    OUTPUT_STRUCT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK → {OUTPUT_STRUCT} ({len(result)} items)")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    purify()

import json

url = "TU_URL_DE_AMAZON"

