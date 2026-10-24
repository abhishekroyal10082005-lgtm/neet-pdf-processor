from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

from app.models import FileRecord, JobSettings, JobStatus, ProcessingJob
from app.storage_db import (
    DB_PATH,
    ensure_storage,
    get_connection,
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

# Compatibility wrapper to keep the import surface simple.
__all__ = [
    "DB_PATH",
    "OUTPUTS_DIR",
    "UPLOADS_DIR",
    "ensure_storage",
    "get_connection",
    "init_db",
    "insert_file_record",
    "list_files",
    "get_file_record",
    "insert_job_record",
    "get_job",
    "update_job",
    "list_jobs",
    "get_storage_path_for_file",
    "get_output_path_for_job",
    "utc_now",
]

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = BASE_DIR / "storage" / "uploads"
OUTPUTS_DIR = BASE_DIR / "storage" / "outputs"
