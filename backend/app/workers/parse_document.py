from celery import Task
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
import hashlib

from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.document import Document
from app.models.segment import Segment
from app.services.file_parser import file_parser, FileType
from app.services.storage_service import StorageService


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
    """
    db = SessionLocal()
    storage = StorageService()

    try:
        # Get document
        document = db.query(Document).filter(Document.id == UUID(document_id)).first()
        if not document:
            raise Exception(f"Document {document_id} not found")

        # Update status
        document.status = 'processing'
        db.commit()

        # Download file from S3
        file_content = storage.download_file(document.file_key)

        # Convert bytes to string for text-based formats
        try:
            content_str = file_content.decode('utf-8')
        except UnicodeDecodeError:
            # Try other encodings
            try:
                content_str = file_content.decode('latin-1')
            except:
                raise ValueError("Unable to decode file content")

        # Parse file
        parsed_segments, metadata = file_parser.parse_file(
            filename=document.filename,
            content=content_str,
            file_type=None  # Auto-detect
        )

        # Update document with metadata
        document.file_metadata = metadata

        # Store segments in database
        for index, parsed_seg in enumerate(parsed_segments):
            # Calculate hash for TM matching
            source_hash = hashlib.md5(
                parsed_seg.source_text.encode('utf-8')
            ).hexdigest()

            # Count words (simple split by whitespace)
            word_count = len(parsed_seg.source_text.split())
            char_count = len(parsed_seg.source_text)

            segment = Segment(
                document_id=document.id,
                index=index,
                segment_key=parsed_seg.segment_id,
                source_text=parsed_seg.source_text,
                context=parsed_seg.context,
                source_hash=source_hash,
                char_count=char_count,
                word_count=word_count,
                placeholders=parsed_seg.placeholders,
                max_length=parsed_seg.max_length or document.max_segment_length,
                is_locked=parsed_seg.metadata.get('is_locked', False)
            )
            db.add(segment)

        # Update document status
        document.status = 'ready'
        document.segments_count = len(parsed_segments)
        db.commit()

        return {
            "document_id": str(document_id),
            "segments_count": len(parsed_segments),
            "file_type": metadata.get('file_type'),
            "status": "success"
        }

    except Exception as e:
        # Update document status to error
        try:
            document = db.query(Document).filter(Document.id == UUID(document_id)).first()
            if document:
                document.status = 'error'
                document.error_message = str(e)
                db.commit()
        except:
            pass
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
