from fastapi import FastAPI, Form, Request
from fastapi.responses import PlainTextResponse
from twilio.twiml.messaging_response import MessagingResponse
from scrapers.blinkit import scrape_blinkit
from scrapers.zepto import scrape_zepto
from scrapers.instamart import scrape_instamart
from utils.claude_ai import get_ai_suggestion
import asyncio

app = FastAPI()

@app.get("/")
def root():
    return {"status": "Grocery Price Agent is running 🛒"}

@app.post("/whatsapp", response_class=PlainTextResponse)
async def whatsapp_webhook(
    Body: str = Form(...),
    From: str = Form(...)
):
    user_message = Body.strip().lower()
    response = MessagingResponse()
    msg = response.message()

    # Parse product from message
    # Supports: "compare tomatoes", "price onion", "check milk 1l"
    keywords = ["compare", "price", "check", "find"]
    product = user_message
    for kw in keywords:
        product = product.replace(kw, "").strip()

    if len(product) < 2:
        msg.body(
            "👋 *Grocery Price Agent*\n\n"
            "Send me a product name to compare prices!\n\n"
            "Examples:\n"
            "• compare tomatoes\n"
            "• price onion 1kg\n"
            "• check milk 1l\n"
            "• find bread"
        )
        return str(response)

    msg.body(f"🔍 Searching prices for *{product}*...\nPlease wait a moment!")

    # Run scrapers in parallel
    try:
        results = await asyncio.gather(
            scrape_blinkit(product),
            scrape_zepto(product),
            scrape_instamart(product),
            return_exceptions=True
        )

        blinkit_data  = results[0] if not isinstance(results[0], Exception) else None
        zepto_data    = results[1] if not isinstance(results[1], Exception) else None
        instamart_data = results[2] if not isinstance(results[2], Exception) else None

        # Build price summary
        price_data = {}
        if blinkit_data:
            price_data["Blinkit"] = blinkit_data
        if zepto_data:
            price_data["Zepto"] = zepto_data
        if instamart_data:
            price_data["Swiggy Instamart"] = instamart_data

        if not price_data:
            msg.body(f"❌ Sorry, couldn't find *{product}* on any platform right now. Try a different name.")
            return str(response)

        # Get AI suggestion
        suggestion = await get_ai_suggestion(product, price_data)
        msg.body(suggestion)

    except Exception as e:
        msg.body(f"⚠️ Something went wrong: {str(e)}\nPlease try again.")

    return str(response)
