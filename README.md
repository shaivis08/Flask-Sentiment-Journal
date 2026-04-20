# 📖 Metamorphosis: An AI-Powered Analytical Journal

**Metamorphosis** is a journaling application that bridges the gap between personal reflection and data science. It uses a multi-layered analysis pipeline to transform raw text entries into structured emotional data and generative insights.

## 🚀 Technical Evolution

The project serves as a transition from basic text processing to a sophisticated AI-integrated backend:

* **Initial:** Basic CRUD operations for journal entry management.
* **Current (NLP Layer):** Integration of **NLTK (VADER)** for sentiment intensity analysis and **FreqDist** for keyword frequency tracking.
* **Current (AI Layer):** Implementation of the **Google Gemini 3 Flash API** to interpret NLP scores and generate contextual feedback.

## ✨ Core Features

### 🧠 Hybrid Sentiment Engine
* **Sentiment Intensity Scoring:** Uses NLTK's VADER lexicon to calculate compound, positive, neutral, and negative scores for every entry.
* **Pattern Classification:** Custom logic that categorizes entries into sentiment-based lists to monitor emotional trends over time.
* **Data Visualization:** Dynamic **Sentiment Arcs** built with `Chart.js`, mapping emotional fluctuations across your journal history.

### 🤖 Generative Insight Layer (Gemini API)
* **Data-Driven Prompts:** Instead of sending raw text, the app passes a structured "package" of sentiment scores and frequency distributions to the Gemini 3 Flash model.
* **Contextual Feedback:** The AI acts as a reflective layer, translating mathematical sentiment scores into constructive daily and weekly insights.

### 🛠️ UX & UI Design
* **Skeuomorphic Navigation:** Page-navigation arrows anchored to the bottom corners to mimic the experience of a physical book.
* **Floating Action Toolbelt:** A central, glassmorphism-inspired menu that keeps AI analysis tools (Daily Insight, Mood Chart, Weekly Review) accessible without cluttering the content area.

## ⚙️ Installation & Setup

Follow these steps to run the project locally:

1. **Clone the Repository:**
```bash
   git clone https://github.com/shaivis08/Flask-Sentiment-Journal.git
   cd Flask-Sentiment-Journal
```

2. **Set up the Virtual Environment:**
```bash
   # Create the environment
   python3 -m venv .venv

   # Activate the environment (macOS/Linux)
   source .venv/bin/activate

   # OR Activate on Windows
   # .venv\Scripts\activate

   # Install required packages
   pip install -r requirements.txt
```

3. **Environment Variables:**  
   Create a `.env` file in the root directory and add your API keys:

GEMINI_API_KEY=your_api_key_here

4. **Run the Application:**
```bash
   python3 app.py
```

## 🛠️ Tech Stack

* **Backend:** Flask (Python 3.9)
* **Database:** SQLite with SQLAlchemy ORM
* **NLP:** NLTK (VADER, FreqDist, Punkt)
* **AI Engine:** Google Gemini 3 Flash API
* **Frontend:** HTML5, CSS3, JavaScript (Chart.js)

## 🔮 Future Roadmap

* **Linguistic Depth:** Integrating **spaCy** for Named Entity Recognition (NER) to track recurring people, events, and locations.
* **Semantic Search:** Implementing **Vector Embeddings** to allow for semantic similarity searches between journal entries.
* **Retrieval-Augmented Generation (RAG):** Connecting the Gemini layer to a vector database to provide long-term continuity in AI feedback.
* **Security:** Implementing user-side encryption for entry content to ensure data privacy.
