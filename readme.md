#  Weather-Aware Order Delay Checker

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
├── main.py             # Python backend script
├── server.js           # Express server — proxies API calls, keeps keys secure
├── index.html          # Frontend UI — space-themed, served by Express
├── package.json        # Node.js dependencies for the server
├── test_main.py        # Unit tests (pytest) — mocked, no API keys needed
├── run_tests.py        # End-to-end mock runner — generates test_results.json
├── mock_orders.json    # Sample orders with all weather conditions pre-set
├── test_results.json   # Auto-generated after running run_tests.py
├── orders.json         # Real input orders (updated in-place after running main.py)
├── .env                # API keys — never commit this!
├── requirements.txt    # Python dependencies
├── AI_LOG.md           # Prompts used during development
└── README.md           # This file
```

---

## 🖥️ Running the UI (Web Dashboard)

The project includes a visual dashboard (`index.html`) served by a tiny Express server (`server.js`). The server acts as a **secure proxy** — API keys stay in `.env` on the server and are never exposed to the browser.

### How it works
```
Browser → /api/weather   → server.js → OpenWeatherMap (with real key)
Browser → /api/apology   → server.js → Gemini API     (with real key)
```

### Setup & Run

**1. Install Node dependencies:**
```bash
npm install
```

**2. Make sure your `.env` has both keys:**
```
OPENWEATHER_API_KEY=your_openweathermap_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

**3. Start the server:**
```bash
node server.js
```

**4. Open in browser:**
```
http://localhost:3000
```

**5. Click "Fetch Current Weather & Update Orders"** — the UI will:
- Fire all weather calls concurrently
- Update each row live with weather condition + status badge
- Generate AI apology messages for delayed orders
- Show a "View Updated orders.json" button with the full syntax-highlighted result

> 💡 For development with auto-reload: `npm run dev` (requires nodemon)

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

##  Key Technical Decisions

| Feature | Approach |
|---|---|
| Concurrent API calls | `asyncio.gather()` + `aiohttp` |
| AI apology messages | Gemini 2.0 Flash via `google-genai` |
| Error handling | `try/except` per order — script never crashes |
| API key security | `.env` file + `python-dotenv` |

---


## 🚀 Deploying to Render (Free Public Link)

Render hosts your Express server and gives you a public URL like `https://weathergate.onrender.com` you can share with anyone.

### Step 1 — Push to GitHub

Make sure your project is on GitHub first. In your project folder:
```bash
git init
git add .
git commit -m "initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/weathergate.git
git push -u origin main
```

> ⚠️ Double-check that `.env` is in `.gitignore` before pushing — your API keys must never go to GitHub.

---

### Step 2 — Create a Render Account
Go to **https://render.com** and sign up with your GitHub account.

---

### Step 3 — Create a New Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repo (`weathergate`)
3. Render will auto-detect the settings from `render.yaml`, but verify:

| Setting | Value |
|---|---|
| **Environment** | `Node` |
| **Build Command** | `npm install` |
| **Start Command** | `npm start` |
| **Instance Type** | `Free` |

---

### Step 4 — Add Your API Keys as Environment Variables

In the Render dashboard, go to your service → **Environment** tab → add:

| Key | Value |
|---|---|
| `OPENWEATHER_API_KEY` | your OpenWeatherMap key |
| `GEMINI_API_KEY` | your Gemini API key |

> This is the equivalent of your `.env` file — keys live securely on Render's server, never in your code.

---

### Step 5 — Deploy

Click **"Create Web Service"**. Render will:
1. Pull your code from GitHub
2. Run `npm install`
3. Start your server with `npm start`
4. Give you a live URL like `https://weathergate.onrender.com`

**First deploy takes ~2 minutes.** After that, every `git push` to `main` auto-deploys.

---

### ⚠️ Free Tier Note
Render's free tier **spins down after 15 minutes of inactivity**. The first visit after inactivity takes ~30 seconds to wake up. This is normal — just refresh if it's slow.

---

## 🧪 Testing

Two levels of testing are provided — no real API keys needed for either.

---

### 1. Unit Tests — `test_main.py`
Verifies individual functions in isolation using mocked API calls.

**Install dependencies:**
```bash
pip install pytest pytest-asyncio
```

**Run:**
```bash
pytest test_main.py -v
```

**Expected output:**
```
collected 10 items

test_main.py::test_generate_apology_contains_customer_name   PASSED
test_main.py::test_generate_apology_contains_city            PASSED
test_main.py::test_generate_apology_starts_with_hi           PASSED
test_main.py::test_generate_apology_returns_string           PASSED
test_main.py::test_order_marked_delayed_on_rain              PASSED
test_main.py::test_order_marked_delayed_on_snow              PASSED
test_main.py::test_order_marked_delayed_on_extreme           PASSED
test_main.py::test_order_on_time_for_clear_weather           PASSED
test_main.py::test_invalid_city_does_not_crash               PASSED
test_main.py::test_invalid_city_does_not_affect_other_orders PASSED

10 passed in 0.35s
```

| Test | What it checks |
|---|---|
| `test_generate_apology_contains_customer_name` | Apology includes the customer's name |
| `test_generate_apology_contains_city` | Apology mentions the city |
| `test_generate_apology_starts_with_hi` | Apology starts with `"Hi <name>,"` |
| `test_generate_apology_returns_string` | Apology is a non-empty, stripped string |
| `test_order_marked_delayed_on_rain` | Order marked `Delayed` + apology added for `Rain` |
| `test_order_marked_delayed_on_snow` | Order marked `Delayed` for `Snow` |
| `test_order_marked_delayed_on_extreme` | Order marked `Delayed` for `Extreme` |
| `test_order_on_time_for_clear_weather` | Order marked `On Time`, no apology added |
| `test_invalid_city_does_not_crash` | Invalid city sets `Error - City Not Found`, no crash |
| `test_invalid_city_does_not_affect_other_orders` | Valid orders still process when one city fails |

---

### 2. End-to-End Mock Runner — `run_tests.py` + `mock_orders.json`

Simulates all weather conditions (Rain, Snow, Clear, Invalid) using `mock_orders.json` and saves a full pass/fail report with AI apology messages to `test_results.json`.

**Run:**
```bash
python run_tests.py
```

**Console output:**
```
INFO: ✅ Order 1001 → Delayed | Hi Alice Smith, your order to New York is delayed due to Rain. We appreciate your patience!
INFO: ✅ Order 1002 → Delayed | Hi Bob Jones, your order to Mumbai is delayed due to Snow. We appreciate your patience!
INFO: ✅ Order 1003 → On Time (weather: Clear)
ERROR: ❌ Order 1004 → City 'InvalidCity123' not found.

──────────────── Test Summary ────────────────
  Order 1001 | Alice Smith     | Weather: Rain  | Status: Delayed                | PASS ✅
  Order 1002 | Bob Jones       | Weather: Snow  | Status: Delayed                | PASS ✅
  Order 1003 | Charlie Green   | Weather: Clear | Status: On Time                | PASS ✅
  Order 1004 | InvalidCity123  | Weather: N/A   | Status: Error - City Not Found | PASS ✅

  Overall: ALL TESTS PASSED ✅
  Results saved to → test_results.json
```

**Generated `test_results.json`** (saved automatically after running):
```json
{
  "summary": {
    "total_orders": 4,
    "delayed": 2,
    "on_time": 1,
    "errors": 1,
    "all_tests_passed": true
  },
  "orders": [
    {
      "order_id": "1001",
      "customer": "Alice Smith",
      "city": "New York",
      "weather_condition": "Rain",
      "status": "Delayed",
      "apology_message": "Hi Alice Smith, your order to New York is delayed due to Rain. We appreciate your patience!",
      "test_result": { "status_check": "PASS ✅", "apology_check": "PASS ✅", "overall": "PASS ✅" }
    },
    {
      "order_id": "1002",
      "customer": "Bob Jones",
      "city": "Mumbai",
      "weather_condition": "Snow",
      "status": "Delayed",
      "apology_message": "Hi Bob Jones, your order to Mumbai is delayed due to Snow. We appreciate your patience!",
      "test_result": { "status_check": "PASS ✅", "apology_check": "PASS ✅", "overall": "PASS ✅" }
    },
    {
      "order_id": "1003",
      "customer": "Charlie Green",
      "city": "London",
      "weather_condition": "Clear",
      "status": "On Time",
      "apology_message": "N/A — weather is clear, no delay",
      "test_result": { "status_check": "PASS ✅", "apology_check": "PASS ✅", "overall": "PASS ✅" }
    },
    {
      "order_id": "1004",
      "customer": "InvalidCity123",
      "city": "InvalidCity123",
      "weather_condition": "N/A",
      "status": "Error - City Not Found",
      "apology_message": "N/A — weather is clear, no delay",
      "test_result": { "status_check": "PASS ✅", "apology_check": "PASS ✅", "overall": "PASS ✅" }
    }
  ]
}
```

> ✅ No real API keys needed for either test approach — all external calls are mocked.

---

## 📝 AI Log
See [`AI_LOG.md`](./AI_LOG.md) for the prompts used to build the parallel fetching, error handling, and apology message logic.
