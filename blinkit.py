import httpx
import os

SERPAPI_KEY = os.environ.get("SERPAPI_KEY", "")

async def scrape_blinkit(product: str) -> dict | None:
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                "https://serpapi.com/search",
                params={
                    "engine": "google_shopping",
                    "q": f"{product} blinkit india",
                    "api_key": SERPAPI_KEY,
                    "gl": "in",
                    "hl": "en",
                    "num": 10,
                }
            )
            data = resp.json()
            results = data.get("shopping_results", [])

            # First try exact Blinkit match
            for r in results:
                if "blinkit" in r.get("source", "").lower():
                    return _parse(r, product, "https://blinkit.com")

            # Fallback: return first result with a price
            for r in results:
                parsed = _parse(r, product, "https://blinkit.com")
                if parsed:
                    return parsed

        return None
    except Exception as e:
        print(f"[Blinkit] Error: {e}")
        return None

def _parse(r: dict, product: str, fallback_url: str) -> dict | None:
    price_str = r.get("price", "0").replace("₹", "").replace(",", "").strip()
    try:
        price = float(price_str.split()[0])
    except:
        return None
    if price <= 0:
        return None
    return {
        "name": r.get("title", product)[:60],
        "price": price,
        "unit": r.get("source", ""),
        "url": r.get("link", fallback_url)
    }
