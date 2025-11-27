from celery import Task
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime

from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.document import Document
from app.models.segment import Segment


class ParseDocumentTask(Task):
    """Base task for parsing with error handling."""

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure."""
        db = SessionLocal()
        try:
            document_id = kwargs.get('document_id')
            if document_id:
                document = db.query(Document).filter(Document.id == document_id).first()
                if document:
                    document.status = 'error'
                    db.commit()
        finally:
            db.close()


@celery_app.task(base=ParseDocumentTask, bind=True, name="app.workers.parse_document.parse")
def parse_document(self, document_id: str):
    """
    Parse document and extract segments.

    This worker:
    1. Downloads document from S3
    2. Detects file type
    3. Parses content
    4. Extracts translatable segments
    5. Detects placeholders
    6. Stores segments in database

    Args:
        document_id: Document UUID

    TODO: Implement actual parsers (XML, JSON, CSV, etc.)
    This is a placeholder for the parsing logic.
    """
    db = SessionLocal()

    try:
        # Get document
        document = db.query(Document).filter(Document.id == UUID(document_id)).first()
        if not document:
            raise Exception(f"Document {document_id} not found")

        # Update status
        document.status = 'processing'
        db.commit()

        # TODO: Download file from S3 using document.file_url

        # TODO: Parse based on file_type
        # - XML: Use lxml + defusedxml
        # - JSON: Use json module
        # - CSV: Use csv module
        # - XLIFF: Use lxml
        # - DOCX: Use python-docx
        # - PDF: Use pdfplumber

        # Placeholder: Create sample segments
        sample_segments = [
            {
                "index": 0,
                "source_text": "Sample segment 1",
                "placeholders": [],
                "char_count": 16,
                "word_count": 3
            },
            {
                "index": 1,
                "source_text": "Welcome {user_name}!",
                "placeholders": ["{user_name}"],
                "char_count": 20,
                "word_count": 2
            }
        ]

        # Store segments
        for seg_data in sample_segments:
            segment = Segment(
                document_id=document.id,
                index=seg_data["index"],
                source_text=seg_data["source_text"],
                char_count=seg_data["char_count"],
                word_count=seg_data["word_count"],
                placeholders=seg_data["placeholders"],
                max_length=document.max_segment_length
            )
            db.add(segment)

        # Update document status
        document.status = 'ready'
        db.commit()

        return {
            "document_id": str(document_id),
            "segments_count": len(sample_segments),
            "status": "success"
        }

    except Exception as e:
        document = db.query(Document).filter(Document.id == UUID(document_id)).first()
        if document:
            document.status = 'error'
            db.commit()
        raise

    finally:
        db.close()


@celery_app.task(name="app.workers.parse_document.example_task")
def example_task(x: int, y: int) -> int:
    """
    Example Celery task for testing.

    Args:
        x: First number
        y: Second number

    Returns:
        Sum of x and y
    """
    return x + y
