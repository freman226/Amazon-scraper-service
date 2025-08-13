# app/services/scraper.py
from playwright.async_api import async_playwright

async def scrape_amazon(url: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        # Extrae los productos usando selectores
        items = []
        products = await page.query_selector_all(".clase-del-producto")  # Ajusta el selector
        for product in products:
            title = await product.query_selector_eval(".clase-titulo", "el => el.textContent")
            price = await product.query_selector_eval(".clase-precio", "el => el.textContent")
            link = await product.query_selector_eval("a", "el => el.href")
            items.append({
                "title": title,
                "price": price,
                "url": link
            })
        await browser.close()
        return items
