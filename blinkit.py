import asyncio
import httpx
import os

PINCODE = os.environ.get("PINCODE", "110087")

async def scrape_blinkit(product: str) -> dict | None:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "app_client": "consumer_web",
            "web_app_version": "1000",
        }
        params = {
            "search_keyword": product,
            "size": 5,
            "start": 0,
        }
        async with httpx.AsyncClient(timeout=15) as client:
            # Set location first
            await client.get(
                f"https://blinkit.com/v1/location/selected?pincode={PINCODE}",
                headers=headers
            )
            resp = await client.get(
                "https://blinkit.com/v2/product/search/",
                params=params,
                headers=headers
            )
            data = resp.json()
            products = data.get("objects", [])
            if not products:
                return None
            p = products[0]
            return {
                "name": p.get("name", product),
                "price": float(p.get("mrp", p.get("price", 0))),
                "unit": p.get("unit", p.get("description", "")),
                "url": f"https://blinkit.com/s/?q={product}"
            }
    except Exception as e:
        print(f"[Blinkit] Error: {e}")
        return None
