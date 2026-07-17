"""Text-to-Speech helpers using gTTS."""

import io
import tempfile
from gtts import gTTS
from utils.languages import LANGUAGES, GTTS_CODES


def text_to_speech_bytes(text: str, lang_name: str) -> tuple[bytes | None, str | None]:
    """
    Convert text to MP3 bytes using gTTS.

    Returns (mp3_bytes, error_message).
    error_message is None on success.
    """
    if not text or not text.strip():
        return None, "No text to speak."

    lang_code = LANGUAGES.get(lang_name, "en")
    # Fall back to English if gTTS doesn't support the language
    gtts_code = GTTS_CODES.get(lang_code, "en")

    try:
        tts = gTTS(text=text.strip(), lang=gtts_code, slow=False)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        return buf.read(), None
    except Exception as exc:
        return None, f"TTS error: {exc}"
