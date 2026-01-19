import fasttext
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), '../../models/lid.176.bin')
# We expect models to be at project_root/models, so relative path from libs/language_detection is ../../models

_model = None

def get_model():
    global _model
    if _model is None:
        try:
            # Handle docker/local path differences
            # If running in docker, /app/models provided via volume
            # If local, ./models
            
            # Using absolute path logic might be safer
            possible_paths = [
                "/app/models/lid.176.bin",
                os.path.abspath(os.path.join(os.path.dirname(__file__), '../../models/lid.176.bin')),
                "models/lid.176.bin"
            ]
            
            model_file = None
            for p in possible_paths:
                if os.path.exists(p):
                    model_file = p
                    break
            
            if model_file:
                # Suppress warning
                fasttext.FastText.eprint = lambda x: None
                _model = fasttext.load_model(model_file)
            else:
                print(f"Warning: Language model not found in {possible_paths}")
        except Exception as e:
            print(f"Error loading language model: {e}")
    return _model

def detect_language(text):
    """
    Returns (lang_code, confidence).
    """
    model = get_model()
    if not model or not text:
        return None, 0.0
        
    try:
        # Replace newlines
        clean_text = text.replace('\n', ' ')
        predictions = model.predict(clean_text, k=1)
        
        # predictions = (('__label__en',), array([0.9]))
        label = predictions[0][0].replace('__label__', '')
        score = float(predictions[1][0])
        
        return label, score
    except Exception as e:
        print(f"Detection error: {e}")
        return None, 0.0
