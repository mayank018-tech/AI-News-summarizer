"""
ner.py — Robust Named Entity Recognition
─────────────────────────────────────────
Uses spaCy NER with extensive post-processing rules to handle
AI/tech articles correctly:

  • AI product names (Gemini, Claude, GPT-4 …) → NOT people
  • Tech frameworks/platforms (FastAI, PyTorch …) → NOT locations
  • Version strings and vague time words → NOT dates
  • Short all-caps abbreviations → NOT organisations
  • "Azure and Office 365" compound phrases → cleaned up
"""
import re
import spacy
import spacy.cli

nlp = None

# ── Comprehensive AI / tech product blocklists ─────────────────────────────────

# These are AI model / product names that spaCy mistakes for PERSON
_AI_PRODUCTS_NOT_PERSON: set[str] = {
    # Google
    "Gemini", "Gemini Ultra", "Gemini Advanced", "Gemini Pro", "Bard", "PaLM", "PaLM 2", "Imagen", "Lumiere",
    # OpenAI
    "GPT", "GPT-4", "GPT-4o", "GPT-5", "GPT-3", "ChatGPT", "Codex", "DALL-E",
    "DALL·E", "Sora", "Whisper", "Embeddings",
    # Anthropic
    "Claude", "Claude 2", "Claude 3", "Claude 3.5", "Claude 3.5 Sonnet", "Constitutional AI",
    # Meta
    "Llama", "Llama 2", "Llama 3", "LLaMA", "Meta AI",
    # Microsoft
    "Copilot", "Bing Chat", "Sydney",
    # Mistral / others
    "Mistral", "Falcon", "Phi", "Phi-2", "Grok", "Inflection", "DeepSeek",
    # Generic AI terms misread as names
    "AI", "AGI", "ASI", "LLM", "NLP", "ML", "RL", "RLHF",
    "Transformer", "BERT", "RoBERTa", "T5", "XLNet", "BLOOM",
    "Stable Diffusion", "MidJourney", "Midjourney",
    # Frameworks sometimes tagged as persons
    "TensorFlow", "PyTorch", "Keras", "JAX", "Flax", "Hugging Face",
}

# Tech Giants & AI Labs (Often mistaken as locations or people)
_TECH_ORGS: set[str] = {
    "OpenAI", "Google", "Microsoft", "Apple", "Amazon", "Meta", "Facebook",
    "Twitter", "X", "Anthropic", "DeepMind", "Nvidia", "NVIDIA", "AMD", 
    "Intel", "IBM", "Tesla", "Mistral", "Inflection", "xAI", "HuggingFace", "Hugging Face", "GitHub", "GitLab"
}

# These should NOT appear in the locations bucket
_NOT_LOCATION: set[str] = _TECH_ORGS.union({
    # AI / ML terms and product names
    "AI", "AGI", "ML", "DL", "NLP", "LLM", "RL",
    "Gemini", "Bard", "PaLM", "Imagen",
    "GPT", "ChatGPT", "DALL-E", "Sora", "Codex",
    "Claude", "Llama", "LLaMA",
    "FastAI", "PyTorch", "TensorFlow", "Keras",
    # Cloud and Infra
    "AWS", "GCP", "Azure", "Docker", "Kubernetes",
    # Generic words spaCy confuses with places
    "Internet", "Web", "Cloud", "Space", "Core", "Hub",
})

# Medical / science abbreviations misread as ORGs or other
_MEDICAL_ABBR: set[str] = {
    "PET", "MRI", "CT", "ECG", "EEG", "DNA", "RNA", "PCR",
    "WHO", "CDC", "NIH", "FDA", "EMA",
}

# Patterns for vague / non-useful dates
_VAGUE_DATE_RE = re.compile(
    r"^(a\s+|the\s+|an\s+)?(few|several|many|some|couple|number\s+of|"
    r"next|last|previous|recent|past|current|this|that|those|"
    r"upcoming|following|coming|decade|century|era|age|period|"
    r"week|month|year|quarter|season|moment|time|now|soon|later|"
    r"today|yesterday|tomorrow|recently|shortly)\b",
    re.IGNORECASE,
)

# "X and Y" compound ORG patterns — split them
_AND_SPLIT_RE = re.compile(r"\s+and\s+", re.IGNORECASE)


def _load_spacy_model():
    global nlp
    if nlp is not None:
        return nlp
    for model_name in ("en_core_web_lg", "en_core_web_md", "en_core_web_sm"):
        try:
            nlp = spacy.load(model_name)
            return nlp
        except OSError:
            continue
    try:
        spacy.cli.download("en_core_web_sm")
        nlp = spacy.load("en_core_web_sm")
    except Exception:
        nlp = spacy.blank("en")
    return nlp


def _strip_article(text: str) -> str:
    """Remove leading the/a/an and trailing punctuation."""
    text = re.sub(r"^(the|a|an)\s+", "", text.strip(), flags=re.IGNORECASE)
    return re.sub(r"[.,;:!?'\"]+$", "", text).strip()


def _is_version_string(text: str) -> bool:
    """True for things like 'Llama 3', 'GPT-4o', 'v2.1'."""
    return bool(re.match(r"^[\w\-]+\s*\d[\d.]*[a-z]?$", text, re.IGNORECASE))


def _looks_like_person(text: str) -> bool:
    """
    Heuristic: a PERSON entity should look like an actual human name.
    - At least 2 capitalised words  OR  a known human name pattern
    - Must NOT be in the AI products blocklist
    - Must NOT be all-uppercase (acronym)
    - Must NOT be a version string
    """
    if text in _AI_PRODUCTS_NOT_PERSON:
        return False
    
    # Block anything that starts with a known AI product name (e.g. 'Gemini Ultra')
    first_word = text.split()[0] if text else ""
    if first_word in _AI_PRODUCTS_NOT_PERSON or first_word in _TECH_ORGS:
        return False

    if text.upper() == text and len(text) <= 6:   # e.g. "AI", "GPT"
        return False
    if _is_version_string(text):
        return False
    words = text.split()
    # Need ≥2 words each starting uppercase, or a single word that is
    # clearly a known personal name (we can't check all names, so we
    # require ≥2 words to be conservative for single-word matches)
    if len(words) == 1:
        # Only keep if it's clearly a human first name not in our blocklist
        # and not all-caps
        if text[0].isupper() and not text.isupper() and text.isalpha():
            return True   # e.g. "Sundar" — allow single capitalised word
        return False
    return all(w[0].isupper() for w in words if w.isalpha())


# Common tech terms often misclassified as ORG by spaCy
_TECH_TERMS: set[str] = {
    "AI", "ML", "NLP", "Python", "Java", "JavaScript", "React", "C++", 
    "Vue", "Angular", "Node.js", "Docker", "Kubernetes", "API", "HTML", "CSS", 
    "SQL", "Machine Learning", "Artificial Intelligence", "AGI", "Deep Learning",
    "Computer Vision", "Blockchain", "Web3", "Crypto"
}

def _is_org_in_context(ent, doc) -> bool:
    """
    Determine if an entity is acting as an ORG based on surrounding context.
    e.g., 'AI Inc', 'CEO of AI', 'Python Software Foundation'.
    """
    org_indicators = {"inc", "inc.", "corp", "corp.", "corporation", "ltd", "ltd.", 
                      "foundation", "company", "co.", "co", "institute", "lab", "labs",
                      "group", "agency", "department", "association"}
                      
    # Check word immediately following
    if ent.end < len(doc):
        next_word = doc[ent.end].text.lower()
        if next_word in org_indicators:
            return True
            
    # Check word immediately preceding
    if ent.start > 0:
        prev_word = doc[ent.start - 1].text.lower()
        if prev_word in {"ceo", "cto", "president", "director", "founder", "at", "by", "from"}:
            return True
            
    return False

def extract_entities(text: str) -> dict:
    """
    Extract named entities from article text with robust post-processing.
    Returns a dict: { organizations, people, locations, dates, technologies, products }
    """
    results = {
        "organizations": [],
        "people":        [],
        "locations":     [],
        "dates":         [],
        "technologies":  [],
        "products":      []
    }

    if not text or not isinstance(text, str):
        return results

    model = _load_spacy_model()
    doc   = model(text[:100_000])   # cap at 100k chars

    orgs:   set[str] = set()
    people: set[str] = set()
    locs:   set[str] = set()
    dates:  set[str] = set()
    techs:  set[str] = set()
    prods:  set[str] = set()

    for ent in doc.ents:
        raw     = ent.text.strip()
        cleaned = _strip_article(raw)
        label   = ent.label_

        if not cleaned or len(cleaned) < 2:
            continue

        # ── PERSON ────────────────────────────────────────────────────────
        if label == "PERSON":
            if cleaned in _AI_PRODUCTS_NOT_PERSON or cleaned in _TECH_ORGS:
                # Reclassify known AI products or tech orgs
                if cleaned in _TECH_ORGS:
                    orgs.add(cleaned)
                else:
                    prods.add(cleaned)
                continue
            if _looks_like_person(cleaned):
                people.add(cleaned)
            # else: discard — likely a misclassification

        # ── ORG ───────────────────────────────────────────────────────────
        elif label == "ORG":
            # Skip known medical abbreviations
            if cleaned.upper() in _MEDICAL_ABBR:
                continue
                
            # Context-based filtering for tech terms
            is_tech = False
            for tech in _TECH_TERMS:
                if cleaned.lower() == tech.lower():
                    is_tech = True
                    break
                    
            if is_tech:
                if _is_org_in_context(ent, doc):
                    orgs.add(cleaned)
                else:
                    techs.add(cleaned)
                continue
                
            # Skip all-caps ≤4-char acronyms (often noise)
            if cleaned.isupper() and len(cleaned) <= 4:
                continue
            # Split "Azure and Office 365" → ["Azure", "Office 365"]
            if _AND_SPLIT_RE.search(cleaned):
                for part in _AND_SPLIT_RE.split(cleaned):
                    part = part.strip()
                    if part and len(part) > 1 and not (part.isupper() and len(part) <= 4):
                        orgs.add(part)
            else:
                orgs.add(cleaned)

        # ── LOCATION / GPE ────────────────────────────────────────────────
        elif label in ("GPE", "LOC", "FAC"):
            # Block AI/tech terms tagged as locations
            if cleaned in _TECH_ORGS:
                # Redirect tech organizations to ORGs
                orgs.add(cleaned)
                continue
            if cleaned in _NOT_LOCATION:
                continue
            if cleaned.upper() in _MEDICAL_ABBR:
                continue
            # Block if it ends in digits (e.g. "FastAI 2")
            if re.search(r"\d", cleaned):
                continue
            locs.add(cleaned)

        # ── DATE ──────────────────────────────────────────────────────────
        elif label == "DATE":
            # Skip vague time references
            if _VAGUE_DATE_RE.match(cleaned):
                continue
            # Skip version strings misread as dates
            if _is_version_string(cleaned):
                continue
            # Always keep 4-digit year references (2024, 2025, etc.)
            if re.match(r"^\d{4}$", cleaned):
                dates.add(cleaned)
                continue
            # Keep anything with a digit + meaningful length
            has_digit = bool(re.search(r"\d", cleaned))
            month_names = {
                "january","february","march","april","may","june",
                "july","august","september","october","november","december",
                "jan","feb","mar","apr","jun","jul","aug","sep","oct","nov","dec"
            }
            has_month = any(m in cleaned.lower() for m in month_names)
            if (has_digit or has_month) and len(cleaned) >= 4:
                dates.add(cleaned)

        # ── PRODUCT / TECH Catch-all ──────────────────────────────────────
        elif label == "PRODUCT":
            if cleaned and len(cleaned) > 2 and cleaned not in _MEDICAL_ABBR:
                prods.add(cleaned)

    results["organizations"] = sorted(orgs)
    results["people"]        = sorted(people)
    results["locations"]     = sorted(locs)
    results["dates"]         = sorted(dates)
    results["technologies"]  = sorted(techs)
    results["products"]      = sorted(prods)
    return results
