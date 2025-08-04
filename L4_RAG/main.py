from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

from .server import app
import uvicorn


def main():
    uvicorn.run(app, port=8000, host="0.0.0.0")

main()