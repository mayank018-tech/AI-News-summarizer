import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from summarize import _compute_tf, _STOP

def generate_brief(text, max_words=40):
    """
    Generate an ultra-short summary (max 2 sentences, < 40 words).
    Preserves most important information based on TF-IDF scoring.
    """
    if not text or len(text.strip()) < 50:
        return text.strip()[:max_words * 5]
        
    try:
        sentences = sent_tokenize(text)
        if not sentences:
            return ""
            
        if len(sentences) <= 2:
            brief_text = " ".join(sentences)
        else:
            tf = _compute_tf(text)
            
            scores = []
            for i, sent in enumerate(sentences):
                # Ignore very short sentences
                if len(sent.split()) < 5:
                    continue
                    
                words = [w.lower() for w in word_tokenize(sent) if w.lower() not in _STOP and w.isalnum()]
                score = sum(tf.get(w, 0) for w in words)
                
                # Boost first sentence significantly (usually contains the core news)
                if i == 0:
                    score *= 2.0
                elif i == 1:
                    score *= 1.5
                    
                scores.append((i, score, sent))
                
            scores.sort(key=lambda x: x[1], reverse=True)
            top_sentences = scores[:2]
            top_sentences.sort(key=lambda x: x[0])
            
            brief_text = " ".join([sent for i, score, sent in top_sentences])
            
        # Ensure it's under 40 words
        words = brief_text.split()
        if len(words) > max_words:
            # Try just the first sentence if the combination is too long
            first_sent_words = sent_tokenize(brief_text)[0].split()
            if len(first_sent_words) <= max_words:
                brief_text = " ".join(first_sent_words)
            else:
                brief_text = " ".join(words[:max_words]) + "..."
                
        return brief_text
        
    except Exception as e:
        print(f"[Brief Generation Error] {e}")
        # Fallback to truncating the text directly
        words = text.split()
        return " ".join(words[:max_words]) + "..."
