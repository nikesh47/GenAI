from dotenv import load_dotenv
load_dotenv()

from langchain_community.document_loaders import PyPDFLoader
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore

pdf_path = Path(__file__).parent / "nodejs.pdf"

loader = PyPDFLoader(file_path=pdf_path)
docs = loader.load() # retunrs pdf ( read pdf file)

# Chunking

text_splitter =RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200

)

splits_docs = text_splitter.split_documents(docs)
# Vector embedding
embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-large"

)

# Using [embedding model] create embedding of splits_docs and store in DB(Vector DB)
vector_store = QdrantVectorStore.from_documents(
    documents=splits_docs,
    url="http://localhost:6333",
    collection_name="learning_vectors",
    embedding=embedding_model
)

print("Indexing of Documents is done ..........")










