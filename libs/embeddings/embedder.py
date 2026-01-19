from sentence_transformers import SentenceTransformer
import os

# Using a lightweight model for MVP
MODEL_NAME = 'all-MiniLM-L6-v2'
MODEL_PATH = os.path.join(os.path.dirname(__file__), '../../models/sentence-transformers')

_model = None

def get_model():
    global _model
    if _model is None:
        try:
            # We rely on sentence-transformers to handle caching usually,
            # but we can force a path if needed. For now let it cache in default location or set via env.
            # Docker volume for caching would be good: /app/models or /root/.cache
            print(f"Loading embedding model {MODEL_NAME}...")
            _model = SentenceTransformer(MODEL_NAME)
        except Exception as e:
            print(f"Error loading embedding model: {e}")
    return _model

def generate_embedding(text):
    """
    Generate 384-dim embedding for text.
    Returns list of floats.
    """
    model = get_model()
    if not model or not text:
        return None
        
    try:
        # Generate embedding
        embedding = model.encode(text)
        return embedding.tolist()
    except Exception as e:
        print(f"Embedding error: {e}")
        return None
