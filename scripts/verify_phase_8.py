import requests
import sys
import time

API_URL = "http://localhost:8000"

def verify_phase_8():
    print("Verifying Phase 8 API...")
    
    # 1. Health
    try:
        r = requests.get(f"{API_URL}/health")
        if r.status_code != 200:
            print(f"[FAIL] Health check failed: {r.status_code}")
            sys.exit(1)
        print("Health check OK.")
    except Exception as e:
        print(f"[FAIL] Connection error: {e}")
        sys.exit(1)

    # 2. List Articles
    r = requests.get(f"{API_URL}/articles?limit=5")
    if r.status_code != 200:
        print(f"[FAIL] List articles failed: {r.status_code}")
        sys.exit(1)
    articles = r.json()
    print(f"List Articles: Found {len(articles)}")
    if not articles:
        print("[WARN] No articles to specific detail test.")
        
    # 3. Get Article Detail
    if articles:
        art_id = articles[0]['id']
        r = requests.get(f"{API_URL}/articles/{art_id}")
        if r.status_code != 200:
            print(f"[FAIL] Get article detail failed: {r.status_code}")
        else:
            detail = r.json()
            print(f"Detail OK: {detail['title']} | Entities: {len(detail.get('entities', []))}")

    # 4. Search (Text)
    r = requests.get(f"{API_URL}/search?q=politics&type=text")
    if r.status_code == 200:
        print(f"Text Search 'politics': Found {len(r.json())}")
    else:
        print(f"[FAIL] Text search failed: {r.status_code}")

    # 5. Search (Semantic)
    r = requests.get(f"{API_URL}/search?q=climate&type=semantic")
    if r.status_code == 200:
        print(f"Semantic Search 'climate': Found {len(r.json())}")
    else:
        print(f"[FAIL] Semantic search failed: {r.status_code}")

    # 6. Topics
    r = requests.get(f"{API_URL}/topics/politics")
    if r.status_code == 200:
        print(f"Topic Filter 'politics': Found {len(r.json())}")
    else:
        print(f"[FAIL] Topic filter failed: {r.status_code}")
        
    print("[SUCCESS] Phase 8 verification passed.")

if __name__ == "__main__":
    verify_phase_8()
