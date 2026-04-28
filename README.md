<div align="center">

# 🎓 NGLP — Next Gen Learning Pathway

### AI-Powered Personalised Learning Roadmap System

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-LLaMA--3-orange?style=flat)
![LangChain](https://img.shields.io/badge/LangChain-0.2+-1C3C3C?style=flat)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-1.3+-F7931E?style=flat&logo=scikit-learn&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

**A final year CS project that combines Large Language Models, content-based recommendation,
and interactive data visualisation to deliver personalised learning roadmaps.**

[Live Demo](#running-the-project) · [Features](#features) · [Architecture](#architecture) · [Tech Stack](#tech-stack)

</div>

---

## 📖 Overview

NGLP solves a fundamental problem in online learning: **platforms give content, but not direction.**

When a student wants to learn Python, Machine Learning, or Cybersecurity, they face thousands
of unstructured resources with no clear starting point, no sequence, and no personalisation
based on their current knowledge level.

NGLP solves this by:
- Using **Groq's LLaMA-3** to generate a structured, phased roadmap tailored to each student
- Providing an **AI chatbot mentor** for concept explanations and guidance
- Using **TF-IDF cosine similarity** to recommend the most relevant resources per topic
- Tracking progress with **6 types of visualisations**
- Sending **contextual notifications** for streaks, milestones, and study reminders

---

## ✨ Features

| Feature | Description |
|---|---|
| 🤖 **AI Roadmap Generation** | Groq LLaMA-3 generates phased roadmaps in real-time |
| 💬 **AI Chatbot Mentor** | Context-aware responses using Groq + LangChain |
| 🔍 **TF-IDF Recommender** | Scikit-learn cosine similarity resource recommendations |
| 📊 **Progress Analytics** | 6 Seaborn/Matplotlib charts with real user data |
| 🔔 **Notification System** | Streak tracking, milestone alerts, study reminders |
| ← **Back Navigation** | Browser-like navigation history in sidebar |
| 🔐 **Authentication** | SHA-256 hashed passwords, session management |
| 📥 **Data Export** | Download progress CSV at any time |
| 🔄 **Offline Mode** | 24 static fallback roadmaps + rule-based chatbot |
| 📱 **Clean UI** | Inter font, indigo design system, card-based layout |

---

## 🏗 Architecture

```
┌──────────────────────────────────────────────────────────┐
│                   PRESENTATION LAYER                     │
│   app.py (router + auth + back navigation)               │
│   dashboard.py │ roadmap.py │ chatbot_page.py │ progress │
└─────────────────┬────────────────────────────────────────┘
                  │
┌─────────────────▼────────────────────────────────────────┐
│                BUSINESS + AI LOGIC LAYER                  │
│  auth.py          │ data_manager.py  │ pathway_engine.py  │
│  chatbot.py       │ recommender.py   │ visualizer.py      │
│  resource_manager │ notifications.py                      │
└─────────────────┬────────────────────────────────────────┘
                  │
┌─────────────────▼────────────────────────────────────────┐
│                      DATA LAYER                          │
│  users.json  │  progress.csv  │  resources.csv           │
│  roadmap_cache.json                                      │
└──────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
nglp/
├── app.py                      # Entry point, router, back navigation
├── requirements.txt
├── README.md
├── VIVA_PREPARATION.md         # Viva Q&A guide
├── .streamlit/
│   └── config.toml             # Theme: Indigo #6366F1
├── data/
│   ├── users.json              # Hashed user accounts
│   ├── progress.csv            # Topic completion log
│   ├── resources.csv           # 70+ curated learning resources
│   └── roadmap_cache.json      # AI roadmap cache (auto-created)
├── modules/
│   ├── auth.py                 # SHA-256 auth + session management
│   ├── data_manager.py         # CSV/JSON I/O + boolean normalisation
│   ├── pathway_engine.py       # Groq AI + 24 static roadmaps
│   ├── chatbot.py              # Groq SDK + LangChain + rule fallback
│   ├── recommender.py          # TF-IDF cosine similarity
│   ├── visualizer.py           # 6 Seaborn/Matplotlib charts
│   ├── resource_manager.py     # Resource search + filter
│   └── notifications.py        # Streak, milestone, reminder alerts
└── pages/
    ├── dashboard.py            # Hero card + KPIs + notifications
    ├── roadmap.py              # Phased topic cards + resource panel
    ├── chatbot_page.py         # Full AI chat interface
    └── progress.py             # Analytics + export
```

---

## 🛠 Tech Stack

| Technology | Version | Purpose | Why Chosen |
|---|---|---|---|
| Python | 3.9+ | Core language | Best AI/data ecosystem |
| Streamlit | 1.35+ | UI framework | Rapid interactive data apps |
| Groq API | — | LLM inference | Fastest inference (500-800 tok/s) |
| LLaMA-3 8B | — | Language model | Open-source, high quality |
| LangChain | 0.2+ | LLM orchestration | Conversation history management |
| Pandas | 2.0+ | Data handling | Industry standard for tabular data |
| NumPy | 1.24+ | Numerical ops | Foundation for ML operations |
| Scikit-learn | 1.3+ | TF-IDF + cosine sim | Production ML library |
| Seaborn | 0.13+ | Statistical charts | Publication-quality visuals |
| Matplotlib | 3.7+ | Chart rendering | Backend for Seaborn |
| SHA-256 | Built-in | Password hashing | One-way cryptographic hash |

---

## 🚀 Running the Project

### 1. Clone / Download
```bash
git clone https://github.com/yourusername/nglp.git
cd nglp
```

### 2. Virtual Environment
```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Groq API Key (Free at console.groq.com)
```bash
# macOS/Linux
export GROQ_API_KEY=your_key_here

# Windows CMD
set GROQ_API_KEY=your_key_here

# Windows PowerShell
$env:GROQ_API_KEY="your_key_here"
```

### 5. Launch
```bash
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

> **Note:** The app works completely without a Groq API key in offline mode —
> all 8 skills × 3 levels have complete static roadmaps.

---

## 🔄 User Flow

```
Register/Login → Select Skill + Level → AI Generates Roadmap
      ↓
Dashboard (LEARN THIS NEXT card + Notifications)
      ↓
Roadmap (Mark topics complete → resources recommended)
      ↓
Chatbot (Ask questions → AI explains with context)
      ↓
Progress (6 charts + export CSV)
```

---

## 📊 Supported Skills

| Skill | Levels | Fallback Roadmap |
|---|---|---|
| 🐍 Python | Beginner, Intermediate, Advanced | ✅ Full |
| 🤖 Machine Learning | Beginner, Intermediate, Advanced | ✅ Full |
| 📊 Data Science | Beginner, Intermediate, Advanced | ✅ Full |
| 🌐 Web Development | Beginner, Intermediate, Advanced | ✅ Full |
| 🧠 Artificial Intelligence | Beginner, Intermediate, Advanced | ✅ Full |
| ⚙️ DevOps | Beginner, Intermediate, Advanced | ✅ Full |
| ☁️ Cloud Computing | Beginner, Intermediate, Advanced | ✅ Full |
| 🔐 Cybersecurity | Beginner, Intermediate, Advanced | ✅ Full |

---

## 🐛 Key Bugs Fixed During Development

| Bug | Impact | Fix |
|---|---|---|
| Top-level `groq` import | App crashed without package | Lazy imports inside functions |
| CSV boolean as string | Progress tracking never worked | `_normalise_bool()` on every read |
| API key read at import | Key set after start invisible | Fresh `os.environ.get()` per call |
| Python 3.10 type hints | Syntax error on 3.9 | Removed `dict\|None` syntax |
| Duplicate prefill sends | Chatbot sent message twice | `session_state.pop()` |
| Matplotlib figure leaks | Memory warnings | `_finish()` helper pattern |
| Inconsistent widget keys | Resource toggle broken | Standardised key naming |

---

## 🔮 Future Improvements

- [ ] PostgreSQL database replacing CSV/JSON
- [ ] Persistent chatbot memory with vector store (Chroma/Pinecone)
- [ ] Collaborative filtering alongside TF-IDF
- [ ] AI-generated quiz per topic
- [ ] bcrypt password hashing + OAuth2
- [ ] Mobile-responsive layout
- [ ] Admin dashboard for educators
- [ ] Completion certificates

---

## 👨‍💻 Development

Built as a Final Year Computer Science Project.

**Core Technologies Used:**
- AI/LLM integration with prompt engineering
- Classical NLP with TF-IDF vectorisation
- Multi-chart data visualisation
- SHA-256 cryptographic authentication
- Three-tier modular architecture

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">
Built with ❤️ using Python + Streamlit + Groq AI
</div>
