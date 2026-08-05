"""
MIT AI Articles — Dataset Enhancement & ML Category Classifier Training
=======================================================================
Enhances the raw MIT_AI_ARTICLES.csv dataset with derived features and
auto-generated category labels, then trains a TF-IDF + Logistic Regression
pipeline to classify articles into 3 categories:

  0 → AI Technology & Systems
  1 → Research & Science
  2 → Policy, Law & Ethics

Outputs:
  ml_model/category_classifier.pkl   — trained pipeline (vectorizer + model)
  data/MIT_AI_ARTICLES_enhanced.csv  — enhanced dataset with labels
"""

import os
import re
import sys
import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.metrics import (
    classification_report, accuracy_score, confusion_matrix, f1_score
)

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_CSV     = os.path.join(BASE_DIR, "data", "MIT_AI_ARTICLES.csv")
ENHANCED_CSV = os.path.join(BASE_DIR, "data", "MIT_AI_ARTICLES_enhanced.csv")
MODEL_PATH   = os.path.join(BASE_DIR, "ml_model", "category_classifier.pkl")

# ── Category label definitions ─────────────────────────────────────────────────
LABEL_MAP = {
    0: "AI Technology & Systems",
    1: "Research & Science",
    2: "Policy, Law & Ethics",
}

TECH_KW = [
    "model", "neural", "architecture", "gpu", "compute", "hardware",
    "deep learning", "machine learning", "training", "inference", "dataset",
    "algorithm", "network", "transformer", "llm", "language model",
    "image recognition", "computer vision", "robotics", "automation",
    "chip", "processor", "software", "code", "programming", "benchmark",
    "performance", "efficiency", "accuracy", "parameter", "weight",
    "generative", "diffusion", "embedding", "token", "fine-tuning",
    "reinforcement learning", "autonomous", "self-driving", "drone",
]

RESEARCH_KW = [
    "research", "paper", "publish", "university", "study", "scientist",
    "scientific", "laboratory", "experiment", "discovery", "findings",
    "journal", "peer review", "hypothesis", "biology", "chemistry",
    "physics", "medical", "clinical", "drug", "disease", "genome",
    "protein", "molecule", "material", "quantum", "neuroscience",
    "cognitive", "breakthrough", "mit", "stanford", "cambridge",
    "department", "professor", "phd", "graduate", "undergraduate",
]

POLICY_KW = [
    "policy", "ethics", "law", "regulation", "government", "bill",
    "safety", "copyright", "congress", "senate", "legislation",
    "compliance", "gdpr", "privacy", "surveillance", "bias",
    "fairness", "transparency", "accountability", "rights",
    "court", "legal", "lawsuit", "ban", "restrict", "govern",
    "agency", "federal", "international", "treaty", "standard",
    "misinformation", "deepfake", "harm", "risk", "social impact",
    "disinformation", "censorship", "trustworthy", "responsible ai",
    "human rights", "civil", "democratic", "justice", "equity",
    "data protection", "openai", "anthropic", "white house",
    "executive order", "act", "framework", "guidelines", "safe",
    "harmful", "dangerous", "misuse", "abuse", "threat", "weapon",
    "national security", "defense", "military", "warfare", "geopolitics",
    "authoritarian", "democratic", "vote", "election", "public",
]


def score_text(text: str) -> int:
    """Return the best-matching category index for a piece of text."""
    text_lower = text.lower()
    tech   = sum(1 for kw in TECH_KW   if kw in text_lower)
    res    = sum(1 for kw in RESEARCH_KW if kw in text_lower)
    policy = sum(1 for kw in POLICY_KW  if kw in text_lower)

    scores = [tech, res, policy]
    # Break ties by favouring Research (articles with equal scores are usually academic)
    return int(np.argmax(scores))


def clean_text(text: str) -> str:
    """Lightweight text cleaning for the TF-IDF vectorizer."""
    text = str(text).lower()
    text = re.sub(r"http\S+",  " ", text)          # strip URLs
    text = re.sub(r"[^a-z\s]", " ", text)          # keep only letters + spaces
    text = re.sub(r"\s+",      " ", text).strip()  # collapse whitespace
    return text


# ── 1. Load raw dataset ────────────────────────────────────────────────────────
print("=" * 60)
print("  MIT AI Articles — ML Training Pipeline")
print("=" * 60)

print(f"\n[1/6] Loading dataset from: {DATA_CSV}")
df = pd.read_csv(DATA_CSV, low_memory=False)
print(f"      Raw rows: {len(df):,}  |  Columns: {list(df.columns)}")

# ── 2. Dataset Enhancement ────────────────────────────────────────────────────
print("\n[2/6] Enhancing dataset …")

# Drop rows missing critical fields
df = df.dropna(subset=["title", "body"])
df = df.reset_index(drop=True)

# Derived feature: combined text input for the model
df["combined_text"] = (
    df["title"].fillna("") + " " +
    df["summary"].fillna("") + " " +
    df["body"].fillna("")
)

# Derived feature: article length in words
df["text_length"] = df["body"].apply(lambda x: len(str(x).split()))

# Derived feature: whether a research paper link exists
df["has_paper_link"] = df["paper_link"].apply(
    lambda x: 1 if (isinstance(x, str) and x.strip() not in ["", "nan"]) else 0
)

# Derived feature: publication year
def extract_year(val):
    try:
        return pd.to_datetime(val).year
    except Exception:
        return None

df["year"] = df["publication_date"].apply(extract_year)

# Auto-label every article using keyword scoring
print("      Auto-labeling categories …")
df["label"] = df["combined_text"].apply(score_text)
df["category"] = df["label"].map(LABEL_MAP)

# Print distribution
dist = df["category"].value_counts()
print("\n      Label distribution:")
for cat, cnt in dist.items():
    pct = cnt / len(df) * 100
    print(f"        {cat:<35} {cnt:>4} ({pct:.1f}%)")

# Save enhanced CSV
df.to_csv(ENHANCED_CSV, index=False)
print(f"\n      ✓ Enhanced dataset saved → {ENHANCED_CSV}")

# ── 3. Prepare Features & Labels ──────────────────────────────────────────────
print("\n[3/6] Preparing features …")

df["input_text"] = df["combined_text"].apply(clean_text)
X = df["input_text"].values
y = df["label"].values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"      Train: {len(X_train):,}  |  Test: {len(X_test):,}")

# ── 4. Train & Compare Models ─────────────────────────────────────────────────
print("\n[4/6] Training & comparing models …\n")

candidates = {
    "Logistic Regression": LogisticRegression(
        max_iter=1000, C=1.0, solver="lbfgs", class_weight="balanced"
    ),
    "Naive Bayes (Multinomial)": MultinomialNB(alpha=0.1),
    "Linear SVM": LinearSVC(max_iter=2000, C=1.0, class_weight="balanced"),
}

tfidf = TfidfVectorizer(
    max_features=15000,
    ngram_range=(1, 2),
    sublinear_tf=True,
    min_df=2,
    strip_accents="unicode",
)

best_name     = None
best_metric   = 0.0
best_pipeline = None

for name, clf in candidates.items():
    pipe = Pipeline([("tfidf", tfidf), ("clf", clf)])
    pipe.fit(X_train, y_train)
    preds    = pipe.predict(X_test)
    accuracy = accuracy_score(y_test, preds)
    macro_f1 = f1_score(y_test, preds, average="macro")
    print(f"  ── {name}")
    print(f"     Accuracy : {accuracy * 100:.2f}% | Macro F1: {macro_f1:.3f}")
    print(classification_report(
        y_test, preds,
        target_names=list(LABEL_MAP.values()),
        digits=3,
    ))
    if macro_f1 > best_metric:
        best_metric   = macro_f1
        best_name     = name
        best_pipeline = pipe

# ── 5. Save Best Model ─────────────────────────────────────────────────────────
print(f"\n[5/6] Best model: {best_name}  (Macro F1 = {best_metric:.3f})")
joblib.dump(best_pipeline, MODEL_PATH)
print(f"      ✓ Model saved → {MODEL_PATH}")

# ── 6. Confusion Matrix ────────────────────────────────────────────────────────
print("\n[6/6] Confusion matrix (best model):")
preds_best = best_pipeline.predict(X_test)
cm = confusion_matrix(y_test, preds_best)
labels = list(LABEL_MAP.values())
header = f"{'':>36}" + "".join(f"{l[:10]:>12}" for l in labels)
print(header)
for i, row in enumerate(cm):
    print(f"  {labels[i]:<34}" + "".join(f"{v:>12}" for v in row))

print("\n✅ Training complete! Model is ready for inference.")
print(f"   Load with: joblib.load('{MODEL_PATH}')")
