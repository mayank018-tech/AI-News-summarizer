import os
import sys
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Auto-copy generated newspaper background image and logo to static folder
try:
    import shutil
    # Newspaper background
    src_paper = r"C:\Users\Mayank S Gohil\.gemini\antigravity-ide\brain\f2e5a47b-d401-410a-970b-d4eff82151d1\ai_newspaper_1785881589120.png"
    dest_paper = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "newspaper_visual.png")
    if os.path.exists(src_paper):
        shutil.copy(src_paper, dest_paper)
    
    # Logo image
    src_logo = r"C:\Users\Mayank S Gohil\.gemini\antigravity-ide\brain\f2e5a47b-d401-410a-970b-d4eff82151d1\media__1785883526545.jpg"
    dest_logo = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "bg3.png")
    if os.path.exists(src_logo):
        shutil.copy(src_logo, dest_logo)
except Exception as e:
    pass

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, make_response
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import urllib.request
import re

def fetch_article_text(url):
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8', errors='ignore')
        
        # Strip script & style elements
        text = re.sub(r'<script.*?>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style.*?>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<.*?>', ' ', text)
        
        # Clean up whitespace and empty lines
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        # Filter down to the main content (ignore layout boilerplate header/footer if possible)
        text_lines = text.split('\n')
        # Keep only paragraphs/lines with actual sentence structure
        content_lines = [line for line in text_lines if len(line) > 40 and not any(kw in line.lower() for kw in ['cookies', 'privacy policy', 'all rights reserved', 'sign up', 'subscribe'])]
        
        cleaned_text = '\n'.join(content_lines)
        if len(cleaned_text) < 150:
            cleaned_text = '\n'.join(text_lines) # Fallback to all text if filter was too aggressive
            
        return cleaned_text[:4000] # Cap text length to prevent huge context sizes
    except Exception as e:
        return f"Failed to retrieve article content: {str(e)}"

from summarize import generate_summary
from keywords import extract_keywords
from ner import extract_entities
from sentiment import analyze_sentiment
from ml_model.predictor import predict_category
from credibility import analyze_credibility
from bias import detect_bias
from company_insights import extract_company_insights
from brief import generate_brief
from terminology import explain_terminology

import nltk
from nltk.corpus import words
def _ensure_words():
    nltk_data_dir = '/tmp/nltk_data'
    if nltk_data_dir not in nltk.data.path:
        nltk.data.path.append(nltk_data_dir)
    try:
        nltk.data.find('corpora/words')
    except LookupError:
        nltk.download('words', download_dir=nltk_data_dir, quiet=True)

_ensure_words()
_english_vocab = set(w.lower() for w in words.words())

def is_meaningful_text(text, threshold=0.3):
    cleaned = re.sub(r'[^a-zA-Z\s]', '', text.lower()).split()
    if not cleaned or len(cleaned) < 5:
        return False
    valid_count = sum(1 for w in cleaned if w in _english_vocab)
    return (valid_count / len(cleaned)) >= threshold

app = Flask(__name__)
# Enable CORS for cross-origin requests from GitHub Pages
CORS(app, supports_credentials=True)

# Required for cross-origin cookies (sessions)
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True

@app.after_request
def add_header(response):
    # If the request is for a static file (like images, CSS, JS), allow caching
    if request.path.startswith('/static/'):
        response.headers['Cache-Control'] = 'public, max-age=31536000'
    else:
        # Prevent caching for dynamic routes and API
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response

app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key_1234')

# Use Supabase Database URL or a local SQLite backup
db_url = os.environ.get('DATABASE_URL')
if not db_url:
    # Use fallback SQLite database in /tmp folder so the app runs on Vercel's read-only file system
    db_url = 'sqlite:////tmp/app.db'
else:
    # Correct connection string prefix if it starts with postgres:// (SQLAlchemy requires postgresql://)
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class Summary(db.Model):
    __tablename__ = 'summaries'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # Nullable for guest/anonymous
    headline = db.Column(db.String(255), nullable=False)
    original_text = db.Column(db.Text, nullable=False)
    summary_text = db.Column(db.Text, nullable=False)
    sentiment_label = db.Column(db.String(50))
    sentiment_score = db.Column(db.Float) # compound score
    primary_category = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

# Ensure tables are created
with app.app_context():
    db.create_all()

@app.before_request
def check_valid_session():
    # If a user is logged in, ensure their account still exists in the DB (handles Render ephemeral disk wipes)
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if not user:
            session.clear()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/history')
def history():
    user_id = session.get('user_id')
    # If logged in, show user history; otherwise show guest history (user_id is None)
    summaries = Summary.query.filter_by(user_id=user_id).order_by(Summary.created_at.desc()).all()
    return render_template('history.html', summaries=summaries)

@app.route('/api/history', methods=['GET', 'POST'])
def api_history():
    user_id = session.get('user_id')
    if request.is_json and request.get_json():
        user_id = request.get_json().get('user_id', user_id)
        
    summaries = Summary.query.filter_by(user_id=user_id).order_by(Summary.created_at.desc()).all()
    history_data = []
    for s in summaries:
        history_data.append({
            'id': s.id,
            'headline': s.headline,
            'summary_text': s.summary_text,
            'sentiment_label': s.sentiment_label,
            'sentiment_score': s.sentiment_score,
            'primary_category': s.primary_category,
            'created_at': s.created_at.strftime("%Y-%m-%d %H:%M")
        })
    return jsonify({"history": history_data})

@app.route('/reanalyze/<int:summary_id>')
def reanalyze(summary_id):
    user_id = session.get('user_id')
    summary = Summary.query.filter_by(id=summary_id, user_id=user_id).first_or_404()
    return render_template('index.html', prefill_text=summary.original_text)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
        else:
            username = request.form.get('username')
            password = request.form.get('password')
            
        user = User.query.filter((User.username == username) | (User.email == username)).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            if request.is_json:
                return jsonify({"status": "success", "message": "Logged in successfully", "redirect": "index.html", "user_id": user.id, "username": user.username})
            return redirect(url_for('index'))
            
        if request.is_json:
            return jsonify({"status": "error", "message": "Invalid username or password"}), 401
        return render_template('login.html', error="Invalid username or password")
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
        else:
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            
        if User.query.filter_by(username=username).first():
            if request.is_json:
                return jsonify({"status": "error", "message": "Username already exists"}), 400
            return render_template('signup.html', error="Username already exists")
            
        if User.query.filter_by(email=email).first():
            if request.is_json:
                return jsonify({"status": "error", "message": "Email already registered"}), 400
            return render_template('signup.html', error="Email already registered")
            
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        session['user_id'] = new_user.id
        session['username'] = new_user.username
        
        if request.is_json:
            return jsonify({"status": "success", "message": "Registered successfully", "redirect": "index.html", "user_id": new_user.id, "username": new_user.username})
        return redirect(url_for('index'))
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/edit-profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    error = None
    success = None
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        new_password = request.form.get('password', '').strip()
        
        if not username or not email:
            error = "Username and email cannot be empty."
        else:
            # Check username uniqueness
            existing_user = User.query.filter_by(username=username).first()
            if existing_user and existing_user.id != user.id:
                error = "Username already taken."
            
            # Check email uniqueness
            existing_email = User.query.filter_by(email=email).first()
            if existing_email and existing_email.id != user.id:
                error = "Email already registered."
                
        if not error:
            user.username = username
            user.email = email
            if new_password:
                user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            session['username'] = user.username
            success = "Profile updated successfully!"
            
    return render_template('edit_profile.html', user=user, error=error, success=success)

@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    
    # Query database stats for the current user
    total_count = Summary.query.filter_by(user_id=user_id).count()
    pos_count = Summary.query.filter_by(user_id=user_id, sentiment_label='Positive').count()
    neu_count = Summary.query.filter_by(user_id=user_id, sentiment_label='Neutral').count()
    neg_count = Summary.query.filter_by(user_id=user_id, sentiment_label='Negative').count()
    
    tech_count = Summary.query.filter_by(user_id=user_id, primary_category='AI Technology & Systems').count()
    research_count = Summary.query.filter_by(user_id=user_id, primary_category='Research & Science').count()
    policy_count = Summary.query.filter_by(user_id=user_id, primary_category='Policy, Law & Ethics').count()
    
    # Calculate average compound score
    from sqlalchemy import func
    avg_score_res = db.session.query(func.avg(Summary.sentiment_score)).filter_by(user_id=user_id).scalar()
    avg_score = round(avg_score_res, 3) if avg_score_res is not None else 0.0
    
    # Top Category
    cat_counts = {
        'AI Technology & Systems': tech_count,
        'Research & Science': research_count,
        'Policy, Law & Ethics': policy_count
    }
    top_category = max(cat_counts, key=cat_counts.get) if total_count > 0 else "None"
    
    stats = {
        'total': total_count,
        'pos': pos_count,
        'neu': neu_count,
        'neg': neg_count,
        'tech': tech_count,
        'research': research_count,
        'policy': policy_count,
        'avg_score': avg_score,
        'top_category': top_category
    }
    
    return render_template('dashboard.html', stats=stats)

@app.route('/api/dashboard', methods=['GET', 'POST'])
def api_dashboard():
    user_id = session.get('user_id')
    if request.is_json and request.get_json():
        user_id = request.get_json().get('user_id', user_id)
        
    # Query database stats for the current user
    total_count = Summary.query.filter_by(user_id=user_id).count()
    pos_count = Summary.query.filter_by(user_id=user_id, sentiment_label='Positive').count()
    neu_count = Summary.query.filter_by(user_id=user_id, sentiment_label='Neutral').count()
    neg_count = Summary.query.filter_by(user_id=user_id, sentiment_label='Negative').count()
    
    tech_count = Summary.query.filter_by(user_id=user_id, primary_category='AI Technology & Systems').count()
    research_count = Summary.query.filter_by(user_id=user_id, primary_category='Research & Science').count()
    policy_count = Summary.query.filter_by(user_id=user_id, primary_category='Policy, Law & Ethics').count()
    
    from sqlalchemy import func
    avg_score_res = db.session.query(func.avg(Summary.sentiment_score)).filter_by(user_id=user_id).scalar()
    avg_score = round(avg_score_res, 3) if avg_score_res is not None else 0.0
    
    cat_counts = {
        'AI Technology & Systems': tech_count,
        'Research & Science': research_count,
        'Policy, Law & Ethics': policy_count
    }
    top_category = max(cat_counts, key=cat_counts.get) if total_count > 0 else "None"
    
    return jsonify({
        'total': total_count,
        'pos': pos_count,
        'neu': neu_count,
        'neg': neg_count,
        'tech': tech_count,
        'research': research_count,
        'policy': policy_count,
        'avg_score': avg_score,
        'top_category': top_category,
        'username': session.get('username')
    })

@app.route('/analyze', methods=['POST'])
def analyze():
    """
    Accepts article text, runs the core NLP pipeline sequentially,
    and returns a structured JSON payload with summarization,
    sentiment, categories, entity recognition, and keywords.
    """
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'Invalid request payload. Must include text.'}), 400
            
        text = data['text'].strip()
        if not text:
            return jsonify({'error': 'Article text content cannot be empty.'}), 400

        # Scraping Trigger: If the input text is a URL, fetch the webpage body first
        if text.startswith('http://') or text.startswith('https://') or ('.' in text and ' ' not in text and len(text) < 120):
            scraped_text = fetch_article_text(text)
            if scraped_text.startswith("Failed to retrieve"):
                return jsonify({'error': scraped_text}), 400
            text = scraped_text

        if not is_meaningful_text(text):
            return jsonify({'error': 'The provided text contains too much unrecognizable or gibberish content. Please provide a valid news article.'}), 400

        # 1. Headline Extraction (First non-empty line or default title)
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        headline = lines[0] if lines else "Analyzed News Article"
        if len(headline) > 120:
            headline = headline[:120] + "..."

        # 2. Sequential NLP pipeline steps
        summary = generate_summary(text)
        keywords = extract_keywords(text)
        entities = extract_entities(text)
        sentiment_data = analyze_sentiment(text)
        
        # 3. ML-based category classification (TF-IDF + LinearSVC)
        categories = predict_category(text)

        # 4. Advanced NLP Features
        credibility = analyze_credibility(text)
        bias_data = detect_bias(text)
        company_insights = extract_company_insights(text)
        brief = generate_brief(text)
        terminology = explain_terminology(text)

        # Save to database if user is logged in (or as guest if user is None)
        user_id = session.get('user_id')
        if request.is_json and request.get_json():
            user_id = request.get_json().get('user_id', user_id)
            
        new_summary = Summary(
            user_id=user_id,
            headline=headline,
            original_text=text,
            summary_text=summary,
            sentiment_label=sentiment_data.get('label'),
            sentiment_score=sentiment_data.get('scores', {}).get('compound', 0.0),
            primary_category=categories.get('primary')
        )
        db.session.add(new_summary)
        db.session.commit()

        return jsonify({
            'headline': headline,
            'summary': summary,
            'keywords': keywords,
            'entities': entities,
            'sentiment': sentiment_data,
            'categories': categories,
            'credibility': credibility,
            'bias': bias_data,
            'company_insights': company_insights,
            'brief': brief,
            'terminology': terminology
        })

    except Exception as e:
        return jsonify({'error': f'Analysis error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
