"""
Unified file parsing service.

Coordinates different file format parsers and provides a consistent interface
for the translation workflow.

Supported formats:
- XML (generic, Android strings.xml)
- JSON (flat, nested, i18n)
- CSV (key-value, multi-column)
- XLIFF (1.2, 2.0)
"""

from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import mimetypes

from app.services.xml_handler import XMLHandler, XMLSegment
from app.services.json_handler import JSONHandler, JSONSegment
from app.services.csv_handler import CSVHandler, CSVSegment
from app.services.xliff_handler import XLIFFHandler, XLIFFSegment


class FileType(str, Enum):
    """Supported file types for translation."""
    ANDROID_XML = "android_xml"
    IOS_STRINGS = "ios_strings"
    GENERIC_XML = "generic_xml"
    JSON = "json"
    I18N_JSON = "i18n_json"
    CSV = "csv"
    XLIFF_12 = "xliff_12"
    XLIFF_20 = "xliff_20"
    UNKNOWN = "unknown"


class ParsedSegment:
    """Unified segment representation across all file types."""

    def __init__(
        self,
        segment_id: str,
        source_text: str,
        context: Optional[str] = None,
        placeholders: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        target_text: Optional[str] = None,
        max_length: Optional[int] = None
    ):
        self.segment_id = segment_id
        self.source_text = source_text
        self.context = context
        self.placeholders = placeholders or []
        self.metadata = metadata or {}
        self.target_text = target_text
        self.max_length = max_length


class FileParser:
    """Main file parser service that coordinates all format handlers."""

    def __init__(self):
        self.xml_handler = XMLHandler()
        self.json_handler = JSONHandler()
        self.csv_handler = CSVHandler()
        self.xliff_handler = XLIFFHandler()

    def detect_file_type(self, filename: str, content: str) -> FileType:
        """
        Auto-detect file type from filename and content.

        Args:
            filename: Original filename
            content: File content as string

        Returns:
            Detected FileType enum
        """
        # Check by extension first
        lower_filename = filename.lower()

        if lower_filename.endswith('.xlf') or lower_filename.endswith('.xliff'):
            version = self.xliff_handler.detect_xliff_version(content)
            if version == '1.2':
                return FileType.XLIFF_12
            elif version == '2.0':
                return FileType.XLIFF_20
            return FileType.XLIFF_12  # Default to 1.2

        if lower_filename.endswith('.json'):
            # Try to detect i18n format (has locale keys at root level)
            try:
                import json
                data = json.loads(content)
                if isinstance(data, dict):
                    # Check if top-level keys look like locale codes
                    top_keys = list(data.keys())
                    if all(len(k) == 2 or len(k) == 5 and '-' in k for k in top_keys[:5]):
                        return FileType.I18N_JSON
            except:
                pass
            return FileType.JSON

        if lower_filename.endswith('.csv'):
            return FileType.CSV

        if lower_filename.endswith('.xml'):
            # Detect Android strings.xml
            if 'strings.xml' in lower_filename or '<resources>' in content[:500]:
                return FileType.ANDROID_XML
            return FileType.GENERIC_XML

        if lower_filename.endswith('.strings'):
            return FileType.IOS_STRINGS

        # Content-based detection
        content_preview = content[:1000].strip()

        if content_preview.startswith('<?xml') or content_preview.startswith('<'):
            if '<xliff' in content_preview:
                version = self.xliff_handler.detect_xliff_version(content)
                return FileType.XLIFF_12 if version == '1.2' else FileType.XLIFF_20
            elif '<resources>' in content_preview:
                return FileType.ANDROID_XML
            return FileType.GENERIC_XML

        if content_preview.startswith('{') or content_preview.startswith('['):
            return FileType.JSON

        # Check for CSV patterns
        if ',' in content[:200] or ';' in content[:200] or '\t' in content[:200]:
            return FileType.CSV

        return FileType.UNKNOWN

    def parse_file(
        self,
        filename: str,
        content: str,
        file_type: Optional[FileType] = None,
        **kwargs
    ) -> Tuple[List[ParsedSegment], Dict[str, Any]]:
        """
        Parse file and extract translatable segments.

        Args:
            filename: Original filename
            content: File content as string
            file_type: Optional explicit file type (auto-detect if None)
            **kwargs: Additional parser-specific options

        Returns:
            Tuple of (segments list, metadata dict)

        Raises:
            ValueError: If file type is unsupported or parsing fails
        """
        # Auto-detect if not specified
        if file_type is None:
            file_type = self.detect_file_type(filename, content)

        if file_type == FileType.UNKNOWN:
            raise ValueError(f"Unknown file type for '{filename}'")

        # Route to appropriate parser
        if file_type == FileType.ANDROID_XML:
            segments, metadata = self.xml_handler.parse_android_xml(content)
            return self._convert_xml_segments(segments), metadata

        elif file_type == FileType.GENERIC_XML:
            segments, metadata = self.xml_handler.parse_generic_xml(content)
            return self._convert_xml_segments(segments), metadata

        elif file_type == FileType.JSON:
            segments, metadata = self.json_handler.parse_json(content)
            return self._convert_json_segments(segments), metadata

        elif file_type == FileType.I18N_JSON:
            source_locale = kwargs.get('source_locale', 'en')
            segments, metadata = self.json_handler.parse_i18n_json(content, source_locale)
            return self._convert_json_segments(segments), metadata

        elif file_type == FileType.CSV:
            key_column = kwargs.get('key_column', 0)
            text_columns = kwargs.get('text_columns')
            segments, metadata = self.csv_handler.parse_csv(content, key_column, text_columns)
            return self._convert_csv_segments(segments), metadata

        elif file_type in [FileType.XLIFF_12, FileType.XLIFF_20]:
            segments, metadata = self.xliff_handler.parse_xliff_12(content)
            return self._convert_xliff_segments(segments), metadata

        else:
            raise ValueError(f"Unsupported file type: {file_type}")

    def export_file(
        self,
        filename: str,
        original_content: str,
        translations: Dict[str, str],
        target_language: str,
        file_type: Optional[FileType] = None,
        **kwargs
    ) -> str:
        """
        Export translated file in original format.

        Args:
            filename: Original filename
            original_content: Original file content
            translations: Dict mapping segment_id to translated text
            target_language: Target language code
            file_type: Optional explicit file type
            **kwargs: Additional export options

        Returns:
            Translated file content as string
        """
        # Auto-detect if not specified
        if file_type is None:
            file_type = self.detect_file_type(filename, original_content)

        # Route to appropriate exporter
        if file_type == FileType.ANDROID_XML:
            return self.xml_handler.export_android_xml(
                original_content,
                translations,
                target_language
            )

        elif file_type == FileType.GENERIC_XML:
            return self.xml_handler.export_generic_xml(
                original_content,
                translations
            )

        elif file_type == FileType.JSON:
            preserve_formatting = kwargs.get('preserve_formatting', True)
            return self.json_handler.export_json(
                original_content,
                translations,
                preserve_formatting
            )

        elif file_type == FileType.I18N_JSON:
            source_locale = kwargs.get('source_locale', 'en')
            return self.json_handler.export_i18n_json(
                original_content,
                translations,
                target_language,
                source_locale
            )

        elif file_type == FileType.CSV:
            key_column = kwargs.get('key_column', 0)
            text_columns = kwargs.get('text_columns')
            add_translation_column = kwargs.get('add_translation_column', False)
            return self.csv_handler.export_csv(
                original_content,
                translations,
                key_column,
                text_columns,
                add_translation_column,
                target_language
            )

        elif file_type in [FileType.XLIFF_12, FileType.XLIFF_20]:
            state = kwargs.get('state', 'translated')
            return self.xliff_handler.export_xliff_12(
                original_content,
                translations,
                target_language,
                state
            )

        else:
            raise ValueError(f"Unsupported file type for export: {file_type}")

    def create_xliff_from_file(
        self,
        filename: str,
        content: str,
        source_language: str,
        target_language: str,
        file_type: Optional[FileType] = None
    ) -> str:
        """
        Create XLIFF 1.2 file from any supported format.

        Useful for creating industry-standard exchange format.

        Args:
            filename: Original filename
            content: File content
            source_language: Source language code
            target_language: Target language code
            file_type: Optional file type

        Returns:
            XLIFF 1.2 content as string
        """
        # Parse original file
        segments, metadata = self.parse_file(filename, content, file_type)

        # Convert to XLIFF segments
        xliff_segments = [
            {
                'id': seg.segment_id,
                'source': seg.source_text,
                'target': seg.target_text,
                'context': seg.context
            }
            for seg in segments
        ]

        return self.xliff_handler.create_xliff_12(
            xliff_segments,
            source_language,
            target_language,
            filename
        )

    def validate_translation(
        self,
        source_text: str,
        translated_text: str,
        file_type: FileType
    ) -> Tuple[bool, List[str]]:
        """
        Validate translation for placeholder preservation.

        Args:
            source_text: Source text
            translated_text: Translated text
            file_type: File type (determines validation rules)

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        # Route to appropriate validator
        if file_type in [FileType.ANDROID_XML, FileType.GENERIC_XML]:
            return self.xml_handler.validate_placeholders(source_text, translated_text)
        elif file_type in [FileType.JSON, FileType.I18N_JSON]:
            return self.json_handler.validate_placeholders(source_text, translated_text)
        elif file_type == FileType.CSV:
            return self.csv_handler.validate_placeholders(source_text, translated_text)
        elif file_type in [FileType.XLIFF_12, FileType.XLIFF_20]:
            return self.xliff_handler.validate_placeholders(source_text, translated_text)

        return True, []

    def _convert_xml_segments(self, segments: List[XMLSegment]) -> List[ParsedSegment]:
        """Convert XMLSegment to ParsedSegment."""
        return [
            ParsedSegment(
                segment_id=seg.segment_id,
                source_text=seg.source_text,
                context=seg.context,
                placeholders=seg.placeholders,
                metadata=seg.metadata
            )
            for seg in segments
        ]

    def _convert_json_segments(self, segments: List[JSONSegment]) -> List[ParsedSegment]:
        """Convert JSONSegment to ParsedSegment."""
        return [
            ParsedSegment(
                segment_id=seg.segment_id,
                source_text=seg.source_text,
                context=seg.context,
                placeholders=seg.placeholders,
                metadata=seg.metadata
            )
            for seg in segments
        ]

    def _convert_csv_segments(self, segments: List[CSVSegment]) -> List[ParsedSegment]:
        """Convert CSVSegment to ParsedSegment."""
        return [
            ParsedSegment(
                segment_id=seg.segment_id,
                source_text=seg.source_text,
                context=seg.context,
                placeholders=seg.placeholders,
                metadata=seg.metadata
            )
            for seg in segments
        ]

    def _convert_xliff_segments(self, segments: List[XLIFFSegment]) -> List[ParsedSegment]:
        """Convert XLIFFSegment to ParsedSegment."""
        return [
            ParsedSegment(
                segment_id=seg.segment_id,
                source_text=seg.source_text,
                context=seg.context,
                placeholders=seg.placeholders,
                metadata=seg.metadata,
                target_text=seg.target_text
            )
            for seg in segments
        ]


# Global instance
file_parser = FileParser()
