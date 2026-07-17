# VAANI AI — Language Translator

AI-powered desktop language translator with a modern dark UI.

## Features
- **110+ languages** via Google Translate (deep_translator)
- **Voice Input** — speak into your mic to set the input text
- **Text-to-Speech** — hear the translation read aloud
- **Translation History** — last 25 translations, click to restore
- **Swap Languages** — flip source/target with one click
- **Copy** — copy translation to clipboard instantly
- **Clear** — reset everything at once

## How to run

```bash
cd vaani_ai
python main.py
```

## Dependencies

Install via pip:
```bash
pip install -r requirements.txt
```

System packages required (for voice features):
- `portaudio` (microphone input via PyAudio)
- `espeak-ng` (pyttsx3 TTS engine on Linux)
