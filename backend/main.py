"""
UDAAN AI Tutoring Backend
=========================
Scaledown diye context compress kore, Groq (free!) diye AI answer dao.
"""

import os
import re
import json
import hashlib
import time
from typing import Optional
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx

try:
    import fitz
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("WARNING: PyMuPDF not installed. Run: pip install pymupdf")

app = FastAPI(title="UDAAN AI Tutoring API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SCALEDOWN_API_KEY = "Mj3Gew2ryF8stpb2d1XFS4ImruvaV1oFx4GG0gAi"

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "") 

# ────────────────────────────────────────────────────────────────────

CHUNK_SIZE      = 400
CHUNK_OVERLAP   = 50
TOP_K_CHUNKS    = 4

document_store  = {}
response_cache  = {}


class ChatRequest(BaseModel):
    doc_id: str
    question: str
    student_name: Optional[str] = "Student"

class QuizRequest(BaseModel):
    doc_id: str
    num_questions: int = 5


def chunk_text(text: str) -> list:
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        end = min(i + CHUNK_SIZE, len(words))
        chunk = " ".join(words[i:end])
        if len(chunk.strip()) > 50:
            chunks.append(chunk.strip())
        i += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


def compute_relevance_score(query: str, chunk: str) -> float:
    stop_words = {"the","a","an","is","are","was","were","be","been",
                  "what","how","why","when","where","which","who",
                  "in","on","at","to","for","of","and","or","but","it","this","that"}
    query_words = [w for w in re.findall(r'\b\w+\b', query.lower()) if w not in stop_words and len(w) > 2]
    if not query_words:
        return 0.0
    chunk_lower = chunk.lower()
    hits = sum(1 for w in query_words if w in chunk_lower)
    if query.lower().strip() in chunk_lower:
        hits += len(query_words)
    length_penalty = min(1.0, 300 / max(len(chunk.split()), 1))
    return (hits / len(query_words)) * length_penalty


def prune_context(chunks: list, max_chars: int = 7200) -> list:
    pruned = []
    total = 0
    for chunk in chunks:
        if total + len(chunk) <= max_chars:
            pruned.append(chunk)
            total += len(chunk)
        else:
            remaining = max_chars - total
            if remaining > 200:
                pruned.append(chunk[:remaining] + "...")
            break
    return pruned


async def call_ai_api(system_prompt: str, user_message: str) -> str:
    # STEP 1: Scaledown compression
    compressed_context = user_message

    try:
        async with httpx.AsyncClient(timeout=20, verify=False) as client:
            r = await client.post(
                "https://api.scaledown.xyz/compress/raw/",
                headers={
                    "x-api-key": SCALEDOWN_API_KEY,
                    "Content-Type": "application/json"
                },
                json={
                    "context": user_message,
                    "prompt": system_prompt,
                    "scaledown": {"rate": "auto"}
                }
            )
            data = r.json()
            if data.get("successful"):
                compressed_context = data["compressed_prompt"]
                print(f"Scaledown: {data.get('original_prompt_tokens')} -> {data.get('compressed_prompt_tokens')} tokens!")
            else:
                print("Scaledown failed, using original")
    except Exception as e:
        print(f"Scaledown error: {e}")

    # STEP 2: Groq API
    try:
        async with httpx.AsyncClient(timeout=30, verify=False) as client:
            r = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user",   "content": compressed_context}
                    ],
                    "max_tokens": 600,
                    "temperature": 0.3
                }
            )
            result = r.json()
            if "choices" in result:
                return result["choices"][0]["message"]["content"]
            else:
                raise HTTPException(status_code=500, detail=f"Groq error: {result}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI error: {str(e)}")


@app.get("/")
def root():
    return {"status": "UDAAN AI Backend is running"}


@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    if not PDF_AVAILABLE:
        raise HTTPException(status_code=500, detail="PyMuPDF not installed.")
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files supported.")

    pdf_bytes = await file.read()
    doc_id = hashlib.md5(pdf_bytes[:1000] + file.filename.encode()).hexdigest()[:12]

    if doc_id in document_store:
        info = document_store[doc_id]
        return {
            "doc_id": doc_id,
            "filename": file.filename,
            "pages": info["metadata"]["pages"],
            "chunks": info["metadata"]["num_chunks"],
            "status": "already_processed",
            "message": f"Already loaded! {info['metadata']['num_chunks']} chunks ready."
        }

    try:
        pdf_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        full_text = ""
        page_count = len(pdf_doc)
        for i in range(page_count):
            page_text = pdf_doc[i].get_text()
            page_text = re.sub(r'\s+', ' ', page_text)
            full_text += f"\n[Page {i+1}]\n" + page_text
        pdf_doc.close()
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"PDF read error: {str(e)}")

    if len(full_text.strip()) < 100:
        raise HTTPException(status_code=422, detail="PDF has no readable text.")

    chunks = chunk_text(full_text)
    document_store[doc_id] = {
        "filename": file.filename,
        "chunks":   chunks,
        "metadata": {
            "pages":      page_count,
            "num_chunks": len(chunks),
            "uploaded_at": time.time(),
        }
    }

    return {
        "doc_id":   doc_id,
        "filename": file.filename,
        "pages":    page_count,
        "chunks":   len(chunks),
        "status":   "success",
        "message":  f"PDF processed! {len(chunks)} chunks from {page_count} pages."
    }


@app.post("/chat")
async def chat(req: ChatRequest):
    if req.doc_id not in document_store:
        raise HTTPException(status_code=404, detail="Document not found. Upload PDF first.")
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    cache_key = hashlib.md5(f"{req.doc_id}:{req.question.lower().strip()}".encode()).hexdigest()
    if cache_key in response_cache:
        return {**response_cache[cache_key], "from_cache": True}

    doc        = document_store[req.doc_id]
    all_chunks = doc["chunks"]

    scored = sorted(
        [(c, compute_relevance_score(req.question, c)) for c in all_chunks],
        key=lambda x: x[1], reverse=True
    )
    top_chunks = [c for c, s in scored[:TOP_K_CHUNKS] if s > 0] or [c for c, _ in scored[:2]]
    pruned     = prune_context(top_chunks)
    context    = "\n\n---\n\n".join(pruned)

    approx_used  = int(len(context.split()) * 1.3) + int(len(req.question.split()) * 1.3)
    approx_naive = int(len(" ".join(all_chunks).split()) * 1.3)
    savings      = max(0, int((1 - approx_used / max(approx_naive, 1)) * 100))

    system_prompt = (
        "You are UDAAN, a friendly AI tutor for rural Indian students "
        "helping " + req.student_name + " understand NCERT/State Board curriculum. "
        "RULES: "
        "1. Answer ONLY from the provided textbook context. "
        "2. Give curriculum-aligned answers in simple language for Class 8-12 students. "
        "3. Address " + req.student_name + " by name and be encouraging. "
        "4. Structure: define concept, then explain, then give a real-life example. "
        "5. Keep answers concise (3-6 sentences) to save bandwidth for rural users. "
        "6. If not in context say: This topic is not in your uploaded material. "
        "7. End with one encouraging line for " + req.student_name + "."
    )

    user_message = f"""TEXTBOOK CONTEXT:
{context}

STUDENT QUESTION: {req.question}"""

    answer = await call_ai_api(system_prompt, user_message)

    result = {
        "answer":     answer,
        "doc_id":     req.doc_id,
        "filename":   doc["filename"],
        "from_cache": False,
        "cost_stats": {
            "chunks_total":        len(all_chunks),
            "chunks_used":         len(pruned),
            "approx_tokens_used":  approx_used,
            "approx_tokens_naive": approx_naive,
            "savings_percent":     savings,
        }
    }
    response_cache[cache_key] = result
    return result


@app.post("/generate-quiz")
async def generate_quiz(req: QuizRequest):
    if req.doc_id not in document_store:
        raise HTTPException(status_code=404, detail="Document not found.")

    chunks  = document_store[req.doc_id]["chunks"]
    step    = max(1, len(chunks) // 8)
    sample  = chunks[::step][:4]
    context = "\n\n".join(sample)

    system_prompt = """You are a quiz generator. Return ONLY valid JSON, no extra text:
{
  "questions": [
    {
      "question": "...",
      "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "correct": "A",
      "explanation": "..."
    }
  ]
}"""

    user_message = f"Generate {req.num_questions} MCQ questions from:\n\n{context}"
    ai_response  = await call_ai_api(system_prompt, user_message)

    try:
        cleaned   = re.sub(r'```json|```', '', ai_response).strip()
        quiz_data = json.loads(cleaned)
        return {"status": "success", "quiz": quiz_data["questions"]}
    except Exception:
        return {"status": "partial", "raw_response": ai_response}


@app.get("/stats")
def stats():
    return {
        "documents": len(document_store),
        "cached_responses": len(response_cache),
        "cost_strategy": f"Top {TOP_K_CHUNKS} chunks + Scaledown compression + caching"
    }


if __name__ == "__main__":
    import uvicorn
    print("\nUDAN Backend starting...")
    print("API docs: http://localhost:8000/docs\n")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)