# PregelFlow

A Python project that demonstrates a multi agent system using LangGraph, mostly done around internal Pregel architecture (Channels & Super-steps).

## Technologies & Architecture
- **LangGraph**: For building and executing the multi-agent graph.
- **Internal Pregel Architecture**: Utilizes concepts like channels and super-steps for parallel, distributed computation.
- **Asyncio & Aiohttp**: For asynchronous, concurrent API requests.
- **SQLite**: For persistent memory and checkpointing.
- **Dotenv**: For environment variable management.

## Project Idea: Real-time Multi-source Data Aggregator
This system pulls data from three different APIs (Weather, News, and Stock Prices) simultaneously.

### Pregel Implementation Details
- **Nodes as Actors**: Three independent nodes fetch data from their respective APIs.
- **Channels**: Topic channels broadcast the user's query to all fetching nodes at once.
- **Super-steps**: LangGraph executes all three fetches in a single parallel "super-step" before moving to the "Synthesizer" node in the next step.
- **Plan → Execute → Update Cycle**: The architecture visualizes this cycle, and you can inspect `graph.channels` to see how values flow through the internal Pregel machinery.

The system fetches and synthesizes information about a user-supplied topic from three sources: weather, news, and stock data, then generates a final intelligence report.

## Features
- Asynchronous, event-driven architecture
- Persistent memory using SQLite
- Modular design with clear separation of concerns
- Easily extensible for new data sources or agents

## Project Structure
```
main.py
/graph
    builder.py
    nodes.py
    state.py
/services
    weather.py
    news.py
    stock.py
/database
```

## Setup Instructions

### 1. Clone the Repository
```
git clone https://github.com/Himanshu040604/PregelFlow
```

### 2. Create a Virtual Environment
```
python -m venv venv
# Activate (Windows)
venv\Scripts\activate
# Activate (Linux/Mac)
source venv/bin/activate
```

### 3. Install Dependencies
```
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
Create a `.env` file in the project root with the following content:
```
OPENWEATHER_API_KEY=your_openweather_api_key
NEWS_API_KEY=your_newsapi_key
STOCK_API_KEY=your_alphavantage_api_key
```

#### Where to Get Your API Keys
- **OpenWeatherMap**: [https://openweathermap.org/api](https://openweathermap.org/api)
- **NewsAPI**: [https://newsapi.org/](https://newsapi.org/)
- **Alpha Vantage (Stocks)**: [https://www.alphavantage.co/support/#api-key](https://www.alphavantage.co/support/#api-key)

### 5. Run the Application
```
python main.py
```

## Usage
- Enter a topic (e.g., a city name, company, or keyword) when prompted.
- Type `exit` to quit the application.

## Extending the System
- Add new agents by creating new service modules and registering them in `graph/nodes.py` and `graph/builder.py`.
- The system is designed for easy integration of additional data sources.

## License
MIT License

---

**Note:** Ensure your API keys are kept private and not shared publicly.
