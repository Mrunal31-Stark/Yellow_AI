# 🌦️ Weather-Aware Order Delay Checker

A Python script that checks real-time weather for customer delivery cities and automatically flags orders as **Delayed** when bad weather is detected — with AI-generated personalized apology messages powered by **Gemini**.

---

## 📋 What It Does

1. Reads customer orders from `orders.json`
2. Fetches live weather for each city **concurrently** using OpenWeatherMap API
3. Marks any order as `Delayed` if weather is `Rain`, `Snow`, or `Extreme`
4. Uses **Gemini AI** to generate a personalized apology message for each delayed order
5. Handles invalid cities gracefully — logs the error and continues processing others
6. Saves the updated statuses back to `orders.json`

---

## 🗂️ Project Structure

```
project/
├── main.py             # Main script
├── orders.json         # Input orders (updated in-place after running)
├── .env                # API keys — never commit this!
├── requirements.txt    # Python dependencies
├── AI_LOG.md           # Prompts used during development
└── README.md           # This file
```

---

## ⚙️ Setup Instructions

### 1. Clone or Download the Project
```bash
git clone <your-repo-url>
cd <project-folder>
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

**requirements.txt contents:**
```
aiohttp
python-dotenv
google-genai
```

### 3. Create Your `.env` File
Create a file named `.env` in the root of the project:
```
OPENWEATHER_API_KEY=your_openweathermap_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

> ⚠️ Never commit this file to GitHub. Add `.env` to your `.gitignore`.

### 4. Get Your API Keys

**OpenWeatherMap (Free Tier):**
1. Sign up at https://openweathermap.org/api
2. Go to API Keys in your account dashboard
3. Copy your key — note: new keys can take **up to 2 hours** to activate

**Gemini API:**
1. Go to https://aistudio.google.com/app/apikey
2. Create a new API key and copy it

### 5. Set Up `orders.json`
Make sure `orders.json` exists in the same folder as `main.py`:
```json
[
  { "order_id": "1001", "customer": "Alice Smith", "city": "New York", "status": "Pending" },
  { "order_id": "1002", "customer": "Bob Jones", "city": "Mumbai", "status": "Pending" },
  { "order_id": "1003", "customer": "Charlie Green", "city": "London", "status": "Pending" },
  { "order_id": "1004", "customer": "InvalidCity123", "city": "InvalidCity123", "status": "Pending" }
]
```

### 6. Run the Script
```bash
python main.py
```

---

## 📤 Sample Output

**Console logs:**
```
INFO: Weather for New York: Rain
INFO: Weather for London: Clouds
INFO: Weather for Mumbai: Clear
ERROR: Skipping order 1004: City 'InvalidCity123' not found.
INFO: Order 1001 marked Delayed. Message: Hi Alice, your order to New York is delayed...
INFO: Done! orders.json has been updated.
```

**Updated `orders.json`:**
```json
[
  {
    "order_id": "1001",
    "customer": "Alice Smith",
    "city": "New York",
    "status": "Delayed",
    "apology_message": "Hi Alice, your order to New York is delayed due to Rain. We appreciate your patience!"
  },
  {
    "order_id": "1002",
    "customer": "Bob Jones",
    "city": "Mumbai",
    "status": "On Time"
  },
  {
    "order_id": "1003",
    "customer": "Charlie Green",
    "city": "London",
    "status": "On Time"
  },
  {
    "order_id": "1004",
    "customer": "InvalidCity123",
    "city": "InvalidCity123",
    "status": "Error - City Not Found"
  }
]
```

---

## 🔑 Key Technical Decisions

| Feature | Approach |
|---|---|
| Concurrent API calls | `asyncio.gather()` + `aiohttp` |
| AI apology messages | Gemini 2.0 Flash via `google-genai` |
| Error handling | `try/except` per order — script never crashes |
| API key security | `.env` file + `python-dotenv` |

---

## 📝 AI Log
See [`AI_LOG.md`](./AI_LOG.md) for the prompts used to build the parallel fetching, error handling, and apology message logic.