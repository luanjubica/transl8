"""
CSV file parsing and export service.

Handles:
- Simple key-value CSV (key, source_text)
- Multi-column CSV (key, source, target1, target2, ...)
- Product catalogs (SKU, description, name, etc.)

Preserves column structure and supports bulk translation.
"""

import csv
import io
import re
from typing import List, Dict, Any, Optional, Tuple


class CSVSegment:
    """Represents a translatable segment extracted from CSV."""

    def __init__(
        self,
        segment_id: str,
        source_text: str,
        context: Optional[str] = None,
        placeholders: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.segment_id = segment_id
        self.source_text = source_text
        self.context = context
        self.placeholders = placeholders or []
        self.metadata = metadata or {}


class CSVHandler:
    """Handles CSV file parsing and export."""

    # Placeholder patterns
    PLACEHOLDER_PATTERNS = [
        r'\{[^}]+\}',
        r'\{\{[^}]+\}\}',
        r'%\([^)]+\)[sdf]',
        r'%\d+\$[sdf]',
        r'%[sdf]',
        r'\$\{[^}]+\}',
    ]

    def detect_placeholders(self, text: str) -> List[str]:
        """Detect placeholders in text."""
        if not isinstance(text, str):
            return []

        placeholders = []
        for pattern in self.PLACEHOLDER_PATTERNS:
            matches = re.findall(pattern, text)
            placeholders.extend(matches)

        return list(set(placeholders))

    def detect_csv_format(self, csv_content: str) -> Dict[str, Any]:
        """
        Auto-detect CSV format and structure.

        Returns metadata about:
        - Delimiter (comma, semicolon, tab)
        - Has header row
        - Column count
        - Translatable columns
        """
        # Try different delimiters
        delimiters = [',', ';', '\t', '|']
        best_delimiter = ','
        max_columns = 0

        for delimiter in delimiters:
            try:
                reader = csv.reader(io.StringIO(csv_content), delimiter=delimiter)
                first_row = next(reader)
                if len(first_row) > max_columns:
                    max_columns = len(first_row)
                    best_delimiter = delimiter
            except:
                continue

        # Re-read with best delimiter
        reader = csv.reader(io.StringIO(csv_content), delimiter=best_delimiter)
        rows = list(reader)

        if not rows:
            raise ValueError("Empty CSV file")

        # Detect if first row is header
        first_row = rows[0]
        has_header = self._is_likely_header(first_row)

        # Identify translatable columns (contain text, not IDs/numbers)
        translatable_columns = []
        if has_header:
            for idx, col_name in enumerate(first_row):
                # Common translatable column names
                if any(keyword in col_name.lower() for keyword in [
                    'text', 'description', 'name', 'title', 'content',
                    'label', 'message', 'value', 'translation'
                ]):
                    translatable_columns.append(idx)
        else:
            # Assume all columns except first (usually ID) are translatable
            translatable_columns = list(range(1, len(first_row)))

        return {
            'delimiter': best_delimiter,
            'has_header': has_header,
            'column_count': len(first_row),
            'row_count': len(rows),
            'translatable_columns': translatable_columns,
            'header_row': first_row if has_header else None
        }

    def parse_csv(
        self,
        csv_content: str,
        key_column: int = 0,
        text_columns: Optional[List[int]] = None
    ) -> Tuple[List[CSVSegment], Dict[str, Any]]:
        """
        Parse CSV file and extract translatable strings.

        Format options:
        1. key, source_text
        2. id, name, description
        3. sku, product_name, product_description, category

        Args:
            csv_content: CSV file content as string
            key_column: Column index for unique key/ID (default: 0)
            text_columns: List of column indices containing translatable text
                         (if None, auto-detect)

        Returns:
            Tuple of (segments list, metadata dict)
        """
        # Auto-detect format
        format_info = self.detect_csv_format(csv_content)
        delimiter = format_info['delimiter']
        has_header = format_info['has_header']

        reader = csv.reader(io.StringIO(csv_content), delimiter=delimiter)
        rows = list(reader)

        if not rows:
            raise ValueError("Empty CSV file")

        # Extract header if present
        header = None
        data_rows = rows
        if has_header:
            header = rows[0]
            data_rows = rows[1:]

        # Auto-detect text columns if not specified
        if text_columns is None:
            text_columns = format_info['translatable_columns']

        if not text_columns:
            # Default: all columns except key column
            text_columns = [i for i in range(len(rows[0])) if i != key_column]

        segments = []
        metadata = {
            'file_type': 'csv',
            'delimiter': delimiter,
            'has_header': has_header,
            'header': header,
            'key_column': key_column,
            'text_columns': text_columns,
            'total_rows': len(data_rows)
        }

        for row_idx, row in enumerate(data_rows):
            if len(row) <= key_column:
                continue  # Skip malformed rows

            # Get unique key from key column
            row_key = row[key_column] if len(row) > key_column else f"row_{row_idx}"

            # Extract text from each translatable column
            for col_idx in text_columns:
                if col_idx >= len(row):
                    continue

                text = row[col_idx].strip()
                if not text:
                    continue

                # Column name for context
                col_name = header[col_idx] if header and col_idx < len(header) else f"col_{col_idx}"

                placeholders = self.detect_placeholders(text)

                segment = CSVSegment(
                    segment_id=f"{row_key}.{col_name}",
                    source_text=text,
                    context=f"Row {row_idx + 1}, Column '{col_name}'",
                    placeholders=placeholders,
                    metadata={
                        'row_index': row_idx,
                        'row_key': row_key,
                        'column_index': col_idx,
                        'column_name': col_name
                    }
                )
                segments.append(segment)

        return segments, metadata

    def export_csv(
        self,
        original_content: str,
        translations: Dict[str, str],
        key_column: int = 0,
        text_columns: Optional[List[int]] = None,
        add_translation_column: bool = False,
        target_language: Optional[str] = None
    ) -> str:
        """
        Export translated CSV file.

        Options:
        1. Replace source text in-place
        2. Add new column with translations

        Args:
            original_content: Original CSV content
            translations: Dict mapping segment_id to translated text
            key_column: Column index for keys
            text_columns: Columns to translate
            add_translation_column: If True, add new columns instead of replacing
            target_language: Target language code (for column naming)

        Returns:
            Translated CSV content as string
        """
        # Detect format
        format_info = self.detect_csv_format(original_content)
        delimiter = format_info['delimiter']
        has_header = format_info['has_header']

        reader = csv.reader(io.StringIO(original_content), delimiter=delimiter)
        rows = list(reader)

        if not rows:
            return original_content

        # Auto-detect text columns if not specified
        if text_columns is None:
            text_columns = format_info['translatable_columns']
            if not text_columns:
                text_columns = [i for i in range(len(rows[0])) if i != key_column]

        output = io.StringIO()
        writer = csv.writer(output, delimiter=delimiter)

        # Process header row
        if has_header:
            header = rows[0]
            if add_translation_column:
                # Add new columns for translations
                new_header = header.copy()
                for col_idx in text_columns:
                    col_name = header[col_idx] if col_idx < len(header) else f"col_{col_idx}"
                    suffix = f"_{target_language}" if target_language else "_translated"
                    new_header.append(f"{col_name}{suffix}")
                writer.writerow(new_header)
            else:
                writer.writerow(header)
            data_rows = rows[1:]
        else:
            data_rows = rows

        # Process data rows
        for row_idx, row in enumerate(data_rows):
            if not row:
                writer.writerow(row)
                continue

            # Get row key
            row_key = row[key_column] if len(row) > key_column else f"row_{row_idx}"

            if add_translation_column:
                # Keep original row and append translations
                new_row = row.copy()
                for col_idx in text_columns:
                    if col_idx >= len(row):
                        new_row.append('')
                        continue

                    # Get header name if available
                    if has_header and col_idx < len(rows[0]):
                        col_name = rows[0][col_idx]
                    else:
                        col_name = f"col_{col_idx}"

                    segment_id = f"{row_key}.{col_name}"
                    translated_text = translations.get(segment_id, row[col_idx])
                    new_row.append(translated_text)

                writer.writerow(new_row)
            else:
                # Replace source text with translations
                new_row = row.copy()
                for col_idx in text_columns:
                    if col_idx >= len(row):
                        continue

                    # Get column name
                    if has_header and col_idx < len(rows[0]):
                        col_name = rows[0][col_idx]
                    else:
                        col_name = f"col_{col_idx}"

                    segment_id = f"{row_key}.{col_name}"
                    if segment_id in translations:
                        new_row[col_idx] = translations[segment_id]

                writer.writerow(new_row)

        return output.getvalue()

    def _is_likely_header(self, row: List[str]) -> bool:
        """
        Heuristic to determine if row is a header.

        Checks:
        - Contains common header keywords
        - Mostly text (not numbers)
        - No very long text (descriptions)
        """
        if not row:
            return False

        # Check for common header keywords
        header_keywords = [
            'id', 'key', 'name', 'title', 'description', 'text',
            'value', 'source', 'target', 'translation', 'label',
            'sku', 'code', 'category', 'type', 'status'
        ]

        keyword_matches = sum(
            1 for cell in row
            if any(keyword in cell.lower() for keyword in header_keywords)
        )

        # If more than 30% of cells match header keywords, likely a header
        if len(row) > 0 and keyword_matches / len(row) >= 0.3:
            return True

        # Check if cells are short (headers usually are)
        avg_length = sum(len(cell) for cell in row) / len(row) if row else 0
        if avg_length < 20:  # Headers usually short
            # Check if mostly non-numeric
            non_numeric = sum(1 for cell in row if not cell.replace('.', '').isdigit())
            if non_numeric / len(row) >= 0.7:
                return True

        return False

    def validate_placeholders(
        self,
        source_text: str,
        translated_text: str
    ) -> Tuple[bool, List[str]]:
        """Validate placeholder preservation."""
        source_placeholders = set(self.detect_placeholders(source_text))
        target_placeholders = set(self.detect_placeholders(translated_text))

        errors = []

        missing = source_placeholders - target_placeholders
        if missing:
            errors.append(f"Missing placeholders: {', '.join(missing)}")

        extra = target_placeholders - source_placeholders
        if extra:
            errors.append(f"Extra placeholders: {', '.join(extra)}")

        return len(errors) == 0, errors
