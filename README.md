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

## Frontend

Client application lives in `frontend/`.

## Run with Docker

From the project root, after Dockerfiles exist in `backend/` and `frontend/`:

```bash
docker compose up --build
```
