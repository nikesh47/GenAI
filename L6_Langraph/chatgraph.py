from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel
from typing import Literal

from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from typing import Annotated
from langchain.chat_models import init_chat_model
from langgraph.graph.message import add_messages

load_dotenv()


class State(TypedDict):
    messages: Annotated[list, add_messages]
    # Annotation helps to add messages to the state in a structured way until the graph is compiled( end)



llm = init_chat_model(model_provider="openai", model="gpt-4.1")


#Single Node -- It doesnot have memory so do not remember previous messages
# At the end of graph all states are deleted

def chat_node(state: State):
    print("⚠️ chat_node")
    response = llm.invoke(state["messages"])
    return {"messages": [response]}


graph_builder = StateGraph(State)

graph_builder.add_node("chat_node", chat_node)
graph_builder.add_edge(START, "chat_node")
graph_builder.add_edge("chat_node", END)


graph = graph_builder.compile()


def main():
    query = input("> ")

    result = graph.invoke({"messages": [ {"role": "user", "content": query} ]})
    print(result)


main()
