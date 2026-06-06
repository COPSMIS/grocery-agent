import asyncio
from playwright.async_api import async_playwright

# ──────────────────────────────────────────────
# SET YOUR PINCODE HERE
PINCODE = "110087"
# ──────────────────────────────────────────────

async def scrape_zepto(product: str) -> dict | None:
    """
    Scrapes Zepto for the top result of a product.
    Returns: { name, price, unit, url } or None
    """
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            search_url = f"https://www.zeptonow.com/search?query={product.replace(' ', '%20')}"
            await page.goto(search_url, timeout=30000, wait_until="domcontentloaded")
            await page.wait_for_timeout(4000)

            # Dismiss location modal if shown
            try:
                close_btn = page.locator("button[aria-label='Close'], [class*='modal'] button").first
                if await close_btn.is_visible():
                    await close_btn.click()
                    await page.wait_for_timeout(1000)
            except:
                pass

            # Scrape first product card
            items = await page.locator("[data-testid='product-card'], [class*='ProductCard'], [class*='product-card']").all()

            if not items:
                await browser.close()
                return None

            first = items[0]

            name = await first.locator("[class*='name'], [class*='title'], h3, h4, p").first.inner_text()
            price_raw = await first.locator("[class*='price'], [class*='Price']").first.inner_text()
            price = float(''.join(filter(lambda x: x.isdigit() or x == '.', price_raw.split('\n')[0])))

            try:
                unit = await first.locator("[class*='weight'], [class*='quantity'], [class*='grammage']").first.inner_text()
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
        print(f"[Zepto] Error: {e}")
        return None
