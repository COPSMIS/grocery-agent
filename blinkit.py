import asyncio
from playwright.async_api import async_playwright

# ──────────────────────────────────────────────
# SET YOUR PINCODE HERE
PINCODE = "110087"
# ──────────────────────────────────────────────

async def scrape_blinkit(product: str) -> dict | None:
    """
    Scrapes Blinkit for the top result of a product.
    Returns: { name, price, unit, url } or None
    """
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            search_url = f"https://blinkit.com/s/?q={product.replace(' ', '+')}"
            await page.goto(search_url, timeout=30000, wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)

            # Try to set pincode if prompted
            try:
                if await page.locator("input[placeholder*='pincode'], input[placeholder*='location']").count() > 0:
                    await page.fill("input[placeholder*='pincode']", PINCODE)
                    await page.keyboard.press("Enter")
                    await page.wait_for_timeout(2000)
            except:
                pass

            # Scrape first product card
            items = await page.locator(".product-container, [data-testid='product-card'], .Product__UpdatedPlpProductContainer").all()

            if not items:
                # Fallback selector
                items = await page.locator("div[class*='plp-product']").all()

            if not items:
                await browser.close()
                return None

            first = items[0]

            name  = await first.locator("[class*='Product__name'], [class*='product-name'], h5, h4").first.inner_text()
            price_text = await first.locator("[class*='Product__price'], [class*='price']").first.inner_text()
            price = float(''.join(filter(lambda x: x.isdigit() or x == '.', price_text.split('\n')[0])))

            try:
                unit = await first.locator("[class*='weight'], [class*='quantity'], [class*='unit']").first.inner_text()
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
        print(f"[Blinkit] Error: {e}")
        return None
