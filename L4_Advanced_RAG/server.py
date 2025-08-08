from fastapi import FastAPI, Query, Path
from .query_queue.connection import queue
from .query_queue.worker import process_query1




app = FastAPI()

@app.get("/")
def root():
    return {"status": "Server is up and running"}


@app.post("/chat")
def chat(
    query: str = Query(..., description="Chat Message")
):
    # Queue the message (query)
   job = queue.enqueue(process_query1, query)

    # Acknowledge the user , job received
   return {"status": "queued", "job_id": job.id}

@app.get("/result/{job_id}")
def get_result(
    job_id: str = Path(..., description="Job ID")
):
    job = queue.fetch_job(job_id)
    result = job.return_value()

    return {"result": result}