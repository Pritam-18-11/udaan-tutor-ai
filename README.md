# UDAAN ✈️ — Wings to Learn

> An AI-powered tutoring system built for rural Indian students with low-bandwidth internet.

---

## 🎯 Problem Statement

Personalized AI tutors are revolutionizing education — but they are expensive to run. In rural India, where internet is spotty and computing power is low, students cannot afford high-latency, high-cost queries to massive models like GPT-4 for every question.

**Challenge:** Build an intelligent tutoring system capable of ingesting entire state-board textbooks and providing personalized, curriculum-aligned answers — optimized for lowest cost per query and minimal data transfer.

---

## 💡 Our Solution

UDAAN uses **Context Pruning** to reduce API costs by ~95% compared to naive RAG systems.

| Approach     | Tokens per Query | Cost           |
|--------------|------------------|----------------|
|❌ Naive RAG | ~50,000 tokens   | Very Expensive  |
| ✅ UDAAN    | ~1,500 tokens    | **95% Cheaper** |

---

## ✨ Key Features

- 📄 **PDF Textbook Upload** — Upload any NCERT/State Board PDF
- 🤖 **AI Tutor Chat** — Curriculum-aligned, personalized answers
- 🎤 **Voice Assistant** — Ask by voice, get spoken answers
- ⚡ **Context Pruning** — Sends only top 4 relevant chunks to AI
- 🗄️ **Response Caching** — Same question = 0 API tokens
- 🎓 **Learning Modules** — Gravitation & Solar System animations
- 📝 **Quiz Time** — Module-wise quizzes
- 📊 **Student Dashboard** — XP, levels, achievements, performance tracking
- 🌐 **Rural India Ready** — Works on 2G/3G connections

---

## 🏗️ Architecture

```
Student
  │
  ▼
Frontend (HTML/CSS/JS)
  │
  ▼
Backend (FastAPI)
  │
  ├── PDF Upload → PyMuPDF → Smart Chunking
  │
  ├── Query → Local TF-IDF Scoring (FREE)
  │         → Top 4 Chunks Selected
  │         → Scaledown API (Compress)
  │         → Groq API (Answer)
  │         → Cache Response
  │
  └── Return Answer + Cost Stats
```

---

## 🛠️ Tech Stack

| Layer    | Technology            |
|----------|-----------------------|
| Frontend | HTML, CSS, JavaScript |
| Backend  |    Python, FastAPI    |
| PDF Processing |     PyMuPDF     |
| Compression |   Scaledown API    |
| AI Model |    Groq (Llama 3)     |
| Deployment |  Netlify + Render   |

---

## 🚀 Local Setup

### Prerequisites
- Python 3.10+
- Chrome browser (for voice features)

### 1. Clone the repository
```bash
git clone https://github.com/Pritam-18-11/udaan-tutor-ai.git
cd udaan-tutor-ai
```

### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt
```

### 3. Add API Keys
Open `backend/main.py` and update:
```python
SCALEDOWN_API_KEY = "your_scaledown_key"
GROQ_API_KEY      = "your_groq_key"
```

### 4. Run Backend
```bash
py -3.13 main.py
```
Backend runs at: `http://localhost:8000`

### 5. Open Frontend
Open `frontend/index.html` in Chrome browser.

---

## 📡 API Endpoints

| Method | Endpoint | Description  |
|--------|----------|--------------|
|  GET   |   `/`    | Health check |
|  POST  | `/upload-pdf` | Upload textbook PDF |
|  POST  |  `/chat`  | Ask a question |
|  POST  | `/generate-quiz` | Generate quiz from PDF |
|  GET  | `/stats` | Cost optimization stats |

---

## 💰 Cost Optimization Strategy

1. **Smart Chunking** — ~400-word overlapping chunks
2. **Local Scoring** — TF-IDF runs locally (no API cost)
3. **Top-K Selection** — Only top 4 chunks sent to AI
4. **Scaledown Compression** — Chunks compressed before sending
5. **Response Caching** — Repeated questions cost 0 tokens

---

## 🏆 Hackathon

Built for **HPE GenAI for GenZ Hackathon**
- Problem: The Education Tutor for Remote India
- Technique: Context Pruning

---

*UDAAN — Because every Indian student deserves a personal AI tutor. 🇮🇳*