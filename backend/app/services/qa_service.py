import re
from typing import List, Dict, Any, Optional


class QAService:
    """
    Quality Assurance service for translations.

    Validates translations for:
    - Placeholder consistency
    - Length constraints
    - Tag preservation
    - Formatting issues
    """

    @staticmethod
    def detect_placeholders(text: str) -> List[str]:
        """
        Detect placeholders in text.

        Supports common placeholder formats:
        - {variable}
        - {0}, {1}
        - %s, %d, %f
        - %(name)s
        - %1$s, %2$d
        - {{variable}}
        - $variable

        Args:
            text: Text to analyze

        Returns:
            List of detected placeholders
        """
        patterns = [
            r'\{[^}]+\}',           # {variable}, {0}
            r'%\([^)]+\)[sdf]',     # %(name)s
            r'%\d+\$[sdf]',         # %1$s
            r'%[sdf]',              # %s
            r'\{\{[^}]+\}\}',       # {{variable}}
            r'\$[a-zA-Z_][a-zA-Z0-9_]*'  # $variable
        ]

        placeholders = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            placeholders.extend(matches)

        return list(set(placeholders))  # Remove duplicates

    @staticmethod
    def validate_placeholders(
        source_text: str,
        translated_text: str
    ) -> Dict[str, Any]:
        """
        Validate that placeholders are preserved in translation.

        Args:
            source_text: Original text
            translated_text: Translated text

        Returns:
            Dict with validation results
        """
        source_placeholders = set(QAService.detect_placeholders(source_text))
        target_placeholders = set(QAService.detect_placeholders(translated_text))

        missing = source_placeholders - target_placeholders
        extra = target_placeholders - source_placeholders

        is_valid = len(missing) == 0 and len(extra) == 0

        result = {
            "valid": is_valid,
            "source_placeholders": list(source_placeholders),
            "target_placeholders": list(target_placeholders)
        }

        if missing:
            result["missing"] = list(missing)
            result["error"] = f"Missing placeholders: {', '.join(missing)}"

        if extra:
            result["extra"] = list(extra)
            result["warning"] = f"Extra placeholders: {', '.join(extra)}"

        return result

    @staticmethod
    def check_length_constraint(
        text: str,
        max_length: Optional[int]
    ) -> Dict[str, Any]:
        """
        Check if text exceeds length constraint.

        Args:
            text: Text to check
            max_length: Maximum allowed length (None = no limit)

        Returns:
            Dict with length check results
        """
        length = len(text)

        result = {
            "length": length,
            "max_length": max_length,
            "valid": True
        }

        if max_length and length > max_length:
            result["valid"] = False
            result["exceeded_by"] = length - max_length
            result["error"] = f"Text exceeds maximum length by {length - max_length} characters"

        return result

    @staticmethod
    def detect_tags(text: str) -> List[str]:
        """
        Detect HTML/XML tags in text.

        Args:
            text: Text to analyze

        Returns:
            List of detected tags
        """
        # Match opening and self-closing tags
        tags = re.findall(r'<[^>]+>', text)
        return tags

    @staticmethod
    def validate_tags(
        source_text: str,
        translated_text: str
    ) -> Dict[str, Any]:
        """
        Validate that tags are preserved in translation.

        Args:
            source_text: Original text
            translated_text: Translated text

        Returns:
            Dict with validation results
        """
        source_tags = QAService.detect_tags(source_text)
        target_tags = QAService.detect_tags(translated_text)

        # For tags, order matters
        is_valid = source_tags == target_tags

        result = {
            "valid": is_valid,
            "source_tags": source_tags,
            "target_tags": target_tags
        }

        if not is_valid:
            result["error"] = "Tags do not match between source and translation"

        return result

    @staticmethod
    def run_full_qa(
        source_text: str,
        translated_text: str,
        max_length: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Run comprehensive QA checks on translation.

        Args:
            source_text: Original text
            translated_text: Translated text
            max_length: Optional length constraint

        Returns:
            Dict with all QA results
        """
        placeholder_check = QAService.validate_placeholders(source_text, translated_text)
        length_check = QAService.check_length_constraint(translated_text, max_length)
        tag_check = QAService.validate_tags(source_text, translated_text)

        warnings = []
        errors = []

        # Collect warnings and errors
        if not placeholder_check["valid"]:
            errors.append(placeholder_check.get("error", "Placeholder validation failed"))
            if "warning" in placeholder_check:
                warnings.append(placeholder_check["warning"])

        if not length_check["valid"]:
            warnings.append(length_check.get("error", "Length constraint exceeded"))

        if not tag_check["valid"]:
            errors.append(tag_check.get("error", "Tag validation failed"))

        return {
            "passed": len(errors) == 0,
            "warnings": warnings,
            "errors": errors,
            "checks": {
                "placeholders": placeholder_check,
                "length": length_check,
                "tags": tag_check
            }
        }


# Global QA service instance
qa_service = QAService()
