# Tewahedo AI

Project layout for the Tewahedo AI application.

```
tewahedo-ai/
├── backend/
│   ├── app/                 Application code
│   ├── scripts/             Utility and data scripts
│   ├── data/
│   │   ├── raw/             Original source files
│   │   ├── extracted/       Extracted text and intermediate output
│   │   └── processed/       Cleaned data ready for use
│   ├── tests/               Backend tests
│   └── requirements.txt     Python dependencies
├── frontend/                Client application
├── docker-compose.yml       Local backend and frontend services
└── README.md
```

## Backend

Python service. Dependencies go in `backend/requirements.txt`. Source data moves from `data/raw` through `data/extracted` into `data/processed`.

Document ingestion uses PyMuPDF first and falls back page-by-page to Tesseract
OCR when direct text is missing or unusable. Tesseract must be installed with
the Amharic `amh` language model.

From `backend/`, extract a PDF already stored in `data/raw/`:

```powershell
.\.venv\Scripts\python.exe scripts\extract_pdf.py document.pdf
```

## Groq answers

Answer generation uses the official `groq` Python SDK. The API key stays in a local file that Git ignores. The application reads `GROQ_MODEL` and calls that model id; it does not substitute another model.

Create `backend/.env` yourself and put these lines in it. Replace the placeholders locally. Do not paste the key into chat, source files, or tests:

```
GROQ_API_KEY=your_actual_key_here
GROQ_MODEL=your_selected_model_id
GROQ_TIMEOUT_SECONDS=60
```

`backend/.env.example` shows the same placeholders. Groq's current chat-completions quickstart uses `llama-3.3-70b-versatile`. The models page also lists `llama-3.1-8b-instant`, `openai/gpt-oss-20b`, and `openai/gpt-oss-120b`. Rate limits differ by model and account, so set `GROQ_MODEL` to an id your account can call.

From `backend/`, install the SDK and confirm Git ignores the key file without printing it:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
git check-ignore -v backend/.env
```

`git check-ignore` should name `.gitignore`. It should not ignore `backend/.env.example`.

Start the ingestion API from `backend/`:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Ask one question from `backend/`. The first run loads the local BGE-M3 retrieval model, then sends the top retrieved parent passages to Groq:

```powershell
.\.venv\Scripts\python.exe scripts\answer_question.py "ሰንበትን የማክበር ትእዛዝ መቼ ተሰጠ?"
```

A four-question sample writes `backend/data/evaluation/groq-answer-sample.json` and does not replace the frozen retrieval files:

```powershell
.\.venv\Scripts\python.exe scripts\evaluate_groq_sample.py
```

If Groq rejects the key, the process exits with `authentication`. A rate limit exits with `rate_limit`. An unknown or unavailable model exits with `model_unavailable` and is not replaced. A missing key exits with the message to set `GROQ_API_KEY` in `backend/.env`.

## Frontend

Client application lives in `frontend/`.

## Run with Docker

From the project root, after Dockerfiles exist in `backend/` and `frontend/`:

```bash
docker compose up --build
```
