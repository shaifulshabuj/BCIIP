from services.crawler.rss_fetcher import fetch_and_process_feed
import time

SOURCES = [
    ("Prothom Alo", "https://www.prothomalo.com/feed"),
    ("The Daily Star", "https://www.thedailystar.net/rss.xml"),
]

def run_crawl():
    print("Starting BCIIP Crawler Phase 1...")
    
    for name, url in SOURCES:
        try:
            fetch_and_process_feed(name, url)
        except Exception as e:
            print(f"Failed to crawl {name}: {e}")
            
    print("Crawl cycle complete.")

if __name__ == "__main__":
    run_crawl()
