"""Translation helpers using deep-translator."""

from deep_translator import GoogleTranslator
from utils.languages import LANGUAGES


def translate_text(text: str, source_name: str, target_name: str) -> tuple[str, str | None]:
    """
    Translate text.

    Returns (translated_text, error_message).
    error_message is None on success.
    """
    if not text or not text.strip():
        return "", "Input text is empty."

    src_code = LANGUAGES.get(source_name, "auto")
    tgt_code = LANGUAGES.get(target_name, "en")

    if src_code == tgt_code and src_code != "auto":
        return text, None  # same language → return as-is

    try:
        translator = GoogleTranslator(source=src_code, target=tgt_code)
        result = translator.translate(text.strip())
        return result or "", None
    except Exception as exc:
        return "", f"Translation failed: {exc}"
