import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Form
from fastapi.responses import PlainTextResponse
from twilio.twiml.messaging_response import MessagingResponse
from blinkit import scrape_blinkit
from zepto import scrape_zepto
from instamart import scrape_instamart
from claude_ai import get_ai_suggestion
import asyncio
import traceback

app = FastAPI()

@app.get("/")
def root():
    return {"status": "Grocery Price Agent is running 🛒"}

@app.get("/test")
def test():
    return {
        "status": "ok",
        "gemini_key_set": bool(os.environ.get("GEMINI_API_KEY")),
        "pincode": os.environ.get("PINCODE", "not set"),
    }

@app.post("/whatsapp", response_class=PlainTextResponse)
async def whatsapp_webhook(
    Body: str = Form(default=""),
    From: str = Form(default="")
):
    response = MessagingResponse()
    msg = response.message()

    try:
        user_message = Body.strip().lower()

        keywords = ["compare", "price", "check", "find"]
        product = user_message
        for kw in keywords:
            product = product.replace(kw, "").strip()

        if len(product) < 2:
            msg.body(
                "👋 *Grocery Price Agent*\n\n"
                "Send me a product name!\n\n"
                "Examples:\n"
                "• compare tomatoes\n"
                "• price onion 1kg\n"
                "• check milk\n"
                "• find bread"
            )
            return str(response)

        results = await asyncio.gather(
            scrape_blinkit(product),
            scrape_zepto(product),
            scrape_instamart(product),
            return_exceptions=True
        )

        price_data = {}
        platforms = ["Blinkit", "Zepto", "Swiggy Instamart"]
        for i, result in enumerate(results):
            if result and not isinstance(result, Exception):
                price_data[platforms[i]] = result

        if not price_data:
            msg.body(
                f"❌ Couldn't find *{product}* on any platform.\n"
                "Try a different name e.g. 'tomato' instead of 'tomatoes'"
            )
            return str(response)

        suggestion = await get_ai_suggestion(product, price_data)
        msg.body(suggestion)

    except Exception as e:
        traceback.print_exc()
        msg.body(f"⚠️ Error: {str(e)}")

    return str(response)
