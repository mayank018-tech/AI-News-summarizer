import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

def _download_vader_lexicon():
    import os
    import shutil
    try:
        nltk.data.find('sentiment/vader_lexicon')
    except Exception:
        # Clean up corrupted files if present
        for path in nltk.data.path:
            try:
                target_dir = os.path.join(path, 'sentiment')
                zip_file = os.path.join(target_dir, "vader_lexicon.zip")
                extracted_folder = os.path.join(target_dir, "vader_lexicon")
                if os.path.exists(zip_file):
                    os.remove(zip_file)
                if os.path.exists(extracted_folder):
                    shutil.rmtree(extracted_folder)
            except Exception:
                pass
        try:
            nltk.download('vader_lexicon', quiet=True)
        except Exception:
            pass

_download_vader_lexicon()

def analyze_sentiment(text):
    """
    Analyzes the sentiment of the text using NLTK's VADER SentimentIntensityAnalyzer.
    Classifies the text as Positive, Neutral, or Negative and returns compound confidence scores.
    """
    default_result = {
        "label": "Neutral",
        "scores": {
            "pos": 0.0,
            "neu": 1.0,
            "neg": 0.0,
            "compound": 0.0
        }
    }

    if not text or not isinstance(text, str):
        return default_result

    try:
        sia = SentimentIntensityAnalyzer()
        scores = sia.polarity_scores(text)
        
        compound = scores.get('compound', 0.0)
        
        # Standard VADER compound score boundaries
        if compound >= 0.05:
            label = "Positive"
        elif compound <= -0.05:
            label = "Negative"
        else:
            label = "Neutral"

        return {
            "label": label,
            "scores": {
                "pos": round(scores.get('pos', 0.0), 3),
                "neu": round(scores.get('neu', 1.0), 3),
                "neg": round(scores.get('neg', 0.0), 3),
                "compound": round(compound, 3)
            }
        }
    except Exception:
        return default_result
