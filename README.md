# CleanScan AI

Production-oriented MVP for a document restoration and PDF enhancement platform.

Built as a working local-stack prototype with:

- React + TypeScript frontend
- FastAPI backend
- SQLite persistence for jobs and uploads
- Real PDF processing with PyMuPDF, OpenCV, Pillow
- Background job execution and progress tracking
- Before/after page preview metadata
- Downloadable processed PDFs

## Quick start

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

## Default URLs

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs

## Features implemented

- Upload PDF or image
- Background asynchronous processing
- Job persistence and workflow tracking
- Page-level progress
- Automatic restoration pipeline (contrast, sharpening, blur cleaning, grayscale normalization, margin cleanup hints)
- Final PDF reconstruction and validation
- Dashboard and processing history UI
- Settings panel with enhancement configuration
- Download final processed PDF

## External capabilities not included by default

These are clearly separated as optional model integrations:

- OCR-based readability analysis using Azure Document Intelligence / Google Vision / Tesseract
- Advanced watermark detection and inpainting using CV models
- Large-scale cloud queue workers (Celery/RQ/Cloud Run)
- Firebase Authentication integration
- Object storage integration (S3, GCS, Azure Blob)

## Important notes

This MVP is intentionally honest about capacity. It does not claim unbounded processing. It uses local infrastructure and concurrency appropriate for a single deploy environment.
