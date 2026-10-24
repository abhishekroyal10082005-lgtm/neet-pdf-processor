from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.models import FileRecord, JobSettings, JobStatus, ProcessingJob

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = BASE_DIR / "storage" / "uploads"
OUTPUTS_DIR = BASE_DIR / "storage" / "outputs"
DB_PATH = DATA_DIR / "cleanscan.db"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_storage() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    ensure_storage()
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS files (
                id TEXT PRIMARY KEY,
                original_name TEXT NOT NULL,
                file_type TEXT NOT NULL,
                size_bytes INTEGER NOT NULL,
                storage_path TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                file_id TEXT NOT NULL,
                file_name TEXT NOT NULL,
                status TEXT NOT NULL,
                total_pages INTEGER NOT NULL DEFAULT 0,
                completed_pages INTEGER NOT NULL DEFAULT 0,
                failed_pages INTEGER NOT NULL DEFAULT 0,
                progress_percent INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                output_file TEXT,
                error_message TEXT,
                settings TEXT NOT NULL,
                processing_started_at TEXT,
                processing_completed_at TEXT,
                estimated_remaining_minutes INTEGER,
                FOREIGN KEY(file_id) REFERENCES files(id)
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def insert_file_record(file_record: FileRecord) -> None:
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO files (id, original_name, file_type, size_bytes, storage_path, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (file_record.id, file_record.original_name, file_record.file_type, file_record.size_bytes,
             file_record.storage_path, file_record.created_at),
        )
        conn.commit()
    finally:
        conn.close()


def list_files() -> List[FileRecord]:
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM files ORDER BY created_at DESC").fetchall()
        return [
            FileRecord(
                id=row["id"],
                original_name=row["original_name"],
                file_type=row["file_type"],
                size_bytes=row["size_bytes"],
                storage_path=row["storage_path"],
                created_at=row["created_at"],
            )
            for row in rows
        ]
    finally:
        conn.close()


def get_file_record(file_id: str) -> Optional[FileRecord]:
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM files WHERE id = ?", (file_id,)).fetchone()
        if row is None:
            return None
        return FileRecord(
            id=row["id"],
            original_name=row["original_name"],
            file_type=row["file_type"],
            size_bytes=row["size_bytes"],
            storage_path=row["storage_path"],
            created_at=row["created_at"],
        )
    finally:
        conn.close()


def insert_job_record(job: ProcessingJob) -> None:
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO jobs (
                id, name, file_id, file_name, status, total_pages, completed_pages, failed_pages,
                progress_percent, created_at, updated_at, output_file, error_message, settings,
                processing_started_at, processing_completed_at, estimated_remaining_minutes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                job.id,
                job.name,
                job.file_id,
                job.file_name,
                job.status.value,
                job.total_pages,
                job.completed_pages,
                job.failed_pages,
                job.progress_percent,
                job.created_at,
                job.updated_at,
                job.output_file,
                job.error_message,
                json.dumps(job.settings.model_dump()),
                job.processing_started_at,
                job.processing_completed_at,
                job.estimated_remaining_minutes,
            ),
        )
        conn.commit()
    finally:
        conn.close()


def get_job(job_id: str) -> Optional[ProcessingJob]:
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        if row is None:
            return None
        return ProcessingJob(
            id=row["id"],
            name=row["name"],
            file_id=row["file_id"],
            file_name=row["file_name"],
            status=JobStatus(row["status"]),
            total_pages=row["total_pages"],
            completed_pages=row["completed_pages"],
            failed_pages=row["failed_pages"],
            progress_percent=row["progress_percent"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            output_file=row["output_file"],
            error_message=row["error_message"],
            settings=JobSettings(**json.loads(row["settings"])),
            processing_started_at=row["processing_started_at"],
            processing_completed_at=row["processing_completed_at"],
            estimated_remaining_minutes=row["estimated_remaining_minutes"],
        )
    finally:
        conn.close()


def update_job(job: ProcessingJob) -> None:
    conn = get_connection()
    try:
        conn.execute(
            """
            UPDATE jobs
            SET name = ?, file_id = ?, file_name = ?, status = ?, total_pages = ?, completed_pages = ?,
                failed_pages = ?, progress_percent = ?, updated_at = ?, output_file = ?, error_message = ?,
                settings = ?, processing_started_at = ?, processing_completed_at = ?, estimated_remaining_minutes = ?
            WHERE id = ?
            """,
            (
                job.name,
                job.file_id,
                job.file_name,
                job.status.value,
                job.total_pages,
                job.completed_pages,
                job.failed_pages,
                job.progress_percent,
                job.updated_at,
                job.output_file,
                job.error_message,
                json.dumps(job.settings.model_dump()),
                job.processing_started_at,
                job.processing_completed_at,
                job.estimated_remaining_minutes,
                job.id,
            ),
        )
        conn.commit()
    finally:
        conn.close()


def list_jobs() -> List[ProcessingJob]:
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM jobs ORDER BY created_at DESC").fetchall()
        jobs: List[ProcessingJob] = []
        for row in rows:
            jobs.append(
                ProcessingJob(
                    id=row["id"],
                    name=row["name"],
                    file_id=row["file_id"],
                    file_name=row["file_name"],
                    status=JobStatus(row["status"]),
                    total_pages=row["total_pages"],
                    completed_pages=row["completed_pages"],
                    failed_pages=row["failed_pages"],
                    progress_percent=row["progress_percent"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                    output_file=row["output_file"],
                    error_message=row["error_message"],
                    settings=JobSettings(**json.loads(row["settings"])),
                    processing_started_at=row["processing_started_at"],
                    processing_completed_at=row["processing_completed_at"],
                    estimated_remaining_minutes=row["estimated_remaining_minutes"],
                )
            )
        return jobs
    finally:
        conn.close()


def get_storage_path_for_file(file_name: str) -> str:
    return str(UPLOADS_DIR / file_name)


def get_output_path_for_job(job_id: str) -> str:
    return str(OUTPUTS_DIR / f"{job_id}.pdf")
