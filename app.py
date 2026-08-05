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

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from summarize import generate_summary
from keywords import extract_keywords
from ner import extract_entities
from sentiment import analyze_sentiment

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key_1234')

# Use Supabase Database URL or a local SQLite backup
db_url = os.environ.get('DATABASE_URL')
if not db_url:
    # Use fallback SQLite database in data folder so the app runs even if DB URL is not provided yet
    db_url = 'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'app.db')
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/history')
def history():
    user_id = session.get('user_id')
    # If logged in, show user history; otherwise show guest history (user_id is None)
    summaries = Summary.query.filter_by(user_id=user_id).order_by(Summary.created_at.desc()).all()
    return render_template('history.html', summaries=summaries)

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
                return jsonify({"status": "success", "message": "Logged in successfully", "redirect": url_for('index')})
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
            return jsonify({"status": "success", "message": "Registered successfully", "redirect": url_for('index')})
        return redirect(url_for('index'))
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

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

        # 3. Simple Rule-based Category Heuristics (Placeholder for future ML classification)
        text_lower = text.lower()
        tech_keywords = ['model', 'neural', 'architecture', 'edge', 'gpu', 'code', 'compute', 'hardware', 'deep learning']
        policy_keywords = ['policy', 'ethics', 'law', 'regulation', 'government', 'bill', 'safety', 'copyright']
        research_keywords = ['research', 'paper', 'publish', 'university', 'study', 'scientist', 'scientific']

        tech_score = sum(1 for kw in tech_keywords if kw in text_lower)
        policy_score = sum(1 for kw in policy_keywords if kw in text_lower)
        research_score = sum(1 for kw in research_keywords if kw in text_lower)

        total_score = tech_score + policy_score + research_score
        if total_score == 0:
            tech_score = 1
            total_score = 1

        categories = {
            "primary": "AI Technology & Systems" if tech_score >= max(policy_score, research_score) else
                       "Research & Science" if research_score >= policy_score else "Policy, Law & Ethics",
            "scores": {
                "tech": round((tech_score / total_score) * 100, 1),
                "policy": round((policy_score / total_score) * 100, 1),
                "research": round((research_score / total_score) * 100, 1)
            }
        }

        # Save to database if user is logged in (or as guest if user is None)
        user_id = session.get('user_id')
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
            'categories': categories
        })

    except Exception as e:
        return jsonify({'error': f'Analysis error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
