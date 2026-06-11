import google.generativeai as genai
import os
import asyncio

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

async def get_ai_suggestion(product: str, price_data: dict) -> str:
    """
    Uses Gemini to generate a friendly WhatsApp price comparison message.
    Falls back to a simple formatted message if AI fails.
    """
    try:
        price_summary = ""
        for platform, data in price_data.items():
            price_summary += f"- {platform}: ₹{data['price']} for {data.get('unit', '')} ({data['name']})\n"

        prompt = f"""You are a grocery price comparison assistant in India.
Product searched: "{product}"

Prices found:
{price_summary}

Write a short WhatsApp message (use emojis) that:
1. Shows prices for each platform
2. Highlights the cheapest with savings amount
3. Gives a 1-line recommendation
Keep it under 200 words. Use *bold* for emphasis."""

        # Try gemini-2.0-flash-lite first (higher free quota)
        for model_name in ["gemini-2.0-flash-lite", "gemini-2.0-flash", "gemini-1.5-flash-latest"]:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                return response.text
            except Exception as e:
                if "quota" in str(e).lower() or "429" in str(e):
                    await asyncio.sleep(2)
                    continue
                raise e

        # All models failed quota — return simple formatted message
        return _simple_comparison(product, price_data)

    except Exception as e:
        print(f"[Gemini] Error: {e}")
        return _simple_comparison(product, price_data)


def _simple_comparison(product: str, price_data: dict) -> str:
    """Fallback: simple formatted message without AI"""
    if not price_data:
        return f"❌ No prices found for *{product}*"

    lines = [f"🛒 *Price Comparison: {product.title()}*\n"]
    prices = []

    for platform, data in price_data.items():
        price = data['price']
        unit = data.get('unit', '')
        name = data.get('name', product)
        unit_str = f" ({unit})" if unit else ""
        lines.append(f"• *{platform}*: ₹{price}{unit_str}")
        prices.append((platform, price))

    if prices:
        prices.sort(key=lambda x: x[1])
        cheapest_platform, cheapest_price = prices[0]
        if len(prices) > 1:
            most_expensive = prices[-1][1]
            savings = round(most_expensive - cheapest_price, 2)
            lines.append(f"\n✅ *Best deal: {cheapest_platform}* at ₹{cheapest_price}")
            if savings > 0:
                lines.append(f"💰 Save ₹{savings} vs most expensive option!")
        else:
            lines.append(f"\n✅ *Best deal: {cheapest_platform}* at ₹{cheapest_price}")

    return "\n".join(lines)
