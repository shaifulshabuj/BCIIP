import requests
import sys
import time

FRONTEND_URL = "http://frontend:3000"

def verify_phase_11():
    print("Verifying Phase 11 (PWA Frontend)...")
    
    # 1. Check Frontend Availability
    print("Checking Frontend Service...", end=" ")
    try:
        r = requests.get(FRONTEND_URL, timeout=5)
        if r.status_code == 200:
            print("[OK]")
        else:
            print(f"[FAIL] Status: {r.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"[FAIL] Connection error: {e}")
        sys.exit(1)

    # 2. Check Manifest (PWA)
    print("Checking Manifest...", end=" ")
    try:
        # Vite PWA plugin generates manifest.webmanifest or manifest.json
        # Configuration in vite.config.js usually puts it at root or /manifest.webmanifest
        # Check standard paths
        manifest_url = f"{FRONTEND_URL}/manifest.webmanifest"
        r = requests.get(manifest_url, timeout=2)
        if r.status_code == 200:
            print("[OK] (manifest.webmanifest)")
        else:
             # Try /manifest.json just in case default changed
            manifest_url = f"{FRONTEND_URL}/manifest.json"
            r = requests.get(manifest_url, timeout=2)
            if r.status_code == 200:
                 print("[OK] (manifest.json)")
            else:
                 print(f"[FAIL] Manifest not found at {manifest_url} or .webmanifest")
                 # Not critical for basic UI but critical for PWA requirement
                 sys.exit(1)
                 
    except Exception as e:
        print(f"[FAIL] Error checking manifest: {e}")
        sys.exit(1)

    print("[SUCCESS] Phase 11 verification passed.")

if __name__ == "__main__":
    verify_phase_11()
