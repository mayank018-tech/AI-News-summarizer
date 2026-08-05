import nltk
from nltk.tokenize import sent_tokenize
from preprocess import preprocess_text

def _download_sent_tokenizer():
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)

_download_sent_tokenizer()

def generate_summary(text, min_sentences=3, max_sentences=5):
    """
    Generates a concise 3-5 sentence summary of the text using frequency-based sentence scoring.
    """
    if not text or not isinstance(text, str):
        return "No text provided for summarization."

    sentences = sent_tokenize(text)
    # If the text is short, return it as-is
    if len(sentences) <= min_sentences:
        return text

    # Preprocess the entire text to determine word weights
    cleaned_text = preprocess_text(text)
    words = cleaned_text.split()

    if not words:
        return text[:300] + "..."

    # Calculate word frequency counts
    word_frequencies = {}
    for word in words:
        word_frequencies[word] = word_frequencies.get(word, 0) + 1

    # Normalize frequencies by scaling against the most frequent word
    max_freq = max(word_frequencies.values())
    for word in word_frequencies:
        word_frequencies[word] = word_frequencies[word] / max_freq

    # Score each sentence by summing the normalized frequency of its words
    sentence_scores = {}
    for index, sentence in enumerate(sentences):
        cleaned_sentence = preprocess_text(sentence)
        sentence_words = cleaned_sentence.split()

        score = 0
        for word in sentence_words:
            if word in word_frequencies:
                score += word_frequencies[word]
        
        # Adjust score slightly based on sentence length to avoid bias towards extremely long sentences
        if len(sentence_words) > 0:
            sentence_scores[index] = score / len(sentence_words)
        else:
            sentence_scores[index] = 0

    # Pick the top N sentences
    target_count = min(max_sentences, max(min_sentences, len(sentences) // 4))
    
    # Get indices of top sentences
    top_indices = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:target_count]
    
    # Sort indices so the summary sentences appear in chronological order
    top_indices.sort()

    summary = " ".join([sentences[idx].strip() for idx in top_indices])
    return summary
