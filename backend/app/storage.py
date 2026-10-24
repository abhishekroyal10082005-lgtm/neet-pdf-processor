from __future__ import annotations

import asyncio
import os
import shutil
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

import uvicorn
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.models import FileRecord, JobSettings, JobStatus, ProcessingJob
from app.processor import process_pdf_file
from app.storage import (
    DB_PATH,
    OUTPUTS_DIR,
    UPLOADS_DIR,
    get_file_record,
    get_job,
    get_output_path_for_job,
    get_storage_path_for_file,
    init_db,
    insert_file_record,
    insert_job_record,
    list_files,
    list_jobs,
    update_job,
    utc_now,
)


class CreateJobRequest(BaseModel):
    file_id: str
    name: str
    settings: JobSettings = JobSettings()


class JobProgressUpdate(BaseModel):
    status: Optional[str] = None
    progress: Optional[int] = None
    error: Optional[str] = None


class AppState:
    def __init__(self) -> None:
        self.processing_tasks: dict[str, asyncio.Task] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="CleanScan AI API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
state = AppState()


async def process_job_async(job_id: str) -> None:
    job = get_job(job_id)
    if job is None:
        return

    file_record = get_file_record(job.file_id)
    if file_record is None:
        job.status = JobStatus.failed
        job.error_message = "Source file not found."
        job.updated_at = utc_now()
        update_job(job)
        return

    input_path = file_record.storage_path
    output_path = get_output_path_for_job(job.id)
    job.status = JobStatus.processing
    job.processing_started_at = utc_now()
    job.updated_at = utc_now()
    update_job(job)

    try:
        total_pages = 0
        if file_record.file_type.lower() in {"pdf"}:
            import fitz

            with fitz.open(input_path) as doc:
                total_pages = doc.page_count
        else:
            total_pages = 1

        job.total_pages = total_pages
        job.updated_at = utc_now()
        update_job(job)

        def progress_callback(current_page: int, total: int, percent: int) -> None:
            job = get_job(job_id)
            if job is None:
                return
            job.completed_pages = current_page
            job.progress_percent = percent
            job.estimated_remaining_minutes = max(0, int(((total - current_page) / max(current_page, 1)) * 0.1))
            job.updated_at = utc_now()
            update_job(job)

        process_pdf_file(input_path, output_path, job.settings, progress_callback=progress_callback)

        job.status = JobStatus.completed
        job.completed_pages = job.total_pages
        job.progress_percent = 100
        job.output_file = output_path
        job.processing_completed_at = utc_now()
        job.updated_at = utc_now()
        job.error_message = None
        update_job(job)
    except Exception as exc:
        job.status = JobStatus.failed
        job.error_message = str(exc)
        job.failed_pages = max(1, job.failed_pages)
        job.updated_at = utc_now()
        update_job(job)


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok", "message": "CleanScan AI backend is running."}


@app.get("/api/files")
async def list_uploaded_files() -> list[dict]:
    return [
        {
            "id": item.id,
            "name": item.original_name,
            "type": item.file_type,
            "sizeBytes": item.size_bytes,
            "createdAt": item.created_at,
        }
        for item in list_files()
    ]


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)) -> dict:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required.")

    file_id = str(uuid.uuid4())
    upload_file_name = f"{file_id}_{file.filename}"
    storage_path = os.path.join(UPLOADS_DIR, upload_file_name)

    with open(storage_path, "wb") as dst:
        shutil.copyfileobj(file.file, dst)

    file_record = FileRecord(
        id=file_id,
        original_name=file.filename,
        file_type=(file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "unknown"),
        size_bytes=os.path.getsize(storage_path),
        storage_path=storage_path,
        created_at=utc_now(),
    )
    insert_file_record(file_record)
    return {"id": file_id, "name": file.filename, "storagePath": storage_path}


@app.post("/api/jobs")
async def create_job(payload: CreateJobRequest) -> ProcessingJob:
    file_record = get_file_record(payload.file_id)
    if file_record is None:
        raise HTTPException(status_code=404, detail="File not found.")

    job_id = str(uuid.uuid4())
    job = ProcessingJob(
        id=job_id,
        name=payload.name,
        file_id=payload.file_id,
        file_name=file_record.original_name,
        status=JobStatus.queued,
        total_pages=0,
        completed_pages=0,
        failed_pages=0,
        progress_percent=0,
        created_at=utc_now(),
        updated_at=utc_now(),
        output_file=None,
        error_message=None,
        settings=payload.settings,
    )
    insert_job_record(job)
    task = asyncio.create_task(process_job_async(job_id))
    state.processing_tasks[job_id] = task
    return job


@app.get("/api/jobs")
async def get_jobs() -> list[ProcessingJob]:
    return list_jobs()


@app.get("/api/jobs/{job_id}")
async def get_job_detail(job_id: str) -> ProcessingJob:
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job


@app.get("/api/jobs/{job_id}/download")
async def download_job_result(job_id: str):
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found.")
    if job.output_file is None or not os.path.exists(job.output_file):
        raise HTTPException(status_code=404, detail="Processed file not available yet.")
    return FileResponse(job.output_file, media_type="application/pdf", filename=f"{job.file_name}.processed.pdf")


@app.delete("/api/jobs/{job_id}")
async def cancel_job(job_id: str) -> dict:
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found.")
    if job.status in {JobStatus.completed, JobStatus.failed, JobStatus.cancelled}:
        return {"message": "Job already terminal."}

    task = state.processing_tasks.get(job_id)
    if task is not None:
        task.cancel()

    job.status = JobStatus.cancelled
    job.updated_at = utc_now()
    update_job(job)
    return {"message": "Job cancelled."}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
