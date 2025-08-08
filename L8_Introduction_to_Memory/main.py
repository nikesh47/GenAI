from dotenv import load_dotenv
from openai import OpenAI
from mem0 import Memory

import os
import json

load_dotenv()

OPEN_API_KEY = os.getenv("OPEN_API_KEY")
client = OpenAI()

#Configuration for mem0
config ={
    "version":"v1.1",
    # Vector Embedding
    "embedder": {
        "provider": "openai",
        "config": {
            "api_key": OPEN_API_KEY,
            "model": "text-embedding-3-small"
        }

    },
    # LLM to use 
    "llm": {"provider": "openai", "config": {"api_key": OPEN_API_KEY, "model": "gpt-4.1"}},
    # Databse to store the vector-embeddings
    "vector_store" : {
        "provider":"qdrant",
        "config": {
            "host":"localhost",
            "port": "6333"

        }
    },

    # Database to store the memories ( Neo4j)
    "graph_store":{
         "provider": "neo4j",
         "config": {
              "url": "bolt://localhost:7687",
              "username": "neo4j",
              "password": "P@ssw0rd2025"


         }
    }

}

# Mem0 client intialization
mem_client = Memory.from_config(config)



# ChatApp
def chat():
    while True:
        user_input = input(">> ")

        if user_input.strip().lower() in ["exit", "quit", "Bye"]:
                print("Goodbye!")
                break

        # to get all memories 
        # all_memories = mem_client.get_all(user_id = "User1")
        # Not a good idea as it can take to out-of-context

        revelant_memories = mem_client.search(query= user_input,user_id = "User1")


        memories = [f"ID: {mem.get("id")} Memory: {mem.get("memory")}" for mem in revelant_memories.get("results")]
        # We can enter user memeories into the System Prompt


        SYSTEM_PROMPT = f"""
            You are an memeory aware assistant which responds to user with context.
            You are given with past memories and facts about the user.
            
            Memory of the user:
            {json.dumps(memories)}


            """

        result = client.chat.completions.create(
            model = "gpt-4.1",
            messages = [
                {"role":"system", "content":SYSTEM_PROMPT},
                {"role":"user", "content":user_input}]
        )

        print(f"{result.choices[0].message.content}")

        # Adding messages to the memory
        mem_client.add([
            {"role":"user", "content":user_input},
            {"role":"assistant", "content":result.choices[0].message.content}
        ], user_id = "User1")  # -> user_id like a thread_id, can be number but its string usualy


chat()