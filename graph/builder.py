from langgraph.graph import StateGraph, START, END
from graph.state import TotalState
from graph.nodes import weather_node, news_node, stock_node, synthesizer_node

def get_graph_builder():
    """
    Constructs the StateGraph blueprint but DOES NOT compile it yet.
    We return the builder so main.py can add memory to it later.
    """
    # 1. Initialize Graph
    builder = StateGraph(TotalState)

    # 2. Add Nodes
    builder.add_node("weather_agent", weather_node)
    builder.add_node("news_agent", news_node)
    builder.add_node("stock_agent", stock_node)
    builder.add_node("synthesizer", synthesizer_node)

    # 3. Add Edges
    builder.add_edge(START, "weather_agent")
    builder.add_edge(START, "news_agent")
    builder.add_edge(START, "stock_agent")

    builder.add_edge("weather_agent", "synthesizer")
    builder.add_edge("news_agent", "synthesizer")
    builder.add_edge("stock_agent", "synthesizer")
    builder.add_edge("synthesizer", END)

    return builder