"""
run_tests.py — Simulates all weather conditions using mock_orders.json
and saves the results to test_results.json so you can see:
  - Which orders were Delayed / On Time / Error
  - The AI-generated apology messages for delayed orders
  - A pass/fail report for every test case

Run with: python run_tests.py
"""

import asyncio
import json
import os
import logging
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# ── Mock Gemini so we don't need a real API call for testing ──────────────────
def mock_generate_apology(customer_name, city, weather_condition):
    return (
        f"Hi {customer_name}, your order to {city} is delayed due to "
        f"{weather_condition}. We appreciate your patience!"
    )

# ── Simulate weather per order using _test_weather field ─────────────────────
async def mock_fetch_weather(session, city):
    """Returns mocked weather based on city, or raises for invalid cities."""
    mock_weather_map = {
        "New York": "Rain",
        "Mumbai": "Snow",
        "London": "Clear",
    }
    if city not in mock_weather_map:
        raise ValueError(f"City '{city}' not found.")
    return mock_weather_map[city]

# ── Process a single order (same logic as main.py) ───────────────────────────
async def process_order(session, order):
    city = order["city"]
    delay_conditions = {"Rain", "Snow", "Extreme"}

    try:
        weather = await mock_fetch_weather(session, city)

        if weather in delay_conditions:
            order["status"] = "Delayed"
            order["apology_message"] = mock_generate_apology(
                order["customer"], city, weather
            )
            order["weather_condition"] = weather
            logging.info(f"✅ Order {order['order_id']} → Delayed | {order['apology_message']}")
        else:
            order["status"] = "On Time"
            order["weather_condition"] = weather
            logging.info(f"✅ Order {order['order_id']} → On Time (weather: {weather})")

    except ValueError as e:
        order["status"] = "Error - City Not Found"
        order["weather_condition"] = "N/A"
        logging.error(f"❌ Order {order['order_id']} → {e}")

    return order

# ── Run test cases and validate results ──────────────────────────────────────
async def main():
    with open("mock_orders.json", "r") as f:
        orders = json.load(f)

    # Strip internal _test_weather field before processing
    for order in orders:
        order.pop("_test_weather", None)

    logging.info("\n──────────────── Running Mock Tests ────────────────")

    tasks = [process_order(None, order) for order in orders]
    results = list(await asyncio.gather(*tasks))

    # ── Define expected outcomes ──────────────────────────────────────────────
    expected = {
        "1001": {"status": "Delayed",               "has_apology": True},
        "1002": {"status": "Delayed",               "has_apology": True},
        "1003": {"status": "On Time",               "has_apology": False},
        "1004": {"status": "Error - City Not Found","has_apology": False},
    }

    # ── Validate and build test report ───────────────────────────────────────
    test_report = []
    all_passed = True

    for order in results:
        oid = order["order_id"]
        exp = expected[oid]

        status_pass  = order["status"] == exp["status"]
        apology_pass = ("apology_message" in order) == exp["has_apology"]
        passed       = status_pass and apology_pass
        all_passed   = all_passed and passed

        test_report.append({
            "order_id":         oid,
            "customer":         order["customer"],
            "city":             order["city"],
            "weather_condition":order.get("weather_condition", "N/A"),
            "status":           order["status"],
            "apology_message":  order.get("apology_message", "N/A — weather is clear, no delay"),
            "test_result": {
                "status_check":  "PASS ✅" if status_pass  else f"FAIL ❌ (expected {exp['status']})",
                "apology_check": "PASS ✅" if apology_pass else "FAIL ❌ (apology presence mismatch)",
                "overall":       "PASS ✅" if passed        else "FAIL ❌",
            }
        })

    # ── Save results ─────────────────────────────────────────────────────────
    output = {
        "summary": {
            "total_orders":  len(results),
            "delayed":       sum(1 for r in results if r["status"] == "Delayed"),
            "on_time":       sum(1 for r in results if r["status"] == "On Time"),
            "errors":        sum(1 for r in results if r["status"] == "Error - City Not Found"),
            "all_tests_passed": all_passed,
        },
        "orders": test_report,
    }

    with open("test_results.json", "w") as f:
        json.dump(output, f, indent=2)

    # ── Print summary ─────────────────────────────────────────────────────────
    print("\n──────────────── Test Summary ────────────────")
    for entry in test_report:
        print(
            f"  Order {entry['order_id']} | {entry['customer']:<20} | "
            f"Weather: {entry['weather_condition']:<8} | "
            f"Status: {entry['status']:<25} | {entry['test_result']['overall']}"
        )
    print(f"\n  Overall: {'ALL TESTS PASSED ✅' if all_passed else 'SOME TESTS FAILED ❌'}")
    print("  Results saved to → test_results.json")
    print("──────────────────────────────────────────────\n")

if __name__ == "__main__":
    asyncio.run(main())