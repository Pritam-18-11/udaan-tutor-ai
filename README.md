# 🚀 UDAAN – AI-Powered Tutoring System
### Hackathon MVP | Context-Pruned RAG | Cost-Optimized

---

## 📋 What This Project Does

UDAAN is an AI tutoring system that:
- 📄 **Ingests PDF textbooks** (any subject, any size)
- 🤖 **Answers student questions** based on the textbook content
- 💰 **Reduces AI API costs by ~90%** using smart context pruning
- 📝 **Generates quizzes** from uploaded textbooks automatically
- 🌌 **Visualizes physics concepts** (gravity simulation)

---

## 💡 How It's Better Than Naive RAG (Important for Judges!)

| Approach | Tokens per query | Cost |
|----------|-----------------|------|
| **Naive RAG** (send full textbook) | ~50,000 tokens | 💸 Very expensive |
| **Our approach** (context pruning) | ~1,500 tokens | ✅ ~97% cheaper |

**How we achieve this:**
1. **Smart Chunking** — Split textbook into ~400-word chunks (not too big, not too small)
2. **Local Relevance Scoring** — Score ALL chunks locally (FREE, no API call)
3. **Top-K Selection** — Only send the 4 most relevant chunks to AI
4. **Context Pruning** — Trim even those 4 chunks to fit a token budget
5. **Response Caching** — Identical questions get cached responses (0 API calls!)

---

## 📁 Project Structure

```
udaan-ai/
│
├── backend/
│   ├── main.py            ← FastAPI backend (all AI logic here)
│   └── requirements.txt   ← Python dependencies
│
├── frontend/
│   └── index.html         ← Complete frontend (just open in browser)
│
└── README.md              ← This file
```

---

## ⚡ Quick Setup (Step by Step)

### Step 1: Install Python
- Download from https://python.org (get version 3.10 or newer)
- During install, check "Add Python to PATH" ✅
- Open a terminal (Command Prompt on Windows, Terminal on Mac/Linux)
- Verify: type `python --version` — should show Python 3.10+

### Step 2: Get the project files
Put all files in a folder like `udaan-ai/` following the structure above.

### Step 3: Set up the backend

Open your terminal, navigate to the backend folder:

```bash
# Windows
cd C:\path\to\udaan-ai\backend

# Mac/Linux
cd /path/to/udaan-ai/backend
```

Install dependencies:

```bash
pip install -r requirements.txt
```

> ⚠️ If `pip` is not found, try `pip3` or `python -m pip`

This installs:
- `fastapi` — the web framework for our backend
- `uvicorn` — runs the backend server
- `pymupdf` — reads PDF files
- `httpx` — makes API calls to Scaledown

### Step 4: Add your Scaledown API Key

Open `backend/main.py` in any text editor (Notepad works!).

Find this line near the top:
```python
SCALEDOWN_API_KEY = os.environ.get("SCALEDOWN_API_KEY", "YOUR_SCALEDOWN_API_KEY_HERE")
```

Replace `YOUR_SCALEDOWN_API_KEY_HERE` with your actual Scaledown API key:
```python
SCALEDOWN_API_KEY = os.environ.get("SCALEDOWN_API_KEY", "sk-scaledown-abc123your-real-key")
```

Also check/update the Scaledown API URL and model if needed:
```python
SCALEDOWN_BASE_URL = "https://api.scaledown.com/v1"   # ← Your Scaledown URL
SCALEDOWN_MODEL    = "gpt-4o-mini"                     # ← Model name from Scaledown
```

> 💡 **Alternative (safer):** Set it as an environment variable instead:
> - Windows: `set SCALEDOWN_API_KEY=your-key-here`
> - Mac/Linux: `export SCALEDOWN_API_KEY=your-key-here`

### Step 5: Start the backend

```bash
python main.py
```

You should see:
```
🚀 Starting UDAAN AI Backend...
📖 API docs at: http://localhost:8000/docs
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Leave this terminal open!** The backend runs here.

### Step 6: Open the frontend

Open a **new** terminal window (keep the backend running!).

Simply open `frontend/index.html` in your browser:
- **Windows:** Double-click `index.html`, or drag it into Chrome/Firefox
- **Mac:** Right-click → Open with → Chrome (or any browser)
- **Linux:** `xdg-open frontend/index.html`

> 💡 The frontend is just an HTML file — no extra server needed!

---

## 🧪 How to Test (Step by Step)

### Test 1: Backend is working
Open your browser and go to: `http://localhost:8000`

You should see:
```json
{"status": "UDAAN AI Backend is running 🚀", "version": "1.0.0"}
```

### Test 2: Upload a PDF and chat with it

1. Open `frontend/index.html` in your browser
2. Click **Student** → fill in signup form → Submit
3. Click **AI Tutor Chat** option card
4. On the left panel, click the upload area and select any PDF (a textbook, notes, etc.)
5. Wait for "✅ PDF processed!" message
6. In the chat box on the right, ask a question from the textbook
7. You should get an AI answer with a green stats pill showing tokens saved!

### Test 3: AI Quiz generation

1. First upload a PDF (see Test 2)
2. Click **Back to Options** → **Quiz Time**
3. Click the **"🤖 AI Quiz from PDF"** tab
4. Click **"Generate Quiz from PDF"**
5. A 5-question multiple-choice quiz should appear!

### Test 4: API documentation

Go to `http://localhost:8000/docs` — you'll see interactive API docs where you can test every endpoint directly in your browser.

### Test 5: Cost stats

Go to `http://localhost:8000/stats` — shows cost optimization strategy details (great for judges!).

---

## 🔧 Common Errors & Fixes

### Error: `ModuleNotFoundError: No module named 'fastapi'`
**Fix:** You didn't install dependencies. Run:
```bash
pip install -r requirements.txt
```

### Error: `ModuleNotFoundError: No module named 'fitz'`
**Fix:** PyMuPDF failed to install. Try:
```bash
pip install pymupdf
```
or
```bash
pip install PyMuPDF
```

### Error: CORS / "Failed to fetch" in browser
**Fix:** Make sure the backend is running! Open `http://localhost:8000` in browser. If it works, the CORS is configured automatically.

### Error: `Address already in use`
**Fix:** Port 8000 is taken. Either stop the other process, or change port:
In `main.py`, change `port=8000` to `port=8001`, then update `BACKEND_URL` in `index.html` to `http://localhost:8001`.

### Error: `502 AI API error` or `504 timeout`
**Fix:** Your Scaledown API key is wrong or the URL is wrong. Double-check:
- The API key in `main.py`
- The `SCALEDOWN_BASE_URL` matches your Scaledown endpoint
- The `SCALEDOWN_MODEL` matches a model you have access to

### Error: PDF uploads but no AI response
**Fix:** Check backend terminal for error messages. Common causes:
- API key not set correctly → you'll see "Demo Mode" response
- Model name wrong → check Scaledown docs for correct model name

### Error: "PDF appears to have no readable text"
**Fix:** Your PDF is a scanned image (not text-based). The current version requires text-based PDFs. Use a digital textbook PDF, not a photo scan.

### The frontend doesn't look right
**Fix:** Make sure you're opening `index.html` from the `frontend/` folder, not from `backend/`.

---

## 📊 Understanding Cost Optimization (For Judges)

When you chat with the AI, each response shows a green badge like:
```
⚡ 4/127 chunks · ~1,847 tokens · 94% cheaper
```

This means:
- The textbook had **127 chunks** total
- We only sent **4 chunks** to the AI (the most relevant ones)
- We used **~1,847 tokens** instead of ~30,000+ (naive approach)
- This is **94% cheaper** than sending the full book

**The caching system:** If the same question is asked twice, the backend returns the cached answer instantly — **0 API tokens used!**

---

## 🌐 API Endpoints Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/upload-pdf` | Upload a PDF textbook |
| POST | `/chat` | Ask a question |
| POST | `/generate-quiz` | Generate quiz from PDF |
| GET | `/documents` | List uploaded documents |
| GET | `/stats` | Show cost optimization stats |

---

## 🎯 Hackathon Pitch Points

1. **Problem:** Students can't query their textbooks. Naive AI tutors are expensive.
2. **Solution:** UDAAN uses context pruning to make AI tutoring 90%+ cheaper.
3. **How:** Smart chunking + TF-IDF relevance scoring + token budgeting + caching.
4. **Result:** Same quality answers, fraction of the cost.
5. **Demo:** Upload any textbook PDF → ask questions → watch the savings badge!

---

## 👩‍💻 Tech Stack

- **Frontend:** Pure HTML, CSS, JavaScript (no frameworks needed!)
- **Backend:** Python + FastAPI
- **PDF Processing:** PyMuPDF (fitz)
- **AI API:** Scaledown (OpenAI-compatible)
- **Retrieval:** Custom TF-IDF scoring (no vector DB needed!)
- **Storage:** In-memory (perfect for hackathon demo)

---

*Built for hackathon — UDAAN: wings to learn ✈*