from celery import Task
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime

from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.document import Document
from app.models.segment import Segment
from app.models.translation import Translation
from app.models.job import TranslationJob
from app.services.translation_service import translation_service
from app.services.qa_service import qa_service


class TranslateDocumentTask(Task):
    """Base task for translation with error handling."""

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure."""
        db = SessionLocal()
        try:
            job_id = kwargs.get('job_id')
            if job_id:
                job = db.query(TranslationJob).filter(TranslationJob.id == job_id).first()
                if job:
                    job.status = 'failed'
                    job.error_message = str(exc)
                    job.completed_at = datetime.utcnow()
                    db.commit()
        finally:
            db.close()


@celery_app.task(base=TranslateDocumentTask, bind=True, name="app.workers.translate_document.translate")
def translate_document(
    self,
    job_id: str,
    document_id: str,
    target_language: str,
    source_language: str = "auto"
):
    """
    Translate all segments in a document.

    This is the main translation worker that:
    1. Loads all segments for the document
    2. Translates each segment using DeepL
    3. Runs QA checks
    4. Stores translations in database
    5. Updates job progress

    Args:
        job_id: Translation job UUID
        document_id: Document UUID
        target_language: Target language code
        source_language: Source language code (default: auto-detect)
    """
    db = SessionLocal()

    try:
        # Get job
        job = db.query(TranslationJob).filter(TranslationJob.id == UUID(job_id)).first()
        if not job:
            raise Exception(f"Job {job_id} not found")

        # Update job status
        job.status = 'processing'
        job.started_at = datetime.utcnow()
        job.progress = 0
        db.commit()

        # Get document and segments
        document = db.query(Document).filter(Document.id == UUID(document_id)).first()
        if not document:
            raise Exception(f"Document {document_id} not found")

        segments = db.query(Segment).filter(
            Segment.document_id == UUID(document_id),
            Segment.is_locked == False  # Skip locked segments
        ).order_by(Segment.index).all()

        if not segments:
            job.status = 'completed'
            job.progress = 100
            job.completed_at = datetime.utcnow()
            db.commit()
            return

        total_segments = len(segments)
        translated_count = 0

        # TODO: Get glossary for language pair if exists

        # Translate segments in batches for efficiency
        batch_size = 50
        for i in range(0, total_segments, batch_size):
            batch = segments[i:i + batch_size]

            # Extract source texts
            source_texts = [seg.source_text for seg in batch]

            # Translate batch
            try:
                translated_texts = translation_service.translate_batch(
                    texts=source_texts,
                    source_lang=source_language,
                    target_lang=target_language
                )
            except Exception as e:
                # If batch fails, try individual translations
                translated_texts = []
                for text in source_texts:
                    try:
                        result = translation_service.translate_text(
                            text=text,
                            source_lang=source_language,
                            target_lang=target_language
                        )
                        translated_texts.append(result)
                    except:
                        translated_texts.append(text)  # Fallback to original

            # Store translations
            for segment, translated_text in zip(batch, translated_texts):
                # Run QA checks
                qa_result = qa_service.run_full_qa(
                    source_text=segment.source_text,
                    translated_text=translated_text,
                    max_length=segment.max_length
                )

                # Create or update translation
                translation = db.query(Translation).filter(
                    Translation.segment_id == segment.id,
                    Translation.target_language == target_language
                ).first()

                if translation:
                    translation.translated_text = translated_text
                    translation.translation_source = 'ai'
                    translation.length_exceeded = not qa_result['checks']['length']['valid']
                    translation.placeholder_valid = qa_result['checks']['placeholders']['valid']
                    translation.qa_warnings = {
                        "warnings": qa_result['warnings'],
                        "errors": qa_result['errors']
                    }
                else:
                    translation = Translation(
                        segment_id=segment.id,
                        target_language=target_language,
                        translated_text=translated_text,
                        translation_source='ai',
                        length_exceeded=not qa_result['checks']['length']['valid'],
                        placeholder_valid=qa_result['checks']['placeholders']['valid'],
                        qa_warnings={
                            "warnings": qa_result['warnings'],
                            "errors": qa_result['errors']
                        }
                    )
                    db.add(translation)

                translated_count += 1

            # Update progress
            progress = int((translated_count / total_segments) * 100)
            job.progress = progress
            db.commit()

            # Update task state for progress monitoring
            self.update_state(
                state='PROGRESS',
                meta={
                    'current': translated_count,
                    'total': total_segments,
                    'percent': progress
                }
            )

        # Mark job as completed
        job.status = 'completed'
        job.progress = 100
        job.completed_at = datetime.utcnow()
        db.commit()

        # TODO: Add approved translations to Translation Memory

    except Exception as e:
        # Update job with error
        job = db.query(TranslationJob).filter(TranslationJob.id == UUID(job_id)).first()
        if job:
            job.status = 'failed'
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            db.commit()
        raise

    finally:
        db.close()
