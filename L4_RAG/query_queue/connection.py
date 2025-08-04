from redis import Redis
from rq import Queue

queue = Queue(connection=Redis(host="localhost", port=6379))  # Adjust host and port as needed







