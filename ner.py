import spacy
import spacy.cli

nlp = None

def _load_spacy_model():
    global nlp
    if nlp is not None:
        return nlp
    
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        # Download the model dynamically if it is not present
        try:
            spacy.cli.download("en_core_web_sm")
            nlp = spacy.load("en_core_web_sm")
        except Exception:
            # Fallback to empty model if download fails
            nlp = spacy.blank("en")
    return nlp

def extract_entities(text):
    """
    Extracts organizations, people, locations, and dates from the article text using spaCy NER.
    """
    results = {
        "organizations": [],
        "people": [],
        "locations": [],
        "dates": []
    }

    if not text or not isinstance(text, str):
        return results

    model = _load_spacy_model()
    doc = model(text)

    orgs = set()
    people = set()
    locs = set()
    dates = set()

    for ent in doc.ents:
        entity_text = ent.text.strip()
        if not entity_text or len(entity_text) < 2:
            continue
            
        label = ent.label_
        if label == "ORG":
            orgs.add(entity_text)
        elif label == "PERSON":
            people.add(entity_text)
        elif label in ["GPE", "LOC"]:
            locs.add(entity_text)
        elif label == "DATE":
            dates.add(entity_text)

    results["organizations"] = sorted(list(orgs))
    results["people"] = sorted(list(people))
    results["locations"] = sorted(list(locs))
    results["dates"] = sorted(list(dates))

    return results
