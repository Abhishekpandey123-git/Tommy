import json
import os
import re
from typing import Literal

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

load_dotenv()

app = FastAPI(title="AI Reading Assistant API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ExplainRequest(BaseModel):
    text: str = Field(min_length=1, max_length=12000)
    language: Literal["hi", "en"] = "hi"
    level: Literal["beginner", "intermediate", "advanced"] = "beginner"

class Word(BaseModel):
    word: str
    meaning: str
    example: str = ""

class ExplainResponse(BaseModel):
    simple_english: str
    hindi: str
    difficult_words: list[Word] = []
    example: str = ""
    confusion_reason: str = ""


def extract_candidates(text: str) -> list[str]:
    words = re.findall(r"[A-Za-z][A-Za-z'-]{5,}", text)
    stop = {"because", "between", "through", "without", "within", "therefore", "however", "although", "should", "would", "could", "which", "these", "those", "their", "about", "important", "system", "method", "methods"}
    seen = set()
    result = []
    for word in words:
        key = word.lower()
        if key not in stop and key not in seen:
            seen.add(key)
            result.append(word)
    return result[:6]


def demo_response(text: str, language: str) -> ExplainResponse:
    candidates = extract_candidates(text)
    words = [Word(word=w, meaning=f"A potentially difficult term from the selected text. Look at its surrounding context to understand its exact meaning.", example=f"Example: The text uses '{w}' as part of its explanation.") for w in candidates]
    hindi = (
        "इसका आसान मतलब समझने के लिए वाक्य को छोटे हिस्सों में पढ़ें। "
        "चयनित टेक्स्ट में कुछ technical या advanced शब्द हो सकते हैं। "
        "Backend में an AI model जोड़ने पर यहाँ exact Hindi explanation आएगी।"
        if language == "hi" else ""
    )
    return ExplainResponse(
        simple_english="This is demo mode. The extension received your selected text successfully, but no LLM API is configured yet. Add an API key in .env to generate a real explanation.",
        hindi=hindi,
        difficult_words=words,
        example="Configure an LLM provider and the same UI will return context-aware explanations.",
        confusion_reason="Technical sentences can be difficult because they combine unfamiliar vocabulary with dense sentence structure and assumptions from earlier text."
    )


async def llm_response(req: ExplainRequest) -> ExplainResponse:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return demo_response(req.text, req.language)

    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    prompt = f"""You are an expert study tutor. Explain the selected text, not unrelated material.
Target learner level: {req.level}.
Return valid JSON with exactly these keys:
- simple_english: concise explanation in simple English
- hindi: natural Hindi explanation, preserving technical terms in English when that is clearer
- difficult_words: array of up to 6 objects with word, meaning, example
- example: one concrete example if useful
- confusion_reason: explain why the text may be difficult (vocabulary, grammar, implied context, etc.)
Selected text:
{req.text}
"""
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a precise educational assistant. Output JSON only."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
    }
    async with httpx.AsyncClient(timeout=45) as client:
        r = await client.post(f"{base_url}/chat/completions", headers={"Authorization": f"Bearer {api_key}"}, json=payload)
    if r.status_code >= 400:
        raise HTTPException(status_code=502, detail=f"LLM provider error: {r.text[:500]}")
    data = r.json()
    content = data["choices"][0]["message"]["content"]
    try:
        parsed = json.loads(content)
        return ExplainResponse(**parsed)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Invalid LLM response: {exc}")


@app.get("/api/health")
def health():
    return {"status": "ok", "llm_configured": bool(os.getenv("OPENAI_API_KEY"))}


@app.post("/api/explain", response_model=ExplainResponse)
async def explain(req: ExplainRequest):
    return await llm_response(req)
