import asyncio
import httpx
import os

PINCODE = os.environ.get("PINCODE", "110087")

async def scrape_zepto(product: str) -> dict | None:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "origin": "https://www.zeptonow.com",
            "referer": "https://www.zeptonow.com/",
        }
        payload = {
            "query": product,
            "pageNumber": 0,
            "pageSize": 5,
            "intent": False,
            "requiresKnowledge": False,
        }
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                "https://api.zeptonow.com/api/v3/search/",
                json=payload,
                headers=headers
            )
            data = resp.json()
            items = data.get("items", [])
            if not items:
                return None
            item = items[0].get("productVariant", items[0])
            name = item.get("name", product)
            price = float(item.get("sellingPrice", item.get("mrp", 0))) / 100
            unit = item.get("packageSize", item.get("unitQuantity", ""))
            return {
                "name": name,
                "price": price,
                "unit": str(unit),
                "url": f"https://www.zeptonow.com/search?query={product}"
            }
    except Exception as e:
        print(f"[Zepto] Error: {e}")
        return None
