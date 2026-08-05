import re
from sentiment import analyze_sentiment

MARKETING_WORDS = {
    "buy now", "click here", "subscribe", "limited time", "discount", "offer",
    "best in class", "leading provider", "innovative solution", "synergy",
    "exclusive", "premium", "guarantee", "risk-free", "act now", "don't miss out"
}

POLITICAL_WORDS = {
    "democrat", "republican", "conservative", "liberal", "senate", "congress",
    "parliament", "election", "vote", "campaign", "policy", "legislation",
    "government", "regulation", "lawmaker", "bipartisan", "partisan", "regime"
}

EMOTIONAL_WORDS = {
    "devastating", "heartbreaking", "thrilled", "outraged", "furious", 
    "miraculous", "horrific", "tragic", "wonderful", "amazing", "terrible",
    "disgusting", "triumph", "disaster", "catastrophe", "joy", "fear"
}

CLICKBAIT_WORDS = {
    "shocking", "mind-blowing", "you won't believe", "insane", "secret",
    "hidden", "expose", "scandal", "panic", "terrifying", "game-changer", 
    "revolutionary", "magic", "bizarre", "jaw-dropping", "unbelievable"
}

def _count_matches(text, word_set):
    count = 0
    for word in word_set:
        if word in text:
            count += 1
    return count

def _score_to_level(count, low_threshold=1, high_threshold=3):
    if count == 0:
        return "None"
    elif count <= low_threshold:
        return "Low"
    elif count < high_threshold:
        return "Medium"
    else:
        return "High"

def detect_bias(text):
    """
    Analyze the writing style to detect bias, subjectivity, and tone.
    """
    if not text:
        return {
            "objectivity_score": 0,
            "overall_bias": "Unknown",
            "categories": {},
            "explanation": "No text provided."
        }
        
    text_lower = text.lower()
    
    # 1. Count occurrences
    marketing_count = _count_matches(text_lower, MARKETING_WORDS)
    political_count = _count_matches(text_lower, POLITICAL_WORDS)
    emotional_count = _count_matches(text_lower, EMOTIONAL_WORDS)
    clickbait_count = _count_matches(text_lower, CLICKBAIT_WORDS)
    
    # 2. Get sentiment stats to help determine subjectivity
    # Extreme sentiment usually implies subjectivity
    sentiment_data = analyze_sentiment(text)
    compound = abs(sentiment_data.get('avg_compound', 0))
    
    # 3. Calculate Objectivity Score (0-100)
    # Start at 100, penalize for bias signals
    objectivity = 100
    objectivity -= (marketing_count * 5)
    objectivity -= (emotional_count * 5)
    objectivity -= (clickbait_count * 8)
    # High sentiment intensity (compound > 0.5) reduces objectivity
    if compound > 0.5:
        objectivity -= ((compound - 0.5) * 40)
        
    objectivity = max(0, min(100, int(objectivity)))
    
    # 4. Overall Bias Rating
    if objectivity >= 80:
        overall_bias = "Low"
        explanation = "The text appears objective, neutral, and balanced."
    elif objectivity >= 50:
        overall_bias = "Medium"
        explanation = "The text contains some subjective, emotional, or promotional language."
    else:
        overall_bias = "High"
        explanation = "The text is highly subjective and exhibits strong bias, emotion, or sensationalism."
        
    return {
        "objectivity_score": objectivity,
        "overall_bias": overall_bias,
        "categories": {
            "Marketing": _score_to_level(marketing_count),
            "Political": _score_to_level(political_count, 2, 5), # Politics is common in news, threshold is higher
            "Emotional": _score_to_level(emotional_count),
            "Sensational": _score_to_level(clickbait_count)
        },
        "explanation": explanation
    }
