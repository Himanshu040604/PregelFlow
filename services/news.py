import asyncio
import aiohttp
import os
from dotenv import load_dotenv

env_path = r"C:\Users\KIIT\Desktop\Projects\LangGraph\.env"
load_dotenv(env_path)

async def get_news(topic: str) -> str:
    """how it get news. 
    If topic is 'General' or empty: it fetches the top headlines.
    Else it searches for specific articles about the topic"""
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        return "News Error: API Key missing."
    
    if not topic or topic.lower() == "general":
        #gets the top headlines for a generic overview
        url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}&pageSize=3"
        header_text = "Top global headlines"
    else:
        #gets the article related to the specific topic
        url = f"https://newsapi.org/v2/everything?q={topic}&apiKey={api_key}&pageSize=3"
        header_text = f"News about {topic}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                articles = data.get("articles", [])
                
                if not articles:
                    return f"No news found for '{topic}'."
                headlines = [f"- {a['title']} ({a['source']['name']})" for a in articles]
                return f"{header_text}:\n" + "\n".join(headlines)
            else:
                return f"News Error: API returned status {response.status}"
            