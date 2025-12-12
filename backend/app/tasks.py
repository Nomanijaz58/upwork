import os
from celery import Celery
from time import sleep

celery = Celery(
    "tasks",
    broker=os.getenv("REDIS_URL"),
    backend=os.getenv("REDIS_URL")
)

@celery.task(bind=True, max_retries=3)
def generate_proposal(self, job_id: int):
    # Demo: replace with actual OpenAI API call
    print(f"[Celery] Generating proposal for job_id={job_id}")
    sleep(2)
    result = {"proposal": f"Sample proposal for job {job_id}"}
    print(f"[Celery] Done: {result}")
    return result
