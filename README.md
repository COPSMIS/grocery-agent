# 🛒 Grocery Price Agent — WhatsApp Bot

Compares prices on **Blinkit**, **Zepto**, and **Swiggy Instamart** and sends you the best deal via WhatsApp — no manual triggering needed!

---

## How It Works

```
You → WhatsApp "compare tomatoes"
         ↓
   Bot scrapes all 3 apps
         ↓
   Claude AI compares prices
         ↓
   Best deal sent back to WhatsApp ✅
```

---

## Setup Guide (Step by Step)

### Step 1 — Get Your API Keys

#### A) Twilio (WhatsApp)
1. Go to [twilio.com](https://twilio.com) → Sign up (free)
2. Go to **Messaging → Try it out → Send a WhatsApp message**
3. Follow sandbox setup — send the join code from your phone
4. Note down:
   - `TWILIO_ACCOUNT_SID`
   - `TWILIO_AUTH_TOKEN`
   - Your Twilio WhatsApp number (e.g. `+14155238886`)

#### B) Gemini AI (Free)
1. Go to [aistudio.google.com](https://aistudio.google.com)
2. Click **Get API Key** → Create API key
3. Note down: `GEMINI_API_KEY`
4. Free tier: 1500 requests/day — no credit card needed!

---

### Step 2 — Set Your Config

Edit `scrapers/blinkit.py` and `scrapers/zepto.py`:
```python
PINCODE = "110001"   # ← Change to YOUR pincode
```

---

### Step 3 — Deploy to Render (Free Hosting)

1. Push this folder to a **GitHub repo**
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your GitHub repo
4. Render auto-detects `render.yaml`
5. Add these **Environment Variables** in Render dashboard:
   ```
   GEMINI_API_KEY = your_key_here
   TWILIO_ACCOUNT_SID = your_sid_here
   TWILIO_AUTH_TOKEN = your_token_here
   ```
6. Deploy! Note your app URL: `https://your-app.onrender.com`

---

### Step 4 — Connect Twilio Webhook

1. In Twilio Console → Messaging → Sandbox Settings
2. Set **"When a message comes in"** to:
   ```
   https://your-app.onrender.com/whatsapp
   ```
3. Method: `POST`
4. Save!

---

### Step 5 — Test It!

Send a WhatsApp message to your Twilio sandbox number:
```
compare tomatoes
price onion 1kg
check milk
```

---

## Usage Examples

| You send | Bot replies |
|---|---|
| `compare tomatoes` | Price comparison + best deal |
| `price onion 1kg` | Cheapest platform highlighted |
| `check milk 1l` | AI suggestion with savings |
| `find bread` | All platform prices + recommendation |

---

## Project Structure

```
grocery-price-agent/
├── main.py               # FastAPI server + WhatsApp webhook
├── requirements.txt      # Python dependencies
├── render.yaml           # Render deployment config
├── scrapers/
│   ├── blinkit.py        # Blinkit scraper
│   ├── zepto.py          # Zepto scraper
│   └── instamart.py      # Swiggy Instamart scraper
└── utils/
    └── claude_ai.py      # Claude AI for smart suggestions
```

---

## ⚠️ Important Notes

- **Scraping disclaimer**: These scrapers are for personal use only. The apps may change their HTML structure, which can break scrapers. If a scraper fails, update the CSS selectors.
- **Location**: Prices are location-based. Make sure to set your PINCODE correctly.
- **Free tier limits**: Render free tier spins down after inactivity (30s cold start). Upgrade to paid for always-on.
- **Twilio sandbox**: Free sandbox has a join-code flow. For production, apply for WhatsApp Business API.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Bot not responding | Check Render logs, verify webhook URL in Twilio |
| Wrong prices | Update CSS selectors in scraper files |
| Timeout errors | Increase `wait_for_timeout` values in scrapers |
| Cold start delay | Upgrade Render plan or use Railway |
