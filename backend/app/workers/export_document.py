from celery import Task
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime

from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.document import Document
from app.models.segment import Segment
from app.models.translation import Translation
from app.services.file_parser import file_parser, FileType
from app.services.storage_service import StorageService


class ExportDocumentTask(Task):
    """Base task for export with error handling."""
    pass


@celery_app.task(base=ExportDocumentTask, name="app.workers.export_document.export")
def export_document(
    document_id: str,
    target_language: str,
    export_format: str = "original"
):
    """
    Export translated document.

    This worker:
    1. Loads document and translations
    2. Reconstructs file in original format
    3. Preserves structure (tags, formatting)
    4. Uploads to S3
    5. Returns download URL

    Args:
        document_id: Document UUID
        target_language: Target language code
        export_format: Export format (original, xliff, tmx)

    Returns:
        Dict with export URL
    """
    db = SessionLocal()
    storage = StorageService()

    try:
        # Get document
        document = db.query(Document).filter(Document.id == UUID(document_id)).first()
        if not document:
            raise Exception(f"Document {document_id} not found")

        # Get segments and translations
        segments = db.query(Segment).filter(
            Segment.document_id == document.id
        ).order_by(Segment.index).all()

        # Build translations map using segment_key (not segment.id)
        translations = {}
        for segment in segments:
            trans = db.query(Translation).filter(
                Translation.segment_id == segment.id,
                Translation.target_language == target_language
            ).first()

            if trans and segment.segment_key:
                # Use segment_key as the identifier for export
                translations[segment.segment_key] = trans.translated_text

        if not translations:
            raise Exception(f"No translations found for language '{target_language}'")

        # Download original file from S3
        original_content_bytes = storage.download_file(document.file_key)
        original_content = original_content_bytes.decode('utf-8')

        # Export based on format
        if export_format == "original":
            # Reconstruct in original format
            exported_content = file_parser.export_file(
                filename=document.filename,
                original_content=original_content,
                translations=translations,
                target_language=target_language
            )

            # Generate export filename
            name_parts = document.filename.rsplit('.', 1)
            if len(name_parts) == 2:
                export_filename = f"{name_parts[0]}_{target_language}.{name_parts[1]}"
            else:
                export_filename = f"{document.filename}_{target_language}"

        elif export_format == "xliff":
            # Export as XLIFF 1.2
            exported_content = file_parser.create_xliff_from_file(
                filename=document.filename,
                content=original_content,
                source_language=document.source_language,
                target_language=target_language
            )
            export_filename = f"{document.filename.rsplit('.', 1)[0]}_{target_language}.xliff"

        else:
            raise ValueError(f"Unsupported export format: {export_format}")

        # Upload to S3
        export_key = f"exports/{document.project_id}/{document.id}/{export_filename}"
        upload_result = storage.upload_file(
            export_key,
            exported_content.encode('utf-8'),
            content_type='application/xml' if export_format == 'xliff' else None
        )

        # Generate download URL (valid for 24 hours)
        download_url = storage.generate_presigned_download_url(
            export_key,
            expiration=86400  # 24 hours
        )

        return {
            "document_id": str(document_id),
            "target_language": target_language,
            "export_format": export_format,
            "filename": export_filename,
            "download_url": download_url,
            "segments_count": len(segments),
            "translated_count": len(translations),
            "status": "success"
        }

    except Exception as e:
        return {
            "document_id": str(document_id),
            "status": "error",
            "error": str(e)
        }

    finally:
        db.close()
