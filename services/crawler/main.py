from services.crawler.rss_fetcher import fetch_and_process_feed
import time

SOURCES = [
    # Major Bangladesh English Newspapers
    ("Prothom Alo", "https://www.prothomalo.com/feed"),
    ("The Daily Star", "https://www.thedailystar.net/rss.xml"),
    ("Dhaka Tribune", "https://www.dhakatribune.com/feed"),
    ("New Age Bangladesh", "https://www.newagebd.net/rss"),
    ("The Business Standard", "https://www.tbsnews.net/feed"),
    ("The Financial Express", "https://thefinancialexpress.com.bd/feed"),
    ("United News of Bangladesh", "https://unb.com.bd/feed"),
    
    # Bangla News
    ("Kaler Kantho", "https://www.kalerkantho.com/rss.xml"),
    ("Jugantor", "https://www.jugantor.com/feed/rss.xml"),
    ("Samakal", "https://samakal.com/feed"),
    ("Ittefaq", "https://www.ittefaq.com.bd/rss.xml"),
    
    # Specialized/Regional
    ("Dhaka Post", "https://www.dhakapost.com/rss.xml"),
    ("Bangladesh Post", "https://bangladeshpost.net/feed"),
    ("Bangla Tribune", "https://www.banglatribune.com/rss.xml"),
    
    # International (South Asia focus)
    ("Al Jazeera", "https://www.aljazeera.com/xml/rss/all.xml"),
    ("BBC News", "https://feeds.bbci.co.uk/news/rss.xml"),
    ("Reuters", "https://www.reutersagency.com/feed/"),
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
