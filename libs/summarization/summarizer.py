import re
from collections import Counter

def generate_summary(text, lang='en'):
    """
    Generate a simple extractive summary and bullet points.
    Returns (summary_text, summary_bullets_str).
    """
    if not text:
        return None, None
        
    # Simple sentence splitting (replace with more robust one if needed)
    # Using simple regex for splitting by .!?|
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!|\|)\s', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20] # Filter short noise
    
    if not sentences:
        return None, None
        
    # Word frequency map
    words = re.findall(r'\w+', text.lower())
    # remove simple stop words (very basic list)
    stop_words_en = {'the', 'is', 'at', 'which', 'on', 'and', 'a', 'an', 'in', 'to', 'of', 'for', 'it', 'with', 'as', 'was', 'date', 'image'}
    stop_words_bn = {'এবং', 'ও', 'কিন্তু', 'অথবা', 'জন্য', 'থেকে', 'করে', 'হয়', 'না', 'কি', 'কে', 'যে', 'এই', 'এক'}
    
    stop_words = stop_words_en if lang == 'en' else stop_words_bn
    words = [w for w in words if w not in stop_words]
    
    word_freq = Counter(words)
    max_freq = max(word_freq.values()) if word_freq else 1
    
    # Normalize freq
    for w in word_freq:
        word_freq[w] = word_freq[w] / max_freq
        
    # Score sentences
    sent_scores = {}
    for sent in sentences:
        score = 0
        sent_words = re.findall(r'\w+', sent.lower())
        if not sent_words:
            continue
            
        for w in sent_words:
            if w in word_freq:
                score += word_freq[w]
                
        # Normalize by length to avoid favouring long sentences too much
        sent_scores[sent] = score / (len(sent_words) + 1)
        
    # Get top N sentences (e.g. 3)
    import heapq
    top_sentences = heapq.nlargest(3, sent_scores, key=sent_scores.get)
    
    summary_text = " ".join(top_sentences)
    summary_bullets = "\n".join([f"- {s}" for s in top_sentences])
    
    return summary_text, summary_bullets
