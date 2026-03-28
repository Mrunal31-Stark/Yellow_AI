// server.js — tiny Express server
// Reads API keys from .env and proxies all external API calls
// Run: node server.js  →  open http://localhost:3000

const express = require("express");
const path    = require("path");
const fetch   = require("node-fetch");
require("dotenv").config();

const app  = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(express.static(path.join(__dirname)));  // serves index.html

// ── Route 1: Proxy weather fetch ───────────────────────────────────────────────
// Frontend calls /api/weather?city=London  →  server calls OpenWeatherMap with real key
app.get("/api/weather", async (req, res) => {
  const { city } = req.query;
  if (!city) return res.status(400).json({ error: "city is required" });

  try {
    const url  = `https://api.openweathermap.org/data/2.5/weather?q=${encodeURIComponent(city)}&appid=${process.env.OPENWEATHER_API_KEY}`;
    const resp = await fetch(url);
    const data = await resp.json();

    if (!resp.ok) {
      return res.status(resp.status).json({ error: data.message || "City not found" });
    }

    res.json({ weather: data.weather[0].main });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ── Route 2: Proxy Gemini apology generation ──────────────────────────────────
// Frontend calls POST /api/apology  →  server calls Gemini with real key
app.post("/api/apology", async (req, res) => {
  const { customerName, city, weatherCondition } = req.body;
  if (!customerName || !city || !weatherCondition) {
    return res.status(400).json({ error: "customerName, city, weatherCondition required" });
  }

  const prompt = `Write a short, warm apology message for a customer whose delivery is delayed due to weather. Customer name: ${customerName}. City: ${city}. Weather condition: ${weatherCondition}. Keep it under 2 sentences and start with 'Hi ${customerName},'.`;

  try {
    const resp = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${process.env.GEMINI_API_KEY}`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ contents: [{ parts: [{ text: prompt }] }] }),
      }
    );
    const data = await resp.json();
    const msg  = data.candidates?.[0]?.content?.parts?.[0]?.text?.trim()
      || `Hi ${customerName}, your order to ${city} is delayed due to ${weatherCondition}. We appreciate your patience!`;

    res.json({ apology: msg });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.listen(PORT, () => {
  console.log(`\n  WeatherGate running at → http://localhost:${PORT}`);
  console.log(`  API keys loaded from   → .env\n`);
});