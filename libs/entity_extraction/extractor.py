import re

# Simple regex-based entity extraction
# In a real system, we'd use SpaCy or a large NER model.
# Here we use basic heuristics for MVP.

PATTERNS_EN = {
    "PERSON": [
        r"Prime Minister [A-Z][a-z]+ [A-Z][a-z]+",
        r"President [A-Z][a-z]+ [A-Z][a-z]+",
        r"Dr\. [A-Z][a-z]+ [A-Z][a-z]+",
        r"Mr\. [A-Z][a-z]+",
        r"Mrs\. [A-Z][a-z]+"
    ],
    "ORG": [
        r"Awami League",
        r"BNP",
        r"United Nations",
        r"World Bank",
        r"IMF",
        r"Supreme Court",
        r"Rapid Action Battalion",
        r"RAB"
    ],
    "LOC": [
        r"Dhaka",
        r"Chittagong",
        r"Sylhet",
        r"Bangladesh",
        r"India",
        r"Myanmar",
        r"Cox's Bazar"
    ]
}

PATTERNS_BN = {
    "PERSON": [
        r"প্রধানমন্ত্রী [^\s]+ [^\s]+",
        r"ডাঃ [^\s]+",
        r"জনাব [^\s]+",
        r"বেগম [^\s]+"
    ],
    "ORG": [
        r"আওয়ামী লীগ",
        r"বিএনপি",
        r"র‍্যাব",
        r"পুলিশ",
        r"সুপ্রিম কোর্ট",
        r"জাতিসংঘ"
    ],
    "LOC": [
        r"ঢাকা",
        r"চট্টগ্রাম",
        r"সিলেট",
        r"বাংলাদেশ",
        r"ভারত",
        r"মিয়ানমার",
        r"কক্সবাজার"
    ]
}

def extract_entities(text, lang='en'):
    """
    Extract entities from text.
    Returns list of (type, value).
    """
    if not text:
        return []
        
    entities = set()
    
    patterns = PATTERNS_EN if lang == 'en' else PATTERNS_BN
    
    # Regex extraction
    for ent_type, regex_list in patterns.items():
        for pattern in regex_list:
            matches = re.findall(pattern, text)
            for match in matches:
                if len(match) > 2: # Ignore noise
                    entities.add((ent_type, match.strip()))
                    
    # Keyword/Gazetteer lookup (for simple exact matches logic usually better)
    # The arrays above act as both regex and exact match if simplified.
    
    return list(entities)
