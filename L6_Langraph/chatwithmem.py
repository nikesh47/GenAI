from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel
from typing import Literal

from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from typing import Annotated
from langchain.chat_models import init_chat_model
from langgraph.graph.message import add_messages
from langgraph.checkpoint.mongodb import MongoDBSaver


load_dotenv()


class State(TypedDict):
    messages: Annotated[list, add_messages]

# callin LLM with init_chat_model 
llm = init_chat_model(model_provider="openai", model="gpt-4.1")



def chat_node(state: State):
    print("⚠️ chat_node")
    response = llm.invoke(state["messages"])
    return {"messages": [response]}


graph_builder = StateGraph(State)

graph_builder.add_node("chat_node", chat_node)
graph_builder.add_edge(START, "chat_node")
graph_builder.add_edge("chat_node", END)


#graph = graph_builder.compile()

# Compiling the graph with checkpointer
def compile_graph_with_checkpointer(checkpointer):
    
    graph_with_chcekpointer = graph_builder.compile(checkpointer = checkpointer) # bhai dega graph with checkpointer
    return graph_with_chcekpointer



def main():
    # Initialize MongoDBSaver for checkpointing

    DB_URI = "mongodb://admin:admin@localhost:27017"
    config = {"configurable": {"thread_id": "1"}}
    # will connect to MongoDB at the specified URI
    with MongoDBSaver.from_conn_string(DB_URI) as mongo_checkpointer:
        # Compile the graph with the MongoDB checkpointer
        # This will return a graph that can be used to invoke the chat node
        graph_with_mongo = compile_graph_with_checkpointer(mongo_checkpointer)

        query = input("> ")
        # Invoke the graph with the user query
        # The invoke method will return a result that contains the messages
        # The result will be a dictionary with a "messages" key containing the chat messages
        # The config parameter is used to pass additional configuration to the graph
        # In this case, it is used to pass the thread_id
        result = graph_with_mongo.invoke({"messages": [ {"role": "user", "content": query} ]}, config)
        print(result)


main()
