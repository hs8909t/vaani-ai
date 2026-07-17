# VAANI AI

AI-powered language translator — premium dark web app built with Python + Streamlit.

## Run & Operate

- **Web app:** workflow `VAANI AI Web` — `cd vaani_streamlit && streamlit run app.py --server.port 8000`
- **Desktop app (legacy):** workflow `VAANI AI` — CustomTkinter VNC app
- Streamlit entry point: `vaani_streamlit/app.py`

## Stack

- Python 3.11, Streamlit 1.59
- Translation: deep-translator (GoogleTranslator, 110+ languages)
- Voice input: SpeechRecognition + st.audio_input()
- TTS: gTTS (Google Text-to-Speech → MP3 → st.audio())
- History: local JSON file (`vaani_streamlit/translation_history.json`)
- Clipboard: pyperclip

## Where things live

```
vaani_streamlit/
├── app.py                      ← main Streamlit UI + all page logic
├── utils/
│   ├── languages.py            ← language map (110+ langs, gTTS codes)
│   ├── translator.py           ← GoogleTranslator wrapper
│   ├── history.py              ← JSON-based history persistence
│   └── tts.py                  ← gTTS → MP3 bytes helper
├── .streamlit/config.toml      ← server port + dark theme
├── translation_history.json    ← auto-created, stores last 50 entries
└── requirements.txt
```

## Gotchas

- Streamlit runs on port 8000 (not the default 8501)
- Voice input uses `st.audio_input()` — requires Streamlit ≥ 1.23
- gTTS requires internet access for audio generation
- History is written to disk at `vaani_streamlit/translation_history.json`

## Pointers

- See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details
