import time
from services.celery_app import backfill_task
import sys

# Mock for Celery delay if we want to run inline, but here we can import the function directly 
# or use .delay() if we want to test the queue.
# Since we are in the API container, we can call the task directly or via Celery.
# To test full integration, we should probably trigger it via Celery but that requires a worker with the task code.

def verify_phase_13():
    print("Verifying Phase 13 (Backfill)...")
    
    # Target a sitemap (using a known structure or a small one)
    # Prothom Alo or Daily Star (Daily Star has standard sitemap.xml)
    target_url = "https://www.thedailystar.net/sitemap.xml" 
    source_name = "Daily Star Backfill"
    
    print(f"Triggering backfill for {source_name}...")
    try:
        # Triggering task asynchronously
        task = backfill_task.delay(target_url, source_name)
        print(f"Task dispatched: {task.id}")
        
        # Wait a bit? Or just verify it was sent.
        print("Task sent to Celery. Check worker logs for progress.")
        
    except Exception as e:
        print(f"[FAIL] Failed to trigger task: {e}")
        # Fallback: try calling function directly to verify logic (if import works)
        # Note: 'usp' might not be installed in API container if we didn't rebuild it. 
        # But we did `docker-compose up -d --build worker`. 
        # API container also needs rebuild to have `usp` if we run this script there.
        # Wait, I only rebuilt `worker`. I need to rebuild `api` too if I want to run this script or use the dependencies there.
        sys.exit(1)

    print("[SUCCESS] Phase 13 verification trigger passed.")

if __name__ == "__main__":
    verify_phase_13()
