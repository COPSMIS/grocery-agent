import asyncio
import httpx
import os

PINCODE = os.environ.get("PINCODE", "110001")

async def scrape_instamart(product: str) -> dict | None:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "__fetch_req__": "true",
            "origin": "https://www.swiggy.com",
            "referer": "https://www.swiggy.com/instamart",
        }
        params = {
            "pageNumber": 0,
            "searchResultsOffset": 0,
            "layoutPageType": "INSTAMART_AUTO_SUGGEST_SEARCH_PAGE",
            "query": product,
            "ageConsent": "false",
            "pageType": "INSTAMART_SEARCH_PAGE",
        }
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                "https://www.swiggy.com/api/instamart/home",
                params=params,
                headers=headers
            )
            data = resp.json()
            # Navigate Swiggy's nested response
            try:
                widgets = data["data"]["widgets"]
                for w in widgets:
                    items = w.get("data", {}).get("items", [])
                    if items:
                        item = items[0]
                        variations = item.get("variations", [item])
                        v = variations[0]
                        name = v.get("display_name", item.get("display_name", product))
                        price = float(v.get("price", {}).get("offer_price", 0)) / 100
                        unit = v.get("quantity", "")
                        if price > 0:
                            return {
                                "name": name,
                                "price": price,
                                "unit": str(unit),
                                "url": f"https://www.swiggy.com/instamart/search?query={product}"
                            }
            except (KeyError, IndexError, TypeError):
                pass
            return None
    except Exception as e:
        print(f"[Instamart] Error: {e}")
        return None
