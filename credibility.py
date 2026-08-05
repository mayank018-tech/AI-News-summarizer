import re
import spacy

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    import spacy.cli
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

TRUSTED_ORGS = {
    "reuters", "associated press", "bbc", "nytimes", "new york times", 
    "wall street journal", "wsj", "bloomberg", "the guardian", "washington post", 
    "mit", "stanford", "harvard", "nature", "science", "openai", "microsoft", 
    "google", "deepmind", "anthropic", "meta"
}

SENSATIONAL_WORDS = {
    "shocking", "mind-blowing", "insane", "you won't believe", "destroy", 
    "annihilate", "secret", "miracle", "hidden", "expose", "scandal", "panic", 
    "terrifying", "game-changer", "revolutionary", "magic", "outrageous", "bizarre"
}

UNSUPPORTED_PHRASES = {
    "some people say", "many believe", "critics say", "experts agree", 
    "it is said", "rumor has it", "allegedly", "reportedly", "people think"
}

def analyze_credibility(text):
    """
    Generate a credibility score between 0-100 based on heuristics.
    """
    if not text:
        return {"score": 0, "confidence": "Low", "reasons": ["No text provided"]}

    text_lower = text.lower()
    # Limit parsing to first 5000 characters to save time
    doc = nlp(text[:5000])

    score = 70  # Baseline score
    reasons = []

    # 1. Check for quotes
    quotes = re.findall(r'"([^"]*)"', text)
    if len(quotes) >= 2:
        score += 10
        reasons.append("✓ Includes direct quotations")
    elif len(quotes) == 0:
        score -= 5
        reasons.append("⚠ No direct quotations found")

    # 2. Check for trusted organizations
    orgs = [ent.text.lower() for ent in doc.ents if ent.label_ == "ORG"]
    found_trusted = [org for org in orgs if any(trusted in org for trusted in TRUSTED_ORGS)]
    if found_trusted:
        score += 15
        reasons.append("✓ Mentions trusted organizations or institutions")

    # 3. Check for dates and factual entities
    dates = [ent.text for ent in doc.ents if ent.label_ in ["DATE", "TIME", "PERCENT", "MONEY"]]
    if len(dates) >= 3:
        score += 10
        reasons.append("✓ Contains specific factual entities (dates/numbers)")
    else:
        score -= 5
        reasons.append("⚠ Lacks specific factual entities")

    # 4. Check for sensational words
    sensational_count = sum(1 for word in SENSATIONAL_WORDS if word in text_lower)
    if sensational_count == 0:
        score += 5
        reasons.append("✓ Neutral and professional language")
    elif sensational_count >= 3:
        score -= 15
        reasons.append(f"⚠ Uses {sensational_count} sensational or clickbait terms")
    else:
        score -= 5
        reasons.append("⚠ Uses some sensational language")

    # 5. Check for unsupported claims
    unsupported_count = sum(1 for phrase in UNSUPPORTED_PHRASES if phrase in text_lower)
    if unsupported_count > 0:
        score -= 10
        reasons.append(f"⚠ Contains {unsupported_count} unsupported statements (e.g. 'some people say')")

    # Cap score
    score = max(0, min(100, score))

    if score >= 80:
        confidence = "High"
    elif score >= 50:
        confidence = "Medium"
    else:
        confidence = "Low"

    # Limit reasons to max 5 to keep UI clean
    reasons = reasons[:5]

    return {
        "score": score,
        "confidence": confidence,
        "reasons": reasons
    }
