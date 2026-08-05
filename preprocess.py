import string
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download required NLTK datasets with self-healing for corrupted files
def _download_nltk_data():
    import os
    import shutil
    resources = {
        'tokenizers/punkt': 'punkt',
        'tokenizers/punkt_tab': 'punkt_tab',
        'corpora/stopwords': 'stopwords',
        'corpora/wordnet': 'wordnet',
        'corpora/omw-1.4': 'omw-1.4'
    }
    for resource_path, download_name in resources.items():
        try:
            nltk.data.find(resource_path)
        except Exception:
            # Clean up corrupted zip/directory if find fails
            for path in nltk.data.path:
                try:
                    # check for the directory or zip file
                    target_dir = os.path.join(path, os.path.dirname(resource_path))
                    base_name = os.path.basename(resource_path)
                    
                    zip_file = os.path.join(target_dir, base_name + ".zip")
                    extracted_folder = os.path.join(target_dir, base_name)
                    
                    if os.path.exists(zip_file):
                        os.remove(zip_file)
                    if os.path.exists(extracted_folder):
                        if os.path.isdir(extracted_folder):
                            shutil.rmtree(extracted_folder)
                        else:
                            os.remove(extracted_folder)
                except Exception:
                    pass
            
            # Re-download the resource
            try:
                nltk.download(download_name, quiet=True)
            except Exception:
                pass

_download_nltk_data()

def preprocess_text(text):
    """
    Cleans the input text by:
    - Converting to lowercase
    - Tokenizing
    - Removing punctuation & special characters
    - Removing stop words
    - Lemmatizing tokens
    """
    if not text or not isinstance(text, str):
        return ""

    # Convert to lowercase
    text = text.lower()

    # Tokenize
    tokens = word_tokenize(text)

    # Load stop words & lemmatizer
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()

    cleaned_tokens = []
    for token in tokens:
        # Remove punctuation characters
        cleaned_token = token.translate(str.maketrans('', '', string.punctuation)).strip()
        if cleaned_token and cleaned_token not in stop_words and not cleaned_token.isdigit():
            # Lemmatize token
            lemma = lemmatizer.lemmatize(cleaned_token)
            cleaned_tokens.append(lemma)

    return " ".join(cleaned_tokens)
