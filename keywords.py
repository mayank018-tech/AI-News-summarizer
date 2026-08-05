"""
keywords.py — Fast, Efficient Keyword Extractor
───────────────────────────────────────────────
Uses an efficient RAKE (Rapid Automatic Keyword Extraction) style logic 
combined with simple frequency scoring to extract multi-word and single-word 
keyphrases instantly without downloading heavy machine learning models.
"""
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

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

_STOP = set(stopwords.words("english"))
_STOP.update({
    "said", "say", "also", "would", "could", "may", "use", "used",
    "one", "two", "three", "new", "like", "however", "according",
    "across", "end", "expected", "early", "late", "within", "since",
    "make", "made", "way", "year", "years", "time", "part",
    "many", "much", "well", "still", "even", "just", "back", "last",
    "first", "second", "third", "next", "number", "known", "go",
})

def _tokenize_words(text: str) -> list:
    return [re.sub(r"[^a-z]", "", w.lower()) for w in word_tokenize(text)]

def _candidate_phrases(text: str) -> list:
    words = _tokenize_words(text)
    phrases = []
    current = []
    for w in words:
        if not w or len(w) < 2:
            if current:
                phrases.append(" ".join(current))
                current = []
            continue
        if w in _STOP or w.isdigit():
            if current:
                phrases.append(" ".join(current))
                current = []
        else:
            current.append(w)
    if current:
        phrases.append(" ".join(current))
    return [p for p in phrases if len(p) > 1]

def _word_scores(phrases: list) -> dict:
    freq = {}
    degree = {}
    for phrase in phrases:
        words = phrase.split()
        d = len(words) - 1
        for w in words:
            freq[w] = freq.get(w, 0) + 1
            degree[w] = degree.get(w, 0) + d
    return {w: (degree[w] + freq[w]) / freq[w] for w in freq}

def _phrase_score(phrase: str, word_scores: dict) -> float:
    return sum(word_scores.get(w, 0) for w in phrase.split())

def extract_keywords(text: str, top_n: int = 10) -> list:
    if not text or not isinstance(text, str):
        return []

    phrases = _candidate_phrases(text)
    if not phrases:
        return []

    w_scores = _word_scores(phrases)
    seen = set()
    ranked = []
    for phrase in phrases:
        if phrase in seen:
            continue
        seen.add(phrase)
        if len(phrase.split()) > 4:
            continue
        sc = _phrase_score(phrase, w_scores)
        ranked.append((phrase, sc))

    ranked.sort(key=lambda x: x[1], reverse=True)

    final = []
    for phrase, _ in ranked:
        if any(phrase in selected and phrase != selected for selected in final):
            continue
        final.append(phrase.title())
        if len(final) >= top_n:
            break

    return final
