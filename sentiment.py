"""
sentiment.py — Fast VADER Sentiment Analyzer
──────────────────────────────────────────
Uses NLTK's VADER (Valence Aware Dictionary and sEntiment Reasoner) 
to classify text into Positive/Negative/Neutral sentiment instantly.
"""

import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.tokenize import sent_tokenize

def _ensure_nltk():
    for resource, name in [
        ("sentiment/vader_lexicon.zip", "vader_lexicon"),
        ("tokenizers/punkt", "punkt"),
        ("tokenizers/punkt_tab", "punkt_tab")
    ]:
        try:
            nltk.data.find(resource)
        except LookupError:
            nltk.download(name, quiet=True)

_ensure_nltk()
_sia = None

def _get_sia():
    global _sia
    if _sia is None:
        _sia = SentimentIntensityAnalyzer()
    return _sia

def analyze_sentiment(text: str) -> dict:
    default = {
        "label": "Neutral",
        "scores": {"pos": 0.0, "neu": 1.0, "neg": 0.0, "compound": 0.0},
        "avg_compound": 0.0,
        "dominant_tone": "Insufficient text for analysis"
    }

    if not text or len(text.strip()) < 10:
        return default

    try:
        sia = _get_sia()
        sentences = sent_tokenize(text)
        
        compound_sum = 0.0
        pos_sum = 0.0
        neg_sum = 0.0
        neu_sum = 0.0
        count = 0
        
        for sent in sentences:
            if len(sent.split()) < 3:
                continue
            scores = sia.polarity_scores(sent)
            compound_sum += scores['compound']
            pos_sum += scores['pos']
            neg_sum += scores['neg']
            neu_sum += scores['neu']
            count += 1
            
        if count == 0:
            return default
            
        avg_compound = compound_sum / count
        avg_pos = pos_sum / count
        if avg_compound >= 0.05:
            final_label = "Positive"
            tone = "Generally positive language"
            pos_pct = 50.0 + (avg_compound * 40.0)
            neg_pct = (1.0 - avg_compound) * 5.0
            neu_pct = 100.0 - pos_pct - neg_pct
        elif avg_compound <= -0.05:
            final_label = "Negative"
            tone = "Generally negative language"
            neg_pct = 50.0 + (abs(avg_compound) * 40.0)
            pos_pct = (1.0 - abs(avg_compound)) * 5.0
            neu_pct = 100.0 - neg_pct - pos_pct
        else:
            final_label = "Neutral"
            tone = "Balanced tone or mostly objective reporting"
            neu_pct = 70.0 + (30.0 * (1.0 - abs(avg_compound)))
            pos_pct = (100.0 - neu_pct) / 2.0
            neg_pct = (100.0 - neu_pct) / 2.0

        return {
            "label": final_label,
            "scores": {
                "pos": round(pos_pct, 1),
                "neu": round(neu_pct, 1),
                "neg": round(neg_pct, 1),
                "compound": round(avg_compound, 3),
            },
            "avg_compound": round(avg_compound, 3),
            "dominant_tone": tone
        }

    except Exception as e:
        print(f"[Sentiment Error] {e}")
        return default
