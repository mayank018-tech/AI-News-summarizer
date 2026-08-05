from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.tokenize import sent_tokenize
from preprocess import preprocess_text

def extract_keywords(text, top_n=10):
    """
    Extracts the top N most relevant keywords from the text using scikit-learn's TF-IDF Vectorizer.
    Treats individual sentences as the document corpus to evaluate term importance.
    """
    if not text or not isinstance(text, str):
        return []

    sentences = sent_tokenize(text)
    
    # Fallback to simple term frequency if the article is too short for TF-IDF
    if len(sentences) < 2:
        cleaned_text = preprocess_text(text)
        words = cleaned_text.split()
        # Get unique words sorted by count
        unique_words = sorted(list(set(words)), key=lambda w: words.count(w), reverse=True)
        return [w for w in unique_words if len(w) > 2][:top_n]

    # Clean and preprocess sentences
    preprocessed_corpus = []
    for sentence in sentences:
        cleaned_sent = preprocess_text(sentence)
        if cleaned_sent:
            preprocessed_corpus.append(cleaned_sent)

    if not preprocessed_corpus:
        return []

    # Calculate TF-IDF weights across sentences
    try:
        vectorizer = TfidfVectorizer(max_df=0.9, min_df=1)
        tfidf_matrix = vectorizer.fit_transform(preprocessed_corpus)
        
        # Sum TF-IDF weights for each word across all sentences
        feature_names = vectorizer.get_feature_names_out()
        scores = tfidf_matrix.sum(axis=0).A1
        
        # Zip features and scores, sort in descending order
        word_scores = list(zip(feature_names, scores))
        sorted_word_scores = sorted(word_scores, key=lambda x: x[1], reverse=True)
        
        # Filter out very short words
        keywords = [word for word, score in sorted_word_scores if len(word) > 2]
        return keywords[:top_n]
    except Exception:
        # Fallback to word counts on failure
        cleaned_text = preprocess_text(text)
        words = cleaned_text.split()
        unique_words = sorted(list(set(words)), key=lambda w: words.count(w), reverse=True)
        return [w for w in unique_words if len(w) > 2][:top_n]
