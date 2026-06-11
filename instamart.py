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
                    "q": f"{product} swiggy instamart india",
                    "api_key": SERPAPI_KEY,
                    "gl": "in",
                    "hl": "en",
                    "num": 10,
                }
            )
            data = resp.json()
            results = data.get("shopping_results", [])

            # First try exact Instamart match
            for r in results:
                source = r.get("source", "").lower()
                if "swiggy" in source or "instamart" in source:
                    return _parse(r, product, "https://www.swiggy.com/instamart")

            # Fallback: return first result with a price
            for r in results:
                parsed = _parse(r, product, "https://www.swiggy.com/instamart")
                if parsed:
                    return parsed

        return None
    except Exception as e:
        print(f"[Instamart] Error: {e}")
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
