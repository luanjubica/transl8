"""
XLIFF file parsing and export service.

Handles:
- XLIFF 1.2 (most common version)
- XLIFF 2.0 (newer standard)

XLIFF (XML Localization Interchange File Format) is the industry standard
for translation memory and localization workflows.

Security: Uses defusedxml to prevent XXE attacks
"""

from typing import List, Dict, Any, Optional, Tuple
from defusedxml import ElementTree as ET
from defusedxml.ElementTree import ParseError
import re
from datetime import datetime


class XLIFFSegment:
    """Represents a translatable unit extracted from XLIFF."""

    def __init__(
        self,
        segment_id: str,
        source_text: str,
        target_text: Optional[str] = None,
        context: Optional[str] = None,
        placeholders: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        state: str = "new"
    ):
        self.segment_id = segment_id
        self.source_text = source_text
        self.target_text = target_text
        self.context = context
        self.placeholders = placeholders or []
        self.metadata = metadata or {}
        self.state = state  # new, translated, reviewed, final


class XLIFFHandler:
    """Handles XLIFF file parsing and export."""

    # XLIFF 1.2 namespace
    XLIFF_12_NS = "urn:oasis:names:tc:xliff:document:1.2"

    # Placeholder patterns
    PLACEHOLDER_PATTERNS = [
        r'<x\s+id="[^"]*"\s*/?>',        # XLIFF <x> tags
        r'<g\s+id="[^"]*">.*?</g>',      # XLIFF <g> tags
        r'<bx\s+id="[^"]*"\s*/>',        # XLIFF <bx> tags
        r'<ex\s+id="[^"]*"\s*/>',        # XLIFF <ex> tags
        r'\{[^}]+\}',                     # {variable}
        r'%\([^)]+\)[sdf]',               # %(name)s
        r'%\d+\$[sdf]',                   # %1$s
    ]

    def detect_placeholders(self, text: str) -> List[str]:
        """Detect placeholders including XLIFF inline tags."""
        if not isinstance(text, str):
            return []

        placeholders = []
        for pattern in self.PLACEHOLDER_PATTERNS:
            matches = re.findall(pattern, text)
            placeholders.extend(matches)

        return list(set(placeholders))

    def detect_xliff_version(self, xliff_content: str) -> str:
        """
        Detect XLIFF version from file content.

        Returns: "1.2", "2.0", or "unknown"
        """
        try:
            root = ET.fromstring(xliff_content)

            # Check version attribute
            version = root.get('version')
            if version:
                if version.startswith('1.2'):
                    return '1.2'
                elif version.startswith('2.'):
                    return '2.0'

            # Check namespace
            if self.XLIFF_12_NS in root.tag:
                return '1.2'

            # XLIFF 2.0 uses different namespace
            if 'xliff:doc' in root.tag or 'urn:oasis:names:tc:xliff:document:2.0' in root.tag:
                return '2.0'

        except ParseError:
            pass

        return 'unknown'

    def parse_xliff_12(self, xliff_content: str) -> Tuple[List[XLIFFSegment], Dict[str, Any]]:
        """
        Parse XLIFF 1.2 file.

        Structure:
        <xliff version="1.2">
          <file source-language="en" target-language="de">
            <body>
              <trans-unit id="1">
                <source>Hello</source>
                <target>Hallo</target>
              </trans-unit>
            </body>
          </file>
        </xliff>

        Args:
            xliff_content: XLIFF file content as string

        Returns:
            Tuple of (segments list, metadata dict)
        """
        try:
            root = ET.fromstring(xliff_content)
        except ParseError as e:
            raise ValueError(f"Invalid XLIFF: {e}")

        segments = []
        metadata = {
            'file_type': 'xliff_1.2',
            'version': root.get('version', '1.2'),
            'files': []
        }

        # Define namespace
        ns = {'xliff': self.XLIFF_12_NS} if self.XLIFF_12_NS in xliff_content else {}

        # Find all <file> elements
        file_elements = root.findall('.//file') if not ns else root.findall('.//xliff:file', ns)

        for file_elem in file_elements:
            source_lang = file_elem.get('source-language', 'en')
            target_lang = file_elem.get('target-language', '')
            original = file_elem.get('original', '')

            file_info = {
                'source_language': source_lang,
                'target_language': target_lang,
                'original': original,
                'trans_units': 0
            }

            # Find all <trans-unit> elements
            trans_units = file_elem.findall('.//trans-unit') if not ns else file_elem.findall('.//xliff:trans-unit', ns)

            for trans_unit in trans_units:
                unit_id = trans_unit.get('id')
                if not unit_id:
                    continue

                # Extract source text
                source_elem = trans_unit.find('.//source') if not ns else trans_unit.find('.//xliff:source', ns)
                if source_elem is None or source_elem.text is None:
                    continue

                source_text = self._extract_text_with_tags(source_elem)

                # Extract target text if present
                target_elem = trans_unit.find('.//target') if not ns else trans_unit.find('.//xliff:target', ns)
                target_text = None
                state = 'new'

                if target_elem is not None:
                    target_text = self._extract_text_with_tags(target_elem)
                    state = target_elem.get('state', 'translated')

                # Extract context from <note> elements
                notes = trans_unit.findall('.//note') if not ns else trans_unit.findall('.//xliff:note', ns)
                context_notes = [note.text for note in notes if note.text]
                context = ' | '.join(context_notes) if context_notes else unit_id

                # Detect placeholders
                placeholders = self.detect_placeholders(source_text)

                segment = XLIFFSegment(
                    segment_id=unit_id,
                    source_text=source_text,
                    target_text=target_text,
                    context=context,
                    placeholders=placeholders,
                    state=state,
                    metadata={
                        'file_original': original,
                        'source_language': source_lang,
                        'target_language': target_lang,
                        'resname': trans_unit.get('resname', ''),
                        'approved': trans_unit.get('approved', 'no')
                    }
                )
                segments.append(segment)
                file_info['trans_units'] += 1

            metadata['files'].append(file_info)

        return segments, metadata

    def export_xliff_12(
        self,
        original_content: str,
        translations: Dict[str, str],
        target_language: str,
        state: str = "translated"
    ) -> str:
        """
        Export XLIFF 1.2 file with translations.

        Args:
            original_content: Original XLIFF content
            translations: Dict mapping trans-unit ID to translated text
            target_language: Target language code
            state: Translation state (new, translated, final, reviewed)

        Returns:
            Updated XLIFF content as string
        """
        try:
            root = ET.fromstring(original_content)
        except ParseError as e:
            raise ValueError(f"Invalid XLIFF: {e}")

        ns = {'xliff': self.XLIFF_12_NS} if self.XLIFF_12_NS in original_content else {}

        # Update <file> target-language
        file_elements = root.findall('.//file') if not ns else root.findall('.//xliff:file', ns)
        for file_elem in file_elements:
            file_elem.set('target-language', target_language)

        # Update <trans-unit> elements
        trans_units = root.findall('.//trans-unit') if not ns else root.findall('.//xliff:trans-unit', ns)

        for trans_unit in trans_units:
            unit_id = trans_unit.get('id')
            if not unit_id or unit_id not in translations:
                continue

            # Find or create <target> element
            target_elem = trans_unit.find('.//target') if not ns else trans_unit.find('.//xliff:target', ns)

            if target_elem is None:
                # Create new target element after source
                source_elem = trans_unit.find('.//source') if not ns else trans_unit.find('.//xliff:source', ns)
                target_elem = ET.Element('target')
                # Insert after source
                source_index = list(trans_unit).index(source_elem)
                trans_unit.insert(source_index + 1, target_elem)

            # Set translation and state
            target_elem.text = translations[unit_id]
            target_elem.set('state', state)

        # Convert back to string
        xml_str = ET.tostring(root, encoding='unicode')
        return f'<?xml version="1.0" encoding="UTF-8"?>\n{xml_str}'

    def create_xliff_12(
        self,
        segments: List[Dict[str, Any]],
        source_language: str,
        target_language: str,
        original_filename: str = "document"
    ) -> str:
        """
        Create new XLIFF 1.2 file from segments.

        Args:
            segments: List of segment dicts with 'id', 'source', optional 'target'
            source_language: Source language code
            target_language: Target language code
            original_filename: Original file name

        Returns:
            XLIFF 1.2 content as string
        """
        # Create root element
        xliff = ET.Element('xliff', version='1.2', xmlns=self.XLIFF_12_NS)

        # Create file element
        file_elem = ET.SubElement(
            xliff,
            'file',
            {
                'source-language': source_language,
                'target-language': target_language,
                'datatype': 'plaintext',
                'original': original_filename,
                'date': datetime.utcnow().isoformat()
            }
        )

        # Create body
        body = ET.SubElement(file_elem, 'body')

        # Add trans-units
        for idx, segment in enumerate(segments):
            trans_unit = ET.SubElement(
                body,
                'trans-unit',
                id=segment.get('id', str(idx + 1))
            )

            # Source
            source = ET.SubElement(trans_unit, 'source')
            source.text = segment['source']

            # Target (if provided)
            if 'target' in segment and segment['target']:
                target = ET.SubElement(trans_unit, 'target')
                target.text = segment['target']
                target.set('state', segment.get('state', 'translated'))

            # Note/context (if provided)
            if 'context' in segment and segment['context']:
                note = ET.SubElement(trans_unit, 'note')
                note.text = segment['context']

        # Convert to string
        xml_str = ET.tostring(xliff, encoding='unicode')
        return f'<?xml version="1.0" encoding="UTF-8"?>\n{xml_str}'

    def _extract_text_with_tags(self, element) -> str:
        """
        Extract text from element, preserving inline tags like <x/>, <g>.

        XLIFF uses inline tags to represent formatting:
        - <x id="1"/> - standalone tag (like <br/>)
        - <g id="1">text</g> - paired tag (like <b>text</b>)
        - <bx id="1"/>, <ex id="1"/> - begin/end tag pair
        """
        if element.text is None:
            return ''

        # For now, just extract text content
        # TODO: Preserve inline tags in a structured way
        text_parts = [element.text or '']

        for child in element:
            # Add child tag representation
            if child.tag in ['x', 'bx', 'ex']:
                text_parts.append(f'<{child.tag} id="{child.get("id", "")}"/>')
            elif child.tag == 'g':
                text_parts.append(f'<g id="{child.get("id", "")}">{child.text or ""}</g>')

            # Add tail text
            if child.tail:
                text_parts.append(child.tail)

        return ''.join(text_parts)

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
