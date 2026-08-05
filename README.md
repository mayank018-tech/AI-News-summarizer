# AI News Summarizer

A comprehensive full-stack web application that leverages Natural Language Processing (NLP) to analyze, summarize, and extract insights from news articles and text. 

## Features

* **Smart Summarization:** Automatically generate concise and readable summaries of long articles.
* **URL Parsing:** Simply paste a news article URL, and the app will automatically fetch and extract the main content, bypassing boilerplate HTML.
* **Sentiment Analysis:** Classifies text polarity (Positive, Neutral, Negative) using VADER sentiment analysis, providing a compound score.
* **Named Entity Recognition (NER):** Extracts key entities such as Organizations, People, Locations, and Dates using `spaCy`.
* **AI Category Detection:** Utilizes a custom-trained TF-IDF and LinearSVC machine learning model to categorize the text (e.g., AI Technology & Systems, Research & Science, Policy, Law & Ethics).
* **Keyword Extraction:** Identifies the most significant keywords in the text.
* **Credibility Scoring & Bias Detection:** Evaluates the objectivity and potential bias in the writing style.
* **User Accounts & Dashboard:** Secure authentication system with protected routes. Users can sign up, log in, view their personal history of analyzed texts, and see a dashboard with statistical breakdowns.

## Tech Stack

### Backend
* **Python / Flask:** Core web framework handling routing, API endpoints, and session management.
* **SQLAlchemy:** ORM used to manage the database schema (SQLite for local fallback, PostgreSQL/Supabase for production).
* **spaCy, NLTK, Scikit-learn:** Powerful NLP and machine learning libraries powering the core analysis pipelines.
* **Werkzeug Security:** Secure password hashing.

### Frontend
* **HTML5 & Jinja2:** Server-side template rendering.
* **Vanilla CSS3:** Custom, modern, glassmorphism-inspired UI with advanced CSS Grid/Flexbox layouts and custom micro-animations (No external CSS frameworks).
* **Vanilla JavaScript:** Handles dynamic DOM updates, debounced asynchronous `fetch()` API calls to the Flask backend, and UI interactions.
* **Lucide Icons:** Clean vector icons for the user interface.

## Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/mayank018-tech/AI-News-summarizer.git
   cd AI-News-summarizer
   ```

2. **Set up a virtual environment (Recommended)**
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download NLP Models**
   The application requires specific NLTK and spaCy models to function correctly:
   ```bash
   python -m spacy download en_core_web_sm
   python -c "import nltk; nltk.download('vader_lexicon'); nltk.download('punkt'); nltk.download('words')"
   ```

5. **Environment Variables**
   Create a `.env` file in the root directory and configure the following:
   ```env
   SECRET_KEY=your_secure_secret_key
   # Optional: Configure PostgreSQL connection (uses SQLite by default if left blank)
   DATABASE_URL=postgresql://user:password@host:port/dbname
   ```

6. **Run the Application**
   ```bash
   python app.py
   ```
   The application will be available at `http://127.0.0.1:5000`.

## Deployment

The application is configured to run smoothly in serverless and containerized environments. 
- It includes a `vercel.json` for **Vercel** serverless deployment.
- It includes a `Procfile` for **Render** or **Heroku** deployment (using `gunicorn`).
- NLTK data directories are routed to `/tmp` to support read-only file systems commonly found in modern cloud hosts.

## Security

* Protected routes prevent unauthorized access via strict server-side session checks in a centralized `@app.before_request` hook.
* Specialized `Cache-Control` headers prevent browser Back-Forward Cache (BFCache) vulnerabilities after a user logs out.
* CSRF protection and Secure cookie configurations for production.
