import os
import requests
import hashlib
import sys

MODEL_URL = "https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin"
MODEL_DIR = "./models"
MODEL_PATH = os.path.join(MODEL_DIR, "lid.176.bin")

def download_file(url, path):
    print(f"Downloading {url} to {path}...")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    with open(path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print("Download complete.")

def main():
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)
        
    if os.path.exists(MODEL_PATH):
        print(f"Model already exists at {MODEL_PATH}")
        # Optional: Check size or hash to ensure integrity
        return
        
    try:
        download_file(MODEL_URL, MODEL_PATH)
    except Exception as e:
        print(f"Failed to download model: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
