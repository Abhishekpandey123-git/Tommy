# AI Reading Assistant — v0.1

A Chrome/Edge Manifest V3 extension that lets you select difficult text and receive:

- Simple English explanation
- Hindi explanation
- Difficult-word meanings
- Example
- Why the text may be confusing

## Project structure

```text
ai-reading-assistant/
├── extension/       # Chrome/Edge extension
├── backend/         # FastAPI API
└── README.md
```

## 1. Start backend

Windows PowerShell:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python run.py
```

The API runs at `http://127.0.0.1:8000`.

### Optional: connect an LLM

Edit `backend/.env`:

```env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
```

You can also point `OPENAI_BASE_URL` at another OpenAI-compatible provider.

Without an API key, the project runs in demo mode so you can test the extension end-to-end.

## 2. Load extension

Chrome/Edge:

1. Open the extensions page.
2. Enable **Developer mode**.
3. Choose **Load unpacked**.
4. Select the `extension` folder.
5. Open any webpage.
6. Select a sentence.
7. Right-click → **Explain with AI Reading Assistant**.

## 3. Test backend

Open:

`http://127.0.0.1:8000/api/health`

Expected response:

```json
{"status":"ok","llm_configured":false}
```

## Next versions

- Streaming responses
- Word-only quick definition
- Paragraph summarization
- Keyboard shortcut
- Local Ollama/llama.cpp mode
- Personal vocabulary history
- Spaced repetition
- Context from surrounding paragraphs
- Page-level "teach me this chapter" mode
