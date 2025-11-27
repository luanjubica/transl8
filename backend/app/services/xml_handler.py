"""
XML file parsing and export service.

Handles:
- Generic XML files
- Android strings.xml
- iOS .strings files (property list format)

Security: Uses defusedxml to prevent XXE attacks
"""

from typing import List, Dict, Any, Optional, Tuple
from defusedxml import ElementTree as ET
from defusedxml.ElementTree import ParseError
import re
from datetime import datetime


class XMLSegment:
    """Represents a translatable segment extracted from XML."""

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


class XMLHandler:
    """Handles XML file parsing and export with structure preservation."""

    # Placeholder patterns to detect in text
    PLACEHOLDER_PATTERNS = [
        r'\{[^}]+\}',                    # {variable}
        r'\{\{[^}]+\}\}',                # {{variable}}
        r'%\([^)]+\)[sdf]',              # %(name)s, %(value)d
        r'%\d+\$[sdf]',                  # %1$s, %2$d (positional)
        r'%[sdf]',                       # %s, %d, %f
        r'\$\{[^}]+\}',                  # ${variable}
        r'\[\[([^\]]+)\]\]',             # [[variable]]
        r'<[^>]+>',                      # <placeholder> (XML tags in text)
    ]

    def detect_placeholders(self, text: str) -> List[str]:
        """
        Detect placeholders in text using regex patterns.

        Args:
            text: Source text to analyze

        Returns:
            List of detected placeholder strings
        """
        placeholders = []
        for pattern in self.PLACEHOLDER_PATTERNS:
            matches = re.findall(pattern, text)
            placeholders.extend(matches)

        return list(set(placeholders))  # Remove duplicates

    def parse_android_xml(self, xml_content: str) -> Tuple[List[XMLSegment], Dict[str, Any]]:
        """
        Parse Android strings.xml file.

        Format:
        <resources>
            <string name="app_name">MyApp</string>
            <string name="welcome">Hello {name}!</string>
            <string name="format">You have %d messages</string>
            <string-array name="colors">
                <item>Red</item>
                <item>Blue</item>
            </string-array>
        </resources>

        Args:
            xml_content: XML file content as string

        Returns:
            Tuple of (segments list, metadata dict)
        """
        try:
            root = ET.fromstring(xml_content)
        except ParseError as e:
            raise ValueError(f"Invalid XML: {e}")

        segments = []
        metadata = {
            'file_type': 'android_xml',
            'root_tag': root.tag,
            'namespaces': dict(root.attrib) if root.attrib else {},
            'structure': []
        }

        # Parse <string> elements
        for string_elem in root.findall('.//string'):
            name = string_elem.get('name')
            text = string_elem.text or ''

            if not name or not text.strip():
                continue

            # Detect placeholders
            placeholders = self.detect_placeholders(text)

            # Check if translatable (Android convention)
            translatable = string_elem.get('translatable', 'true').lower()
            is_locked = translatable == 'false'

            segment = XMLSegment(
                segment_id=f"string.{name}",
                source_text=text,
                context=name,
                placeholders=placeholders,
                metadata={
                    'element_type': 'string',
                    'name': name,
                    'is_locked': is_locked,
                    'translatable': translatable
                }
            )
            segments.append(segment)
            metadata['structure'].append({
                'type': 'string',
                'name': name,
                'has_placeholders': len(placeholders) > 0
            })

        # Parse <string-array> elements
        for array_elem in root.findall('.//string-array'):
            array_name = array_elem.get('name')
            if not array_name:
                continue

            for idx, item_elem in enumerate(array_elem.findall('.//item')):
                text = item_elem.text or ''
                if not text.strip():
                    continue

                placeholders = self.detect_placeholders(text)

                segment = XMLSegment(
                    segment_id=f"string_array.{array_name}.{idx}",
                    source_text=text,
                    context=f"{array_name}[{idx}]",
                    placeholders=placeholders,
                    metadata={
                        'element_type': 'string-array',
                        'array_name': array_name,
                        'array_index': idx
                    }
                )
                segments.append(segment)

        # Parse <plurals> elements
        for plural_elem in root.findall('.//plurals'):
            plural_name = plural_elem.get('name')
            if not plural_name:
                continue

            for item_elem in plural_elem.findall('.//item'):
                quantity = item_elem.get('quantity', 'other')
                text = item_elem.text or ''

                if not text.strip():
                    continue

                placeholders = self.detect_placeholders(text)

                segment = XMLSegment(
                    segment_id=f"plural.{plural_name}.{quantity}",
                    source_text=text,
                    context=f"{plural_name} ({quantity})",
                    placeholders=placeholders,
                    metadata={
                        'element_type': 'plurals',
                        'plural_name': plural_name,
                        'quantity': quantity
                    }
                )
                segments.append(segment)

        return segments, metadata

    def parse_generic_xml(self, xml_content: str) -> Tuple[List[XMLSegment], Dict[str, Any]]:
        """
        Parse generic XML file by extracting all text nodes.

        Args:
            xml_content: XML file content as string

        Returns:
            Tuple of (segments list, metadata dict)
        """
        try:
            root = ET.fromstring(xml_content)
        except ParseError as e:
            raise ValueError(f"Invalid XML: {e}")

        segments = []
        metadata = {
            'file_type': 'generic_xml',
            'root_tag': root.tag,
            'structure': []
        }

        def extract_text_nodes(element, path=""):
            """Recursively extract text from all elements."""
            current_path = f"{path}/{element.tag}" if path else element.tag

            # Extract text content
            if element.text and element.text.strip():
                text = element.text.strip()
                placeholders = self.detect_placeholders(text)

                # Generate unique segment ID based on path and index
                segment_id = current_path.replace('/', '.')

                segment = XMLSegment(
                    segment_id=segment_id,
                    source_text=text,
                    context=current_path,
                    placeholders=placeholders,
                    metadata={
                        'xpath': current_path,
                        'tag': element.tag,
                        'attributes': dict(element.attrib)
                    }
                )
                segments.append(segment)

            # Recursively process child elements
            for child in element:
                extract_text_nodes(child, current_path)

                # Also extract tail text (text after closing tag)
                if child.tail and child.tail.strip():
                    text = child.tail.strip()
                    placeholders = self.detect_placeholders(text)

                    segment = XMLSegment(
                        segment_id=f"{current_path}.tail",
                        source_text=text,
                        context=f"{current_path} (tail)",
                        placeholders=placeholders,
                        metadata={
                            'xpath': current_path,
                            'type': 'tail_text'
                        }
                    )
                    segments.append(segment)

        extract_text_nodes(root)

        return segments, metadata

    def export_android_xml(
        self,
        original_content: str,
        translations: Dict[str, str],
        target_language: str
    ) -> str:
        """
        Export translated Android XML file.

        Args:
            original_content: Original XML content
            translations: Dict mapping segment_id to translated text
            target_language: Target language code

        Returns:
            Translated XML content as string
        """
        try:
            root = ET.fromstring(original_content)
        except ParseError as e:
            raise ValueError(f"Invalid XML: {e}")

        # Update <string> elements
        for string_elem in root.findall('.//string'):
            name = string_elem.get('name')
            if name:
                segment_id = f"string.{name}"
                if segment_id in translations:
                    string_elem.text = translations[segment_id]

        # Update <string-array> items
        for array_elem in root.findall('.//string-array'):
            array_name = array_elem.get('name')
            if array_name:
                for idx, item_elem in enumerate(array_elem.findall('.//item')):
                    segment_id = f"string_array.{array_name}.{idx}"
                    if segment_id in translations:
                        item_elem.text = translations[segment_id]

        # Update <plurals> items
        for plural_elem in root.findall('.//plurals'):
            plural_name = plural_elem.get('name')
            if plural_name:
                for item_elem in plural_elem.findall('.//item'):
                    quantity = item_elem.get('quantity', 'other')
                    segment_id = f"plural.{plural_name}.{quantity}"
                    if segment_id in translations:
                        item_elem.text = translations[segment_id]

        # Convert back to string with XML declaration
        xml_str = ET.tostring(root, encoding='unicode')
        return f'<?xml version="1.0" encoding="utf-8"?>\n{xml_str}'

    def export_generic_xml(
        self,
        original_content: str,
        translations: Dict[str, str]
    ) -> str:
        """
        Export translated generic XML file.

        Args:
            original_content: Original XML content
            translations: Dict mapping segment_id to translated text

        Returns:
            Translated XML content as string
        """
        try:
            root = ET.fromstring(original_content)
        except ParseError as e:
            raise ValueError(f"Invalid XML: {e}")

        def update_text_nodes(element, path=""):
            """Recursively update text in all elements."""
            current_path = f"{path}/{element.tag}" if path else element.tag
            segment_id = current_path.replace('/', '.')

            # Update element text
            if element.text and element.text.strip():
                if segment_id in translations:
                    element.text = translations[segment_id]

            # Recursively process child elements
            for child in element:
                update_text_nodes(child, current_path)

                # Update tail text
                if child.tail and child.tail.strip():
                    tail_id = f"{current_path}.tail"
                    if tail_id in translations:
                        child.tail = translations[tail_id]

        update_text_nodes(root)

        # Convert back to string
        xml_str = ET.tostring(root, encoding='unicode')
        return f'<?xml version="1.0" encoding="utf-8"?>\n{xml_str}'

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

        # Check for missing placeholders
        missing = source_placeholders - target_placeholders
        if missing:
            errors.append(f"Missing placeholders: {', '.join(missing)}")

        # Check for extra placeholders
        extra = target_placeholders - source_placeholders
        if extra:
            errors.append(f"Extra placeholders: {', '.join(extra)}")

        return len(errors) == 0, errors
