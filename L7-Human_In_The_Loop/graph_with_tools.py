# We design a simple chatbot using LangGraph and LangChain
# The chatbot can answer questions about the weather and perform simple arithmetic operations

# Here We learn Tool Binding and Hybrid Workflow 

from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
import requests

#to import tools
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition




from dotenv import load_dotenv
load_dotenv()

@tool()
def get_weather(city: str):
    """    Takes a city name as an input and returns the current weather for the city
    """

    url = f"https://wttr.in/{city}?format=%C+%t"
    response = requests.get(url)

    if response.status_code == 200:
        return f"The weather of {city} is {response.text}"
    
    return "Something went wrong"

@tool()
def add_num(a: int, b: int) -> int:
    """Adds two numbers."""
    return a + b




tools= [get_weather, add_num]


class State(TypedDict):
    messages: Annotated[list, add_messages]


# callin LLM with init_chat_model 
llm = init_chat_model(model_provider="openai", model="gpt-4.1")

# letting llm know about the tools
llm_with_tools = llm.bind_tools(tools)

def chat_bot_node(state:State):
    messages = llm_with_tools.invoke(state["messages"])
    return {"messages": [messages]}

tools_node = ToolNode(tools = tools)


graph_builder = StateGraph(State)

graph_builder.add_node("chat_bot_node", chat_bot_node)
graph_builder.add_node("tools", tools_node)
graph_builder.add_edge(START, "chat_bot_node")

graph_builder.add_conditional_edges(
    "chat_bot_node",
    tools_condition,
)

graph_builder.add_edge("tools", "chat_bot_node")

# graph_builder.add_edge("chat_bot_node", END)

graph = graph_builder.compile()


def main():
    query = input("> ")

    state = State(
        messages=[{"role": "user", "content": query}]
    )

    for event in graph.stream(state, stream_mode ="values"):
        if "messages" in event:
            event["messages"][-1].pretty_print()




main()