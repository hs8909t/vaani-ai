"""
VAANI AI — AI-Powered Language Translator
Modern dark UI built with CustomTkinter
"""

import customtkinter as ctk
import threading
import os
from datetime import datetime

# ── Third-party (installed via pip) ──────────────────────────────────────────
try:
    from deep_translator import GoogleTranslator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False

try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False

try:
    import pyttsx3
    TTS_ENGINE = pyttsx3.init()
    TTS_ENGINE.setProperty("rate", 155)
    TTS_AVAILABLE = True
except Exception:
    TTS_ENGINE = None
    TTS_AVAILABLE = False

try:
    import pyperclip
    CLIP_AVAILABLE = True
except ImportError:
    CLIP_AVAILABLE = False

# ── Language map (110 languages) ─────────────────────────────────────────────
LANGUAGES = {
    "Auto Detect":        "auto",
    "Afrikaans":          "af",
    "Albanian":           "sq",
    "Amharic":            "am",
    "Arabic":             "ar",
    "Armenian":           "hy",
    "Azerbaijani":        "az",
    "Basque":             "eu",
    "Belarusian":         "be",
    "Bengali":            "bn",
    "Bosnian":            "bs",
    "Bulgarian":          "bg",
    "Catalan":            "ca",
    "Cebuano":            "ceb",
    "Chichewa":           "ny",
    "Chinese (Simp.)":    "zh-CN",
    "Chinese (Trad.)":    "zh-TW",
    "Corsican":           "co",
    "Croatian":           "hr",
    "Czech":              "cs",
    "Danish":             "da",
    "Dutch":              "nl",
    "English":            "en",
    "Esperanto":          "eo",
    "Estonian":           "et",
    "Filipino":           "tl",
    "Finnish":            "fi",
    "French":             "fr",
    "Frisian":            "fy",
    "Galician":           "gl",
    "Georgian":           "ka",
    "German":             "de",
    "Greek":              "el",
    "Gujarati":           "gu",
    "Haitian Creole":     "ht",
    "Hausa":              "ha",
    "Hawaiian":           "haw",
    "Hebrew":             "iw",
    "Hindi":              "hi",
    "Hmong":              "hmn",
    "Hungarian":          "hu",
    "Icelandic":          "is",
    "Igbo":               "ig",
    "Indonesian":         "id",
    "Irish":              "ga",
    "Italian":            "it",
    "Japanese":           "ja",
    "Javanese":           "jw",
    "Kannada":            "kn",
    "Kazakh":             "kk",
    "Khmer":              "km",
    "Korean":             "ko",
    "Kurdish":            "ku",
    "Kyrgyz":             "ky",
    "Lao":                "lo",
    "Latin":              "la",
    "Latvian":            "lv",
    "Lithuanian":         "lt",
    "Luxembourgish":      "lb",
    "Macedonian":         "mk",
    "Malagasy":           "mg",
    "Malay":              "ms",
    "Malayalam":          "ml",
    "Maltese":            "mt",
    "Maori":              "mi",
    "Marathi":            "mr",
    "Mongolian":          "mn",
    "Myanmar (Burmese)":  "my",
    "Nepali":             "ne",
    "Norwegian":          "no",
    "Odia":               "or",
    "Pashto":             "ps",
    "Persian":            "fa",
    "Polish":             "pl",
    "Portuguese":         "pt",
    "Punjabi":            "pa",
    "Romanian":           "ro",
    "Russian":            "ru",
    "Samoan":             "sm",
    "Scots Gaelic":       "gd",
    "Serbian":            "sr",
    "Sesotho":            "st",
    "Shona":              "sn",
    "Sindhi":             "sd",
    "Sinhala":            "si",
    "Slovak":             "sk",
    "Slovenian":          "sl",
    "Somali":             "so",
    "Spanish":            "es",
    "Sundanese":          "su",
    "Swahili":            "sw",
    "Swedish":            "sv",
    "Tajik":              "tg",
    "Tamil":              "ta",
    "Telugu":             "te",
    "Thai":               "th",
    "Turkish":            "tr",
    "Ukrainian":          "uk",
    "Urdu":               "ur",
    "Uyghur":             "ug",
    "Uzbek":              "uz",
    "Vietnamese":         "vi",
    "Welsh":              "cy",
    "Xhosa":              "xh",
    "Yiddish":            "yi",
    "Yoruba":             "yo",
    "Zulu":               "zu",
}

LANG_NAMES      = list(LANGUAGES.keys())
TARGET_LANGS    = [l for l in LANG_NAMES if l != "Auto Detect"]

# ── Colour palette ────────────────────────────────────────────────────────────
BG_APP          = "#0b0b14"
BG_PANEL        = "#13131f"
BG_CARD         = "#1b1b2c"
BG_INPUT        = "#111120"
BG_OUTPUT       = "#0d1a1f"
ACCENT          = "#4fc3f7"
ACCENT_DIM      = "#1e3a4a"
GREEN           = "#00c98d"
GREEN_DIM       = "#0d3328"
PURPLE          = "#9b59f7"
RED             = "#ff5252"
TEXT_MAIN       = "#e8eaf0"
TEXT_DIM        = "#6a7290"
TEXT_TEAL       = "#80d8c8"
TEXT_WARN       = "#ffd740"


class VAANIApp(ctk.CTk):
    """VAANI AI main window."""

    PLACEHOLDER = "Type or paste text here…"

    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("VAANI AI  —  Language Translator")
        self.geometry("1260x820")
        self.minsize(960, 640)
        self.configure(fg_color=BG_APP)

        self._history: list[dict] = []
        self._history_cards: list[ctk.CTkFrame] = []
        self._recognizer = sr.Recognizer() if SR_AVAILABLE else None
        self._speaking   = False

        self._build_header()
        self._build_body()

    # ── Header ────────────────────────────────────────────────────────────────

    def _build_header(self):
        hdr = ctk.CTkFrame(self, fg_color=BG_PANEL, corner_radius=0, height=72)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        inner = ctk.CTkFrame(hdr, fg_color="transparent")
        inner.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            inner, text="◈  VAANI AI",
            font=ctk.CTkFont("Helvetica", 30, "bold"),
            text_color=ACCENT,
        ).pack(side="left", padx=(0, 18))

        ctk.CTkLabel(
            inner, text="AI-Powered Language Translator  •  110+ Languages",
            font=ctk.CTkFont("Helvetica", 13),
            text_color=TEXT_DIM,
        ).pack(side="left")

    # ── Body ──────────────────────────────────────────────────────────────────

    def _build_body(self):
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=16, pady=(10, 14))

        # Left 3/4 — translator
        left = ctk.CTkFrame(body, fg_color=BG_PANEL, corner_radius=14)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Right 1/4 — history
        right = ctk.CTkFrame(body, fg_color=BG_PANEL, corner_radius=14, width=290)
        right.pack(side="right", fill="both")
        right.pack_propagate(False)

        self._build_translator(left)
        self._build_history_panel(right)

    # ── Translator panel ──────────────────────────────────────────────────────

    def _build_translator(self, parent):
        parent.columnconfigure(0, weight=1)

        # ── Language bar ──
        lang_row = ctk.CTkFrame(parent, fg_color="transparent")
        lang_row.pack(fill="x", padx=18, pady=(16, 8))

        # Source language
        ctk.CTkLabel(lang_row, text="FROM", font=ctk.CTkFont(size=10, weight="bold"),
                     text_color=TEXT_DIM).pack(side="left", padx=(0, 6))

        self._src_var = ctk.StringVar(value="Auto Detect")
        src_combo = ctk.CTkComboBox(
            lang_row, values=LANG_NAMES, variable=self._src_var,
            width=210, height=36,
            font=ctk.CTkFont(size=13),
            fg_color=BG_CARD, border_color=ACCENT_DIM,
            button_color=ACCENT_DIM, button_hover_color="#2a4a60",
            dropdown_fg_color=BG_CARD, dropdown_text_color=TEXT_MAIN,
        )
        src_combo.pack(side="left", padx=(0, 8))

        # Swap button
        swap_btn = ctk.CTkButton(
            lang_row, text="⇄", width=44, height=36,
            font=ctk.CTkFont(size=20),
            fg_color=BG_CARD, hover_color="#252535",
            border_width=1, border_color=ACCENT_DIM,
            command=self._swap_languages,
        )
        swap_btn.pack(side="left", padx=6)

        # Target language
        ctk.CTkLabel(lang_row, text="TO", font=ctk.CTkFont(size=10, weight="bold"),
                     text_color=TEXT_DIM).pack(side="left", padx=(6, 6))

        self._tgt_var = ctk.StringVar(value="English")
        tgt_combo = ctk.CTkComboBox(
            lang_row, values=TARGET_LANGS, variable=self._tgt_var,
            width=210, height=36,
            font=ctk.CTkFont(size=13),
            fg_color=BG_CARD, border_color=ACCENT_DIM,
            button_color=ACCENT_DIM, button_hover_color="#2a4a60",
            dropdown_fg_color=BG_CARD, dropdown_text_color=TEXT_MAIN,
        )
        tgt_combo.pack(side="left")

        # ── Input label ──
        in_label_row = ctk.CTkFrame(parent, fg_color="transparent")
        in_label_row.pack(fill="x", padx=18, pady=(4, 2))
        ctk.CTkLabel(in_label_row, text="INPUT TEXT",
                     font=ctk.CTkFont(size=10, weight="bold"), text_color=TEXT_DIM).pack(side="left")

        # ── Input textbox ──
        in_frame = ctk.CTkFrame(parent, fg_color=BG_INPUT, corner_radius=10,
                                border_width=1, border_color="#1e1e35")
        in_frame.pack(fill="both", expand=True, padx=18, pady=(0, 8))

        self._input = ctk.CTkTextbox(
            in_frame, font=ctk.CTkFont("Helvetica", 15),
            fg_color="transparent", text_color=TEXT_MAIN,
            wrap="word", scrollbar_button_color=BG_CARD,
        )
        self._input.pack(fill="both", expand=True, padx=8, pady=8)
        self._input.insert("0.0", self.PLACEHOLDER)
        self._input.configure(text_color=TEXT_DIM)
        self._input.bind("<FocusIn>",  self._on_input_focus_in)
        self._input.bind("<FocusOut>", self._on_input_focus_out)

        # ── Input action row ──
        in_actions = ctk.CTkFrame(parent, fg_color="transparent")
        in_actions.pack(fill="x", padx=18, pady=(0, 8))

        ctk.CTkButton(
            in_actions, text="🎤  Voice Input", width=148, height=38,
            font=ctk.CTkFont(size=13),
            fg_color="#1a4a80" if SR_AVAILABLE else BG_CARD,
            hover_color="#215a99" if SR_AVAILABLE else BG_CARD,
            command=self._voice_input if SR_AVAILABLE else lambda: self._set_status("SpeechRecognition not installed", RED),
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            in_actions, text="✕  Clear", width=100, height=38,
            font=ctk.CTkFont(size=13),
            fg_color="#2b2b40", hover_color="#363650",
            command=self._clear_all,
        ).pack(side="left")

        ctk.CTkButton(
            in_actions, text="Translate  →", width=160, height=38,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=GREEN_DIM, hover_color="#145040",
            border_width=1, border_color=GREEN,
            text_color=GREEN,
            command=self._translate,
        ).pack(side="right")

        # ── Output label ──
        out_label_row = ctk.CTkFrame(parent, fg_color="transparent")
        out_label_row.pack(fill="x", padx=18, pady=(4, 2))
        ctk.CTkLabel(out_label_row, text="TRANSLATION",
                     font=ctk.CTkFont(size=10, weight="bold"), text_color=TEXT_DIM).pack(side="left")

        # ── Output textbox ──
        out_frame = ctk.CTkFrame(parent, fg_color=BG_OUTPUT, corner_radius=10,
                                 border_width=1, border_color="#0d2030")
        out_frame.pack(fill="both", expand=True, padx=18, pady=(0, 8))

        self._output = ctk.CTkTextbox(
            out_frame, font=ctk.CTkFont("Helvetica", 15),
            fg_color="transparent", text_color=TEXT_TEAL,
            wrap="word", state="disabled",
            scrollbar_button_color=BG_CARD,
        )
        self._output.pack(fill="both", expand=True, padx=8, pady=8)

        # ── Output action row ──
        out_actions = ctk.CTkFrame(parent, fg_color="transparent")
        out_actions.pack(fill="x", padx=18, pady=(0, 16))

        ctk.CTkButton(
            out_actions, text="📋  Copy", width=100, height=38,
            font=ctk.CTkFont(size=13),
            fg_color="#2b2b40", hover_color="#363650",
            command=self._copy_output,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            out_actions, text="🔊  Speak", width=114, height=38,
            font=ctk.CTkFont(size=13),
            fg_color="#2a1a4a" if TTS_AVAILABLE else BG_CARD,
            hover_color="#36215e" if TTS_AVAILABLE else BG_CARD,
            border_width=1 if TTS_AVAILABLE else 0,
            border_color=PURPLE if TTS_AVAILABLE else "transparent",
            text_color=PURPLE if TTS_AVAILABLE else TEXT_DIM,
            command=self._speak_output if TTS_AVAILABLE else lambda: self._set_status("pyttsx3 not installed", RED),
        ).pack(side="left")

        self._status_var = ctk.StringVar(value="")
        self._status_lbl = ctk.CTkLabel(
            out_actions, textvariable=self._status_var,
            font=ctk.CTkFont(size=12), text_color=ACCENT,
        )
        self._status_lbl.pack(side="right")

    # ── History panel ─────────────────────────────────────────────────────────

    def _build_history_panel(self, parent):
        hdr = ctk.CTkFrame(parent, fg_color="transparent")
        hdr.pack(fill="x", padx=12, pady=(14, 6))

        ctk.CTkLabel(hdr, text="📜  HISTORY",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=ACCENT).pack(side="left")

        ctk.CTkButton(
            hdr, text="Clear All", width=68, height=26,
            font=ctk.CTkFont(size=11),
            fg_color="#2b2b40", hover_color="#363650",
            command=self._clear_history,
        ).pack(side="right")

        self._hist_scroll = ctk.CTkScrollableFrame(
            parent, fg_color="transparent",
            scrollbar_button_color=BG_CARD,
        )
        self._hist_scroll.pack(fill="both", expand=True, padx=8, pady=(0, 12))
        self._hist_scroll.columnconfigure(0, weight=1)

    # ── Placeholder helpers ───────────────────────────────────────────────────

    def _on_input_focus_in(self, _event=None):
        if self._input.get("0.0", "end").strip() == self.PLACEHOLDER:
            self._input.delete("0.0", "end")
            self._input.configure(text_color=TEXT_MAIN)

    def _on_input_focus_out(self, _event=None):
        if not self._input.get("0.0", "end").strip():
            self._input.insert("0.0", self.PLACEHOLDER)
            self._input.configure(text_color=TEXT_DIM)

    # ── Status helper ─────────────────────────────────────────────────────────

    def _set_status(self, msg: str, color: str = ACCENT):
        self._status_var.set(msg)
        self._status_lbl.configure(text_color=color)

    # ── Translate ─────────────────────────────────────────────────────────────

    def _translate(self):
        text = self._input.get("0.0", "end").strip()
        if not text or text == self.PLACEHOLDER:
            self._set_status("⚠  Enter text first", RED)
            return
        if not TRANSLATOR_AVAILABLE:
            self._set_status("deep_translator not installed", RED)
            return

        src = LANGUAGES.get(self._src_var.get(), "auto")
        tgt = LANGUAGES.get(self._tgt_var.get(), "en")
        self._set_status("Translating…", TEXT_WARN)
        threading.Thread(target=self._do_translate, args=(text, src, tgt), daemon=True).start()

    def _do_translate(self, text: str, src: str, tgt: str):
        try:
            result = GoogleTranslator(source=src, target=tgt).translate(text)
            self.after(0, self._show_result, result, text)
        except Exception as exc:
            self.after(0, self._set_status, f"Error: {str(exc)[:50]}", RED)

    def _show_result(self, result: str, original: str):
        self._output.configure(state="normal")
        self._output.delete("0.0", "end")
        self._output.insert("0.0", result)
        self._output.configure(state="disabled")
        self._set_status("✓  Translation complete", GREEN)
        self._push_history(original, result)

    # ── Swap languages ────────────────────────────────────────────────────────

    def _swap_languages(self):
        src = self._src_var.get()
        tgt = self._tgt_var.get()
        if src == "Auto Detect":
            src = "English"
        self._src_var.set(tgt)
        self._tgt_var.set(src)

        out = self._output.get("0.0", "end").strip()
        if out:
            self._input.delete("0.0", "end")
            self._input.insert("0.0", out)
            self._input.configure(text_color=TEXT_MAIN)
            self._output.configure(state="normal")
            self._output.delete("0.0", "end")
            self._output.configure(state="disabled")

    # ── Clear ─────────────────────────────────────────────────────────────────

    def _clear_all(self):
        self._input.delete("0.0", "end")
        self._input.insert("0.0", self.PLACEHOLDER)
        self._input.configure(text_color=TEXT_DIM)
        self._output.configure(state="normal")
        self._output.delete("0.0", "end")
        self._output.configure(state="disabled")
        self._set_status("")

    # ── Copy ──────────────────────────────────────────────────────────────────

    def _copy_output(self):
        text = self._output.get("0.0", "end").strip()
        if not text:
            self._set_status("Nothing to copy", TEXT_WARN)
            return
        if CLIP_AVAILABLE:
            try:
                pyperclip.copy(text)
                self._set_status("✓  Copied to clipboard", GREEN)
            except Exception:
                self._fallback_copy(text)
        else:
            self._fallback_copy(text)

    def _fallback_copy(self, text: str):
        try:
            self.clipboard_clear()
            self.clipboard_append(text)
            self._set_status("✓  Copied (tk)", GREEN)
        except Exception:
            self._set_status("Copy failed", RED)

    # ── Voice input ───────────────────────────────────────────────────────────

    def _voice_input(self):
        self._set_status("🎤  Listening…  (speak now)", ACCENT)
        threading.Thread(target=self._do_voice, daemon=True).start()

    def _do_voice(self):
        try:
            with sr.Microphone() as mic:
                self._recognizer.adjust_for_ambient_noise(mic, duration=0.4)
                audio = self._recognizer.listen(mic, timeout=8, phrase_time_limit=20)
            text = self._recognizer.recognize_google(audio)
            self.after(0, self._apply_voice, text)
        except sr.WaitTimeoutError:
            self.after(0, self._set_status, "⚠  No speech detected", RED)
        except sr.UnknownValueError:
            self.after(0, self._set_status, "⚠  Could not understand audio", RED)
        except Exception as exc:
            self.after(0, self._set_status, f"Mic error: {str(exc)[:45]}", RED)

    def _apply_voice(self, text: str):
        self._input.delete("0.0", "end")
        self._input.insert("0.0", text)
        self._input.configure(text_color=TEXT_MAIN)
        self._set_status("✓  Voice captured", GREEN)

    # ── Text-to-Speech ────────────────────────────────────────────────────────

    def _speak_output(self):
        text = self._output.get("0.0", "end").strip()
        if not text:
            self._set_status("Nothing to speak", TEXT_WARN)
            return
        if self._speaking:
            return
        self._speaking = True
        self._set_status("🔊  Speaking…", PURPLE)
        threading.Thread(target=self._do_speak, args=(text,), daemon=True).start()

    def _do_speak(self, text: str):
        try:
            TTS_ENGINE.say(text)
            TTS_ENGINE.runAndWait()
            self.after(0, self._set_status, "✓  Done speaking", GREEN)
        except Exception as exc:
            self.after(0, self._set_status, f"TTS error: {str(exc)[:40]}", RED)
        finally:
            self._speaking = False

    # ── History ───────────────────────────────────────────────────────────────

    def _push_history(self, original: str, translated: str):
        entry = {
            "original":   original,
            "translated": translated,
            "src":        self._src_var.get(),
            "tgt":        self._tgt_var.get(),
            "time":       datetime.now().strftime("%H:%M"),
        }
        self._history.insert(0, entry)
        if len(self._history) > 60:
            self._history.pop()
        self._refresh_history()

    def _clear_history(self):
        self._history.clear()
        for w in self._history_cards:
            w.destroy()
        self._history_cards.clear()

    def _refresh_history(self):
        for w in self._history_cards:
            w.destroy()
        self._history_cards.clear()

        for i, entry in enumerate(self._history[:25]):
            card = ctk.CTkFrame(
                self._hist_scroll,
                fg_color=BG_CARD, corner_radius=8,
                border_width=1, border_color="#22223a",
            )
            card.grid(row=i, column=0, sticky="ew", pady=3, padx=2)
            card.columnconfigure(0, weight=1)

            # Header: route + time
            ctk.CTkLabel(
                card,
                text=f"{entry['src']}  →  {entry['tgt']}   {entry['time']}",
                font=ctk.CTkFont(size=9, weight="bold"),
                text_color=TEXT_DIM, anchor="w",
            ).grid(row=0, column=0, sticky="w", padx=8, pady=(6, 1))

            # Original (truncated)
            orig_text = entry["original"][:72] + ("…" if len(entry["original"]) > 72 else "")
            ctk.CTkLabel(
                card, text=orig_text,
                font=ctk.CTkFont(size=11),
                text_color=TEXT_MAIN, anchor="w",
                wraplength=240, justify="left",
            ).grid(row=1, column=0, sticky="w", padx=8)

            # Translated (truncated)
            tr_text = entry["translated"][:72] + ("…" if len(entry["translated"]) > 72 else "")
            ctk.CTkLabel(
                card, text=tr_text,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=TEXT_TEAL, anchor="w",
                wraplength=240, justify="left",
            ).grid(row=2, column=0, sticky="w", padx=8, pady=(1, 6))

            # Click card to restore
            for widget in [card] + card.winfo_children():
                widget.bind("<Button-1>", lambda e, en=entry: self._restore_history(en))

            self._history_cards.append(card)

    def _restore_history(self, entry: dict):
        self._src_var.set(entry["src"])
        self._tgt_var.set(entry["tgt"])
        self._input.delete("0.0", "end")
        self._input.insert("0.0", entry["original"])
        self._input.configure(text_color=TEXT_MAIN)
        self._output.configure(state="normal")
        self._output.delete("0.0", "end")
        self._output.insert("0.0", entry["translated"])
        self._output.configure(state="disabled")
        self._set_status("✓  Restored from history", ACCENT)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = VAANIApp()
    app.mainloop()
