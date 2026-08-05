import spacy
from collections import Counter
import re

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    import spacy.cli
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Define technology keywords to look for around the company name
TECH_KEYWORDS = {
    "gpt", "reasoning", "multimodal", "cloud", "api", "llm", "transformer",
    "diffusion", "generative ai", "neural network", "hardware", "chips",
    "gpu", "tpu", "data center", "search", "robotics", "open source",
    "fine-tuning", "autonomous", "quantum"
}

# Define roles based on keywords
ROLE_MAPPING = {
    "developer": ["developed", "created", "built", "launched", "announced", "released", "maker", "creator", "model"],
    "investor": ["invested", "funded", "backed", "acquired", "bought", "valuation", "stake"],
    "partner": ["partnered", "collaboration", "together", "joint", "alliance"],
    "competitor": ["rival", "competitor", "versus", "competing", "challenge"],
    "regulator": ["sued", "investigation", "banned", "regulation", "lawsuit", "court", "government"]
}

def _get_surrounding_sentences(doc, entity, window=1):
    """Get the sentences surrounding an entity."""
    sentences = list(doc.sents)
    ent_sent_idx = -1
    for i, sent in enumerate(sentences):
        if entity.start >= sent.start and entity.end <= sent.end:
            ent_sent_idx = i
            break
            
    if ent_sent_idx == -1:
        return ""
        
    start_idx = max(0, ent_sent_idx - window)
    end_idx = min(len(sentences), ent_sent_idx + window + 1)
    
    context = " ".join([sent.text for sent in sentences[start_idx:end_idx]])
    return context.lower()

def extract_company_insights(text, max_companies=5):
    """
    Extract organizations and provide insights (role, related tech, keywords).
    """
    if not text:
        return []
        
    # Process text (limit to 10k chars to keep it fast)
    doc = nlp(text[:10000])
    
    # Filter for ORGs
    orgs = [ent for ent in doc.ents if ent.label_ == "ORG"]
    
    # Count occurrences by normalized text
    org_counts = Counter([ent.text.strip().replace('\n', ' ') for ent in orgs])
    
    # Standardize names (e.g. "OpenAI" and "OpenAI's" -> "OpenAI")
    cleaned_counts = Counter()
    for name, count in org_counts.items():
        clean_name = re.sub(r"['’]s$", "", name)
        if len(clean_name) > 1: # Ignore single letter orgs
            cleaned_counts[clean_name] += count
            
    # Get top organizations
    top_orgs = [org for org, count in cleaned_counts.most_common(max_companies)]
    
    results = []
    
    for org_name in top_orgs:
        # Find the first occurrence to get context
        target_ent = None
        for ent in orgs:
            if org_name in ent.text:
                target_ent = ent
                break
                
        if not target_ent:
            continue
            
        context = _get_surrounding_sentences(doc, target_ent, window=2)
        
        # 1. Determine Role
        role = "Subject of article" # Default
        for role_name, keywords in ROLE_MAPPING.items():
            if any(kw in context for kw in keywords):
                if role_name == "developer":
                    role = "Developer / Creator"
                elif role_name == "investor":
                    role = "Investor / Backer"
                elif role_name == "partner":
                    role = "Partner / Collaborator"
                elif role_name == "competitor":
                    role = "Competitor"
                elif role_name == "regulator":
                    role = "Regulator / Legal Entity"
                break
                
        # 2. Extract Related Technologies
        related_tech = []
        for tech in TECH_KEYWORDS:
            if tech in context:
                related_tech.append(tech.title())
                
        # Sort and limit tech
        related_tech = sorted(list(set(related_tech)))[:4]
        
        results.append({
            "name": org_name,
            "occurrences": cleaned_counts[org_name],
            "role": role,
            "related_technologies": related_tech
        })
        
    return results
