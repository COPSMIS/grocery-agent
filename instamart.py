# Swiggy Instamart price fetcher via SerpApi Google Shopping
import httpx
import os

SERPAPI_KEY = os.environ.get("SERPAPI_KEY", "")

async def scrape_instamart(product: str) -> dict | None:
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                "https://serpapi.com/search",
                params={
                    "engine": "google_shopping",
                    "q": f"{product} swiggy instamart",
                    "api_key": SERPAPI_KEY,
                    "gl": "in",
                    "hl": "en",
                    "num": 3,
                }
            )
            data = resp.json()
            results = data.get("shopping_results", [])
            for r in results:
                source = r.get("source", "").lower()
                if "swiggy" in source or "instamart" in source:
                    price_str = r.get("price", "0").replace("₹", "").replace(",", "").strip()
                    try:
                        price = float(price_str)
                    except:
                        price = 0
                    if price > 0:
                        return {
                            "name": r.get("title", product),
                            "price": price,
                            "unit": "",
                            "url": r.get("link", "https://www.swiggy.com/instamart")
                        }
        return None
    except Exception as e:
        print(f"[Instamart] Error: {e}")
        return None
