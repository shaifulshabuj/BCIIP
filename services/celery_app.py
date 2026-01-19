import os
from celery import Celery
from celery.schedules import crontab
from services.crawler.main import run_crawl
from services.processor.main import run_process

# Redis URL for broker and backend
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

app = Celery('bciip', broker=REDIS_URL, backend=REDIS_URL)

app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Dhaka', # Or UTC
    enable_utc=True,
    # Worker settings
    worker_concurrency=2,
)

@app.task(name='crawl_task')
def crawl_task():
    print("Running Crawl Task...")
    run_crawl()
    return "Crawl Completed"

@app.task(name='process_task', autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def process_task():
    print("Running Process Task...")
    run_process()
    return "Process Completed"

# Periodic Schedule
app.conf.beat_schedule = {
    'crawl-every-30-mins': {
        'task': 'crawl_task',
        'schedule': crontab(minute='*/30'),
    },
    'process-every-5-mins': {
        'task': 'process_task',
        'schedule': crontab(minute='*/5'),
    },
}
