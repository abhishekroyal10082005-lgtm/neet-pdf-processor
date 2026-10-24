from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    queued = "queued"
    processing = "processing"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class JobSettings(BaseModel):
    deblur: bool = True
    denoise: bool = True
    contrast: bool = True
    sharpen: bool = True
    deskew: bool = True
    background_normalization: bool = True
    quality: int = 2
    output_dpi: int = 300
    allow_watermark_cleanup: bool = False
    preview_only: bool = False


class FileRecord(BaseModel):
    id: str
    original_name: str
    file_type: str
    size_bytes: int
    storage_path: str
    created_at: str


class ProcessingJob(BaseModel):
    id: str
    name: str
    file_id: str
    file_name: str
    status: JobStatus = JobStatus.queued
    total_pages: int = 0
    completed_pages: int = 0
    failed_pages: int = 0
    progress_percent: int = 0
    created_at: str
    updated_at: str
    output_file: Optional[str] = None
    error_message: Optional[str] = None
    settings: JobSettings = Field(default_factory=JobSettings)
    processing_started_at: Optional[str] = None
    processing_completed_at: Optional[str] = None
    estimated_remaining_minutes: Optional[int] = None
