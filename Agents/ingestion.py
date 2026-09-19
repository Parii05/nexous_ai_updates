"""
NEXUS - Ingestion Agent

Handles document ingestion and indexing.
"""

import os
import tempfile
from pathlib import Path

from rag import upload_pdf


SUPPORTED_EXTENSIONS = {
    ".pdf",
}


def validate_document(file_path: str) -> tuple[bool, str]:
    """
    Validate an uploaded document.
    """

    if not file_path:
        return False, "No file path provided."

    path = Path(file_path)

    if not path.exists():
        return False, "File does not exist."

    if not path.is_file():
        return False, "Provided path is not a file."

    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        return False, "Only PDF documents are currently supported."

    if path.stat().st_size == 0:
        return False, "The uploaded file is empty."

    return True, ""


def ingestion_agent(file_path: str) -> dict:
    """
    Ingest a document into the NEXUS knowledge base.

    The actual PDF extraction, chunking, embedding and Pinecone
    indexing remain inside rag.py.
    """

    valid, error = validate_document(file_path)

    if not valid:
        return {
            "success": False,
            "agent": "ingestion",
            "status": "failed",
            "message": error,
            "filename": os.path.basename(file_path) if file_path else None,
        }

    try:
        upload_pdf(file_path)

        return {
            "success": True,
            "agent": "ingestion",
            "status": "indexed",
            "message": "Document successfully indexed.",
            "filename": os.path.basename(file_path),
        }

    except Exception as exc:
        return {
            "success": False,
            "agent": "ingestion",
            "status": "failed",
            "message": str(exc),
            "filename": os.path.basename(file_path),
        }