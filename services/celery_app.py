import os
from celery import Celery
from celery.schedules import crontab
from services.crawler.main import run_crawl
from services.processor.main import run_process

from libs.utils.config import get_redis_url

# Redis URL for broker and backend
REDIS_URL = get_redis_url()

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
    # Update status in Redis
    import redis
    r = redis.from_url(REDIS_URL)
    r.set("bciip:crawler_status", "running")
    r.set("bciip:last_run", run_crawl.__module__) # Just a dummy write, or use time
    
    try:
        run_crawl()
    finally:
        r.set("bciip:crawler_status", "idle")
        
    return "Crawl Completed"

@app.task(name='process_task', autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def process_task():
    print("Running Process Task...")
    run_process()
    return "Process Completed"

@app.task(name='backfill_task')
def backfill_task(url: str, source: str):
    print(f"Running Backfill Task for {source}...")
    from services.crawler.sitemap_fetcher import fetch_sitemap
    fetch_sitemap(url, source)
    return f"Backfill for {source} Completed"

# Periodic Schedule
app.conf.beat_schedule = {
    'crawl-every-10-mins': {
        'task': 'crawl_task',
        'schedule': crontab(minute='*/10'),
    },
    'process-every-5-mins': {
        'task': 'process_task',
        'schedule': crontab(minute='*/5'),
    },
}
