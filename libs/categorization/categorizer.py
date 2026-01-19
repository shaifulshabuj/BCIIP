
# Keywords for simple baseline categorization
# Expand these lists for better accuracy
KEYWORDS_EN = {
    "politics": ["election", "parliament", "government", "minister", "bnp", "awami league", "politics", "vote", "democracy"],
    "economy": ["economy", "bank", "finance", "stock", "market", "inflation", "gdp", "export", "import", "remittance"],
    "health": ["health", "hospital", "doctor", "disease", "covid", "medicine", "virus", "vaccine", "dengue"],
    "sports": ["cricket", "football", "match", "tournament", "player", "score", "stadium", "team"],
    "technology": ["technology", "digital", "internet", "software", "app", "startup", "robot", "ai"],
    "crime": ["crime", "police", "arrest", "murder", "court", "jail", "rab", "case"],
    "education": ["education", "school", "college", "university", "student", "teacher", "exam"],
    "climate": ["climate", "weather", "flood", "rain", "temperature", "cyclone", "environment"],
    "culture": ["culture", "movie", "song", "drama", "art", "book", "festival"],
    "religion": ["religion", "islam", "hindu", "muslim", "prayer", "mosque", "temple"]
}

KEYWORDS_BN = {
    "politics": ["নির্বাচন", "সংসদ", "সরকার", "মন্ত্রী", "বিএনপি", "আওয়ামী লীগ", "রাজনীতি", "ভোট", "গণতন্ত্র"],
    "economy": ["অর্থনীতি", "ব্যাংক", "শেয়ার", "বাজার", "মুদ্রাস্ফীতি", "জিডিপি", "রপ্তানি", "আমদানি", "রেমিট্যান্স"],
    "health": ["স্বাস্থ্য", "হাসপাতাল", "ডাক্তার", "রোগ", "করোনা", "ঔষধ", "ভাইরাস", "টিকা", "ডেঙ্গু"],
    "sports": ["ক্রিকেট", "ফুটবল", "খেলা", "টুর্নামেন্ট", "খেলোয়াড়", "স্কোর", "স্টেডিয়াম", "দল"],
    "technology": ["প্রযুক্তি", "ডিজিটাল", "ইন্টারনেট", "সফটওয়্যার", "অ্যাপ", "স্টার্টআপ", "রোবট", "এআই"],
    "crime": ["অপরাধ", "পুলিশ", "গ্রেপ্তার", "হত্যা", "আদালত", "কারাগার", "র‍্যাব", "মামলা"],
    "education": ["শিক্ষা", "স্কুল", "কলেজ", "বিশ্ববিদ্যালয়", "ছাত্র", "শিক্ষক", "পরীক্ষা"],
    "climate": ["জলবায়ু", "আবহাওয়া", "বন্যা", "বৃষ্টি", "তাপমাত্রা", "ঘূর্ণিঝড়", "পরিবেশ"],
    "culture": ["সংস্কৃতি", "সিনেমা", "গান", "নাটক", "শিল্প", "বই", "উৎসব"],
    "religion": ["ধর্ম", "ইসলাম", "হিন্দু", "মুসলিম", "নামাজ", "মসজিদ", "মন্দির"]
}

def categorize_text(text, lang='en'):
    """
    Categorize text based on keyword matching.
    Returns (topic, confidence).
    """
    if not text:
        return None, 0.0
        
    text_lower = text.lower()
    
    # Select dictionary based on language (default to mixed/both if unknown or other)
    # Actually, let's just use both to be safe against mixed content
    
    scores = {}
    
    # Process English keywords
    for topic, keywords in KEYWORDS_EN.items():
        count = sum(1 for k in keywords if k in text_lower)
        scores[topic] = scores.get(topic, 0) + count
        
    # Process Bangla keywords
    for topic, keywords in KEYWORDS_BN.items():
        count = sum(1 for k in keywords if k in text_lower)
        scores[topic] = scores.get(topic, 0) + count
        
    # Determine best match
    if not scores:
        return 'others', 0.0
        
    best_topic = max(scores, key=scores.get)
    max_score = scores[best_topic]
    
    # Simple confidence metric: score / total words (normalized) or just raw score cap?
    # Let's use a soft confidence relative to total keywords found
    total_matches = sum(scores.values())
    if total_matches == 0:
        return 'others', 0.0
        
    confidence = max_score / total_matches
    
    # Threshold
    if max_score == 0:
         return 'others', 0.0
         
    return best_topic, round(confidence, 2)
