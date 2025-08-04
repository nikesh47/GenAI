#Take user query
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings

client = OpenAI()
embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-large"
)

# vector DB

vector_db = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="learning_vectors",
    embedding=embedding_model
)


print("Welcome to the PDF AI Assistant! Type 'exit' or 'quit' to end the session.")

while True:
    query = input(">> ")
    if query.strip().lower() in ["exit", "quit"]:
        print("Goodbye!")
        break

    # Vector similatiry search in DB
    search_results = vector_db.similarity_search(query)

    context = "\n\n\n".join([
        f"Page Content: {result.page_content} \nPage Number: {result.metadata['page_label']} \nFile Location: {result.metadata['source']}"
        for result in search_results
    ])

    SYSTEM_PROMPT =f"""
    You are a helpfull AI Assistant who asnweres user query based on the available context
    retrieved from a PDF file along with page_contents and page number.

    You should only ans the user based on the following context and navigate the user
    to open the right page number to know more

    Context:
    {context}
    """

    chat_completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role":"system" , "content" : "SYSTEM_PROMPT"},
            {"role":"user" , "content" : query}
        ]
    )

    print(f"🤖:  {chat_completion.choices[0].message.content}")