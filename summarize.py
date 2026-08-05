"""
summarize.py — Fast TF-IDF Extractive Summarization
───────────────────────────────────────────────────
Uses a lightweight TF-IDF and sentence position scoring approach 
to extract the most important sentences instantly, avoiding heavy 
transformer models.
"""
import math
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import string

def _ensure_nltk():
    for resource, name in [
        ("tokenizers/punkt", "punkt"),
        ("tokenizers/punkt_tab", "punkt_tab"),
        ("corpora/stopwords", "stopwords"),
    ]:
        try:
            nltk.data.find(resource)
        except LookupError:
            nltk.download(name, quiet=True)

_ensure_nltk()
_STOP = set(stopwords.words('english'))

def _compute_tf(text: str) -> dict:
    words = [w.lower() for w in word_tokenize(text) if w.lower() not in _STOP and w.isalnum()]
    tf = {}
    for w in words:
        tf[w] = tf.get(w, 0) + 1
    total = len(words)
    if total > 0:
        for w in tf:
            tf[w] = tf[w] / total
    return tf

def generate_summary(text: str, max_sentences: int = 3) -> str:
    if not text or len(text.strip()) < 50:
        return text.strip()
    
    try:
        sentences = sent_tokenize(text)
        if len(sentences) <= max_sentences:
            return text

        tf = _compute_tf(text)
        
        scores = []
        for i, sent in enumerate(sentences):
            words = [w.lower() for w in word_tokenize(sent) if w.lower() not in _STOP and w.isalnum()]
            score = sum(tf.get(w, 0) for w in words)
            
            # Boost first few sentences (Inverted pyramid for news)
            if i < 2:
                score *= 1.5
                
            scores.append((i, score, sent))
            
        scores.sort(key=lambda x: x[1], reverse=True)
        top_sentences = scores[:max_sentences]
        top_sentences.sort(key=lambda x: x[0])
        
        return "\n".join([f"• {sent.strip()}" for i, score, sent in top_sentences])
    except Exception as e:
        print(f"[Summarization Error] {e}")
        return text[:500] + "..."
