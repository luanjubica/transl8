import deepl
from typing import List, Optional
from app.core.config import settings


class TranslationService:
    """
    Translation service using DeepL API.

    Provides AI-powered translation with support for glossaries
    and translation memory.
    """

    def __init__(self):
        """Initialize DeepL translator."""
        if settings.DEEPL_API_KEY:
            self.translator = deepl.Translator(settings.DEEPL_API_KEY)
            self.enabled = True
        else:
            self.translator = None
            self.enabled = False

    def translate_text(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        glossary_id: Optional[str] = None,
        preserve_formatting: bool = True
    ) -> str:
        """
        Translate text using DeepL.

        Args:
            text: Source text to translate
            source_lang: Source language code (e.g., 'EN', 'DE')
            target_lang: Target language code
            glossary_id: Optional DeepL glossary ID
            preserve_formatting: Preserve formatting tags

        Returns:
            Translated text

        Raises:
            Exception: If translation fails or service not configured
        """
        if not self.enabled:
            raise Exception("DeepL API key not configured")

        try:
            # Convert ISO 639-1 to DeepL format (e.g., 'en' -> 'EN')
            source_lang = source_lang.upper()
            target_lang = target_lang.upper()

            # Special handling for English and Portuguese variants
            if target_lang == 'EN':
                target_lang = 'EN-US'  # or 'EN-GB'
            elif target_lang == 'PT':
                target_lang = 'PT-BR'  # or 'PT-PT'

            # Translate
            result = self.translator.translate_text(
                text,
                source_lang=source_lang if source_lang != 'AUTO' else None,
                target_lang=target_lang,
                preserve_formatting=preserve_formatting,
                glossary=glossary_id
            )

            return result.text

        except deepl.DeepLException as e:
            raise Exception(f"DeepL translation failed: {str(e)}")

    def translate_batch(
        self,
        texts: List[str],
        source_lang: str,
        target_lang: str,
        glossary_id: Optional[str] = None
    ) -> List[str]:
        """
        Translate multiple texts in batch.

        More efficient than individual translations for large documents.

        Args:
            texts: List of source texts
            source_lang: Source language code
            target_lang: Target language code
            glossary_id: Optional DeepL glossary ID

        Returns:
            List of translated texts

        Raises:
            Exception: If translation fails
        """
        if not self.enabled:
            raise Exception("DeepL API key not configured")

        try:
            source_lang = source_lang.upper()
            target_lang = target_lang.upper()

            if target_lang == 'EN':
                target_lang = 'EN-US'
            elif target_lang == 'PT':
                target_lang = 'PT-BR'

            results = self.translator.translate_text(
                texts,
                source_lang=source_lang if source_lang != 'AUTO' else None,
                target_lang=target_lang,
                glossary=glossary_id
            )

            return [result.text for result in results]

        except deepl.DeepLException as e:
            raise Exception(f"DeepL batch translation failed: {str(e)}")

    def get_usage(self) -> dict:
        """
        Get DeepL API usage statistics.

        Returns:
            Dict with character usage and limits
        """
        if not self.enabled:
            return {"error": "DeepL API not configured"}

        try:
            usage = self.translator.get_usage()
            return {
                "character_count": usage.character.count,
                "character_limit": usage.character.limit,
                "usage_percent": (usage.character.count / usage.character.limit * 100) if usage.character.limit else 0
            }
        except deepl.DeepLException as e:
            return {"error": str(e)}

    def get_supported_languages(self) -> dict:
        """
        Get list of supported languages.

        Returns:
            Dict with source and target languages
        """
        if not self.enabled:
            return {"error": "DeepL API not configured"}

        try:
            source_langs = self.translator.get_source_languages()
            target_langs = self.translator.get_target_languages()

            return {
                "source": [{"code": lang.code, "name": lang.name} for lang in source_langs],
                "target": [{"code": lang.code, "name": lang.name} for lang in target_langs]
            }
        except deepl.DeepLException as e:
            return {"error": str(e)}


# Global translation service instance
translation_service = TranslationService()
