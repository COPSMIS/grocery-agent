import google.generativeai as genai
import os

# reads GEMINI_API_KEY from environment variable
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

async def get_ai_suggestion(product: str, price_data: dict) -> str:
    """
    Uses Gemini 2.0 Flash (free) to generate a friendly WhatsApp-style price comparison message.
    price_data format: { "Blinkit": {name, price, unit, url}, "Zepto": {...}, ... }
    """

    # Build a prompt with the scraped data
    price_summary = ""
    for platform, data in price_data.items():
        price_summary += f"- {platform}: ₹{data['price']} for {data.get('unit', 'N/A')} ({data['name']})\n"

    prompt = f"""
You are a helpful grocery price comparison assistant in India.
A user searched for: "{product}"

Here are the prices found:
{price_summary}

Generate a clear, friendly WhatsApp message (use emojis) that:
1. Shows a price comparison table for all platforms
2. Clearly highlights the CHEAPEST option with savings amount
3. Mentions if any platform didn't have the item
4. Gives a short 1-line recommendation
5. Keep it under 300 words

Format it nicely for WhatsApp (use *bold* for emphasis, line breaks for readability).
"""

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text
