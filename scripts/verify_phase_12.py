import requests
import sys

API_URL = "http://localhost:8000"

def verify_phase_12():
    print("Verifying Phase 12 (Realtime Status)...")
    
    # 1. Check Status Endpoint
    print("Checking /status endpoint...", end=" ")
    try:
        r = requests.get(f"{API_URL}/status", timeout=5)
        if r.status_code == 200:
            data = r.json()
            # Check structure
            if "status" in data and "article_count" in data and "timestamp" in data:
                print(f"[OK] Status: {data['status']}, Articles: {data['article_count']}")
            else:
                 print(f"[FAIL] Invalid response structure: {data}")
                 sys.exit(1)
        else:
            print(f"[FAIL] HTTP {r.status_code}")
            sys.exit(1)
            
    except Exception as e:
        print(f"[FAIL] Connection error: {e}")
        sys.exit(1)

    print("[SUCCESS] Phase 12 verification passed.")

if __name__ == "__main__":
    verify_phase_12()
