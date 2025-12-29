import asyncio
import aiohttp
import os
from dotenv import load_dotenv

# --- Load Environment Variables from Global Path ---
# Using raw string (r"") to handle Windows backslashes correctly
env_path = r"C:\Users\KIIT\Desktop\Projects\LangGraph\.env"
load_dotenv(env_path)

async def get_weather(city: str) -> str:
    """
    Fetches weather.
    - If input looks like a stock ticker or 'General', returns a skip message.
    - Otherwise, assumes it is a city and tries to fetch weather.
    """
    # 1. Validation: Don't try to fetch weather for 'Tesla' or 'General'
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
                    
                    # --- Extract Data ---
                    temp = data["main"]["temp"]
                    desc = data["weather"][0]["description"]
                    name = data["name"]
                    
                    # --- NEW: Get Country Code ---
                    # The API returns 'sys': {'country': 'US', ...}
                    country = data["sys"].get("country", "Unknown")
                    
                    return f"Weather in {name}, {country}: {desc.capitalize()}, {temp}°C"
                
                elif response.status == 404:
                    return f"Weather: Bruhh you need to enter a valid city name instead of '{city}'"
                else:
                    return f"Weather Error: Status {response.status}"
    except Exception as e:
        return f"Connection Error: {e}"

# --- Interactive Loop ---

async def main():
    print("---------------------------------------------------------")
    print("Weather Agent Ready!")
    print(f"   (Loaded config from: {env_path})")
    print("   - Type a City Name (e.g., 'London', 'Mumbai').")
    print("   - Type 'General' (Tests the skip logic).")
    print("   - Type 'exit' to quit.")
    print("---------------------------------------------------------")

    while True:
        try:
            user_input = input("\nEnter Location: ").strip()
        except KeyboardInterrupt:
            break

        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Goodbye!")
            break

        if not user_input: continue

        print("   Checking forecast...")
        result = await get_weather(user_input)
        print(f"\n{result}")
        print("-" * 40)

# --- Entry Point ---
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass