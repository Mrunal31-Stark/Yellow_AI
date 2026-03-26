import asyncio
import aiohttp
import json
import os
import logging
from dotenv import load_dotenv
from google import genai

# ── Setup ──────────────────────────────────────────────────────────────────────
load_dotenv()
WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# ── Step 1: Fetch weather for a single city (async) ────────────────────────────
async def fetch_weather(session, city):
    """
    Calls OpenWeatherMap API for a given city.
    Returns the weather data dict, or raises an exception if city is invalid.
    """
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": WEATHER_API_KEY}

    async with session.get(url, params=params) as response:
        if response.status == 200:
            data = await response.json()
            weather_main = data["weather"][0]["main"]  # e.g. "Rain", "Clear"
            logging.info(f"Weather for {city}: {weather_main}")
            return weather_main
        else:
            # This handles InvalidCity123 and any other bad city names
            error_text = await response.text()
            raise ValueError(f"City '{city}' not found. API response: {error_text}")

# ── Step 2: Generate apology message using Gemini AI ──────────────────────────
def generate_apology(customer_name, city, weather_condition):
    """
    Uses Gemini to write a personalized apology message for a delayed order.
    """
    prompt = (
        f"Write a short, warm apology message for a customer whose delivery is delayed due to weather. "
        f"Customer name: {customer_name}. City: {city}. Weather condition: {weather_condition}. "
        f"Keep it under 2 sentences and start with 'Hi {customer_name},'."
    )

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    return response.text.strip()

# ── Step 3: Process a single order ────────────────────────────────────────────
async def process_order(session, order):
    """
    Fetches weather for the order's city and updates its status if needed.
    Handles errors gracefully so one bad city doesn't crash everything.
    """
    city = order["city"]
    delay_conditions = {"Rain", "Snow", "Extreme"}

    try:
        weather = await fetch_weather(session, city)

        if weather in delay_conditions:
            order["status"] = "Delayed"
            apology = generate_apology(order["customer"], city, weather)
            order["apology_message"] = apology
            logging.info(f"Order {order['order_id']} marked Delayed. Message: {apology}")
        else:
            order["status"] = "On Time"
            logging.info(f"Order {order['order_id']} is On Time.")

    except ValueError as e:
        # Log the error but do NOT crash — script continues with other orders
        logging.error(f"Skipping order {order['order_id']}: {e}")
        order["status"] = "Error - City Not Found"

    return order

# ── Step 4: Main function — runs everything concurrently ──────────────────────
async def main():
    # Load orders
    with open("orders.json", "r") as f:
        orders = json.load(f)

    async with aiohttp.ClientSession() as session:
        # Fire all API calls at the same time using asyncio.gather
        tasks = [process_order(session, order) for order in orders]
        updated_orders = await asyncio.gather(*tasks)

    # Save updated orders back to JSON
    with open("orders.json", "w") as f:
        json.dump(list(updated_orders), f, indent=2)

    logging.info("Done! orders.json has been updated.")

# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    asyncio.run(main())