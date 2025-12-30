import asyncio
import aiohttp
import os
from pathlib import Path  # Import pathlib
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
env_path = BASE_DIR / ".env"

load_dotenv(env_path)

async def get_weather(city: str) -> str:
    """
    Fetches weather.
    - If input looks like a stock ticker or 'General', returns a skip message.
    - Otherwise, assumes it is a city and tries to fetch weather.
    """
    if not city or city.lower() == "general" or "." in city or len(city) <= 2:
        return "Weather: N/A (Global/Stock Context)"

    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return "Weather Error: API Key missing. Please check your .env file."

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    temp = data["main"]["temp"]
                    desc = data["weather"][0]["description"]
                    name = data["name"]
                    
                   
                    country = data["sys"].get("country", "Unknown")
                    
                    return f"Weather in {name}, {country}: {desc.capitalize()}, {temp}°C"
                
                elif response.status == 404:
                    return f"Weather: Bruhh you need to enter a valid city name instead of '{city}'"
                else:
                    return f"Weather Error: Status {response.status}"
    except Exception as e:
        return f"Connection Error: {e}"
