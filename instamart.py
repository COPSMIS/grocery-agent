import asyncio
from playwright.async_api import async_playwright

async def scrape_instamart(product: str) -> dict | None:
    """
    Scrapes Swiggy Instamart for the top result of a product.
    Returns: { name, price, unit, url } or None
    """
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            search_url = f"https://www.swiggy.com/instamart/search?query={product.replace(' ', '%20')}"
            await page.goto(search_url, timeout=30000, wait_until="domcontentloaded")
            await page.wait_for_timeout(4000)

            # Dismiss any popups
            try:
                popup = page.locator("[class*='modal'] [class*='close'], [aria-label='close']").first
                if await popup.is_visible():
                    await popup.click()
                    await page.wait_for_timeout(1000)
            except:
                pass

            # Scrape first product card
            items = await page.locator("[class*='ItemWidget'], [class*='product-card'], [data-testid='item-widget']").all()

            if not items:
                # Fallback
                items = await page.locator("div[class*='styles_container']").all()

            if not items:
                await browser.close()
                return None

            first = items[0]

            name = await first.locator("[class*='name'], [class*='title'], [class*='Name'], div[class*='ItemName']").first.inner_text()
            price_raw = await first.locator("[class*='price'], [class*='Price'], [class*='rupee']").first.inner_text()
            price = float(''.join(filter(lambda x: x.isdigit() or x == '.', price_raw.split('\n')[0])))

            try:
                unit = await first.locator("[class*='weight'], [class*='quantity'], [class*='grammage'], [class*='unit']").first.inner_text()
            except:
                unit = ""

            await browser.close()
            return {
                "name": name.strip(),
                "price": price,
                "unit": unit.strip(),
                "url": search_url
            }

    except Exception as e:
        print(f"[Instamart] Error: {e}")
        return None
