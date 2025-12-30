from graph.state import TotalState
from services import weather, news, stock

async def weather_node(state: TotalState):
    """Reads the topic and asks the Weather"""
    topic = state["topic"]
    result = await weather.get_weather(topic)
    return {"results": [result]}

async def news_node(state: TotalState):
    """Reads the topic and asks for the News"""
    topic = state["topic"]
    result = await news.get_news(topic)
    return {"results": [result]}

async def stock_node(state: TotalState):
    """Reads the topic and asks the Stock"""
    topic = state["topic"]
    result = await stock.get_stock_data(topic)
    return {"results": [result]}

def synthesizer_node(state: TotalState):
    """Runs ONLY after Weather, News, and Stocks are done.
    It will simply take the results and make a report for it"""
    results_list = state["results"]
    topic = state["topic"]

    report = f"\nINTELLIGENCE REPORT: '{topic.upper()}'\n"
    report += "=" * 50 + "\n"
    
    for info in results_list:
        report += f"{info}\n"
        report += "-" * 50 + "\n"
        
    return {"final_report": report}