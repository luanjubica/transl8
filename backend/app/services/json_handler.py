"""
JSON file parsing and export service.

Handles:
- Flat JSON key-value pairs
- Nested JSON structures
- i18n JSON formats (nested by locale)

Preserves structure and supports placeholder detection.
"""

import json
import re
from typing import List, Dict, Any, Optional, Tuple


class JSONSegment:
    """Represents a translatable segment extracted from JSON."""

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


class JSONHandler:
    """Handles JSON file parsing and export with structure preservation."""

    # Placeholder patterns
    PLACEHOLDER_PATTERNS = [
        r'\{[^}]+\}',                    # {variable}
        r'\{\{[^}]+\}\}',                # {{variable}}
        r'%\([^)]+\)[sdf]',              # %(name)s
        r'%\d+\$[sdf]',                  # %1$s
        r'%[sdf]',                       # %s, %d
        r'\$\{[^}]+\}',                  # ${variable}
        r'\$t\([^)]+\)',                 # $t(key) - i18next interpolation
    ]

    def detect_placeholders(self, text: str) -> List[str]:
        """
        Detect placeholders in text.

        Args:
            text: Source text to analyze

        Returns:
            List of detected placeholder strings
        """
        if not isinstance(text, str):
            return []

        placeholders = []
        for pattern in self.PLACEHOLDER_PATTERNS:
            matches = re.findall(pattern, text)
            placeholders.extend(matches)

        return list(set(placeholders))

    def parse_json(self, json_content: str) -> Tuple[List[JSONSegment], Dict[str, Any]]:
        """
        Parse JSON file and extract translatable strings.

        Handles both flat and nested structures:
        {
          "welcome": "Hello",
          "user": {
            "greeting": "Welcome {name}",
            "farewell": "Goodbye"
          }
        }

        Args:
            json_content: JSON file content as string

        Returns:
            Tuple of (segments list, metadata dict)
        """
        try:
            data = json.loads(json_content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")

        segments = []
        metadata = {
            'file_type': 'json',
            'structure_type': 'nested' if self._is_nested(data) else 'flat',
            'keys_count': 0
        }

        def extract_strings(obj: Any, path: str = "") -> None:
            """Recursively extract translatable strings from JSON object."""

            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key

                    if isinstance(value, str):
                        # Extract string value
                        if value.strip():  # Only non-empty strings
                            placeholders = self.detect_placeholders(value)

                            segment = JSONSegment(
                                segment_id=current_path,
                                source_text=value,
                                context=current_path,
                                placeholders=placeholders,
                                metadata={
                                    'key_path': current_path,
                                    'depth': len(current_path.split('.'))
                                }
                            )
                            segments.append(segment)
                            metadata['keys_count'] += 1

                    elif isinstance(value, (dict, list)):
                        # Recursively process nested structures
                        extract_strings(value, current_path)

            elif isinstance(obj, list):
                for idx, item in enumerate(obj):
                    current_path = f"{path}[{idx}]"

                    if isinstance(item, str) and item.strip():
                        placeholders = self.detect_placeholders(item)

                        segment = JSONSegment(
                            segment_id=current_path,
                            source_text=item,
                            context=current_path,
                            placeholders=placeholders,
                            metadata={
                                'key_path': current_path,
                                'is_array_item': True,
                                'array_index': idx
                            }
                        )
                        segments.append(segment)
                        metadata['keys_count'] += 1

                    elif isinstance(item, (dict, list)):
                        extract_strings(item, current_path)

        extract_strings(data)

        return segments, metadata

    def export_json(
        self,
        original_content: str,
        translations: Dict[str, str],
        preserve_formatting: bool = True
    ) -> str:
        """
        Export translated JSON file.

        Args:
            original_content: Original JSON content
            translations: Dict mapping segment_id (key path) to translated text
            preserve_formatting: Whether to preserve original indentation

        Returns:
            Translated JSON content as string
        """
        try:
            data = json.loads(original_content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")

        # Detect original indentation
        indent = self._detect_indent(original_content) if preserve_formatting else 2

        def update_strings(obj: Any, path: str = "") -> Any:
            """Recursively update translatable strings in JSON object."""

            if isinstance(obj, dict):
                result = {}
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key

                    if isinstance(value, str):
                        # Replace with translation if available
                        result[key] = translations.get(current_path, value)
                    elif isinstance(value, (dict, list)):
                        result[key] = update_strings(value, current_path)
                    else:
                        result[key] = value
                return result

            elif isinstance(obj, list):
                result = []
                for idx, item in enumerate(obj):
                    current_path = f"{path}[{idx}]"

                    if isinstance(item, str):
                        result.append(translations.get(current_path, item))
                    elif isinstance(item, (dict, list)):
                        result.append(update_strings(item, current_path))
                    else:
                        result.append(item)
                return result

            return obj

        translated_data = update_strings(data)

        # Convert back to JSON string
        return json.dumps(
            translated_data,
            indent=indent,
            ensure_ascii=False,
            sort_keys=False
        )

    def parse_i18n_json(self, json_content: str, source_locale: str = "en") -> Tuple[List[JSONSegment], Dict[str, Any]]:
        """
        Parse i18n JSON format where keys are nested by locale.

        Format:
        {
          "en": {
            "welcome": "Hello",
            "user": {
              "greeting": "Welcome"
            }
          },
          "de": {
            "welcome": "Hallo",
            ...
          }
        }

        Args:
            json_content: JSON file content
            source_locale: Source language locale key

        Returns:
            Tuple of (segments list, metadata dict)
        """
        try:
            data = json.loads(json_content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")

        if source_locale not in data:
            raise ValueError(f"Source locale '{source_locale}' not found in JSON")

        source_data = data[source_locale]
        segments = []
        metadata = {
            'file_type': 'i18n_json',
            'source_locale': source_locale,
            'available_locales': list(data.keys()),
            'keys_count': 0
        }

        def extract_strings(obj: Any, path: str = "") -> None:
            """Extract strings from source locale."""

            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key

                    if isinstance(value, str) and value.strip():
                        placeholders = self.detect_placeholders(value)

                        segment = JSONSegment(
                            segment_id=current_path,
                            source_text=value,
                            context=current_path,
                            placeholders=placeholders,
                            metadata={
                                'key_path': current_path,
                                'locale': source_locale
                            }
                        )
                        segments.append(segment)
                        metadata['keys_count'] += 1

                    elif isinstance(value, (dict, list)):
                        extract_strings(value, current_path)

            elif isinstance(obj, list):
                for idx, item in enumerate(obj):
                    current_path = f"{path}[{idx}]"
                    if isinstance(item, str) and item.strip():
                        placeholders = self.detect_placeholders(item)

                        segment = JSONSegment(
                            segment_id=current_path,
                            source_text=item,
                            context=current_path,
                            placeholders=placeholders,
                            metadata={'key_path': current_path, 'locale': source_locale}
                        )
                        segments.append(segment)
                        metadata['keys_count'] += 1
                    elif isinstance(item, (dict, list)):
                        extract_strings(item, current_path)

        extract_strings(source_data)

        return segments, metadata

    def export_i18n_json(
        self,
        original_content: str,
        translations: Dict[str, str],
        target_locale: str,
        source_locale: str = "en"
    ) -> str:
        """
        Export i18n JSON format with new locale.

        Args:
            original_content: Original JSON content
            translations: Dict mapping key paths to translated text
            target_locale: Target language locale key
            source_locale: Source language locale key

        Returns:
            Updated JSON content with target locale added/updated
        """
        try:
            data = json.loads(original_content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")

        # Create target locale structure by copying source structure
        if source_locale not in data:
            raise ValueError(f"Source locale '{source_locale}' not found")

        def create_translated_structure(obj: Any, path: str = "") -> Any:
            """Create translated version of nested structure."""

            if isinstance(obj, dict):
                result = {}
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key

                    if isinstance(value, str):
                        result[key] = translations.get(current_path, value)
                    elif isinstance(value, (dict, list)):
                        result[key] = create_translated_structure(value, current_path)
                    else:
                        result[key] = value
                return result

            elif isinstance(obj, list):
                result = []
                for idx, item in enumerate(obj):
                    current_path = f"{path}[{idx}]"

                    if isinstance(item, str):
                        result.append(translations.get(current_path, item))
                    elif isinstance(item, (dict, list)):
                        result.append(create_translated_structure(item, current_path))
                    else:
                        result.append(item)
                return result

            return obj

        # Add/update target locale
        data[target_locale] = create_translated_structure(data[source_locale])

        return json.dumps(data, indent=2, ensure_ascii=False, sort_keys=False)

    def _is_nested(self, data: Any) -> bool:
        """Check if JSON structure has nested objects."""
        if isinstance(data, dict):
            for value in data.values():
                if isinstance(value, (dict, list)):
                    return True
        return False

    def _detect_indent(self, json_str: str) -> int:
        """Detect indentation level in JSON string."""
        lines = json_str.split('\n')
        for line in lines:
            if line.startswith(' ') and not line.startswith('  '):
                # Count leading spaces
                indent = len(line) - len(line.lstrip())
                if indent > 0:
                    return indent
        return 2  # Default to 2 spaces

    def validate_placeholders(
        self,
        source_text: str,
        translated_text: str
    ) -> Tuple[bool, List[str]]:
        """
        Validate that placeholders are preserved in translation.

        Args:
            source_text: Original text
            translated_text: Translated text

        Returns:
            Tuple of (is_valid, list of error messages)
        """
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
