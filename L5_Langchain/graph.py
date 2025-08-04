from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel
from typing import Literal

from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict




load_dotenv()
client = OpenAI()

class ClassifyMessage(BaseModel):
    is_coding_question: bool

class CodingValidation(BaseModel):
    accuracy: str



class State(TypedDict):
    """
    A state in the graph.
    """
    user_query: str
    llm_result: str | None
    accuracy: str | None
    is_coding_question: bool | None

def classify_message(state: State):
    print("⚠️ classify_message")
    query = state["user_query"]

    SYSTEM_PROMPT = """
    You are an AI assistant. Your job is to detect if the user's query is
    related to coding question or not.
    Return the response in specified JSON boolean only.
    """
    # Use the OpenAI client to classify the message with Structured output / Response 
    # Using Pydantic for structured output
    response = client.beta.chat.completions.parse(
        model = "gpt-4.1-nano",
        response_format=ClassifyMessage,
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query}
        ]

    )

    is_coding_question = response.choices[0].message.parsed.is_coding_question
    state["is_coding_question"] = is_coding_question

    return state


# Routing Node ( if is_coding_question is True, route to gpt-4.1, else route to gpt-4.1-nano)

def route_query(state: State) -> Literal["general_query", "coding_query"]:
    print("⚠️ route_query")
    is_coding = state["is_coding_question"]

    if is_coding:
        return "coding_query"
    
    return "general_query"



    


def general_query(state: State):
    print("⚠️ general_query")
    
    query = state["user_query"]

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages = [
            {"role": "system", "content": query}
        ]
    )

    state["llm_result"] = response.choices[0].message.content
    return state

            


def coding_query(state: State):
    print("⚠️ coding_query")
    
    query = state["user_query"]

    SYSTEM_PROMPT = """    You are an AI assistant. Your job is to answer coding questions."""

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query}
        ]
    ) 
    state["llm_result"] = response.choices[0].message.content
    return state



def coding_validation(state: State):
    print("⚠️ coding_validatio_query")
    query = state["user_query"]
    llm_code = state["llm_result"]

    SYSTEM_PROMPT = f"""
        You are expert in calculating accuracy of the code according to the question.
        Return the percentage of accuracy
        
        User Query: {query}
        Code: {llm_code}
    """

    response = client.beta.chat.completions.parse(
        model = "gpt-4.1",
        response_format=CodingValidation,
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query}
        ]
    )

    state["accuracy"] = response.choices[0].message.parsed.accuracy
    return state




# Define the graph builder

graph_builder = StateGraph(State)

graph_builder.add_node("classify_message", classify_message)

graph_builder.add_node("route_query", route_query)
graph_builder.add_node("general_query", general_query)
graph_builder.add_node("coding_query", coding_query)
graph_builder.add_node("coding_validation", coding_validation)

graph_builder.add_edge(START, "classify_message")
graph_builder.add_conditional_edges("classify_message", route_query)

graph_builder.add_edge("general_query", END)

graph_builder.add_edge("coding_query", "coding_validation")
graph_builder.add_edge("coding_validation", END)


graph = graph_builder.compile()


def main():

    user = input(">")

    _state: State = {
        "user_query": user,
        "llm_result": None,
        "accuracy": None,
        "is_coding_question": False

    }

    # response = graph.invoke(_state)

    # print("LLM Result:", response)

    #Streaming the graph
    for event in graph.stream(_state):
        print("Event:", event)    


main()







