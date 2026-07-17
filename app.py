"""
VAANI AI — Professional Language Translator
Built with Streamlit | Premium Dark UI
"""

import io
import sys
import os
import zipfile

# Allow imports from this directory when run via `streamlit run`
sys.path.insert(0, os.path.dirname(__file__))


# ── Project ZIP builder ────────────────────────────────────────────────────────
def _build_project_zip() -> bytes:
    """Zip the key project source files in-memory and return raw bytes."""
    ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # Directories / files to include (relative to ROOT)
    INCLUDE_DIRS = ["vaani_streamlit", "vaani_ai", "artifacts/api-server/src"]
    INCLUDE_FILES = [
        ".replit", "replit.md", "replit.nix", "pyproject.toml",
        "package.json", "pnpm-workspace.yaml", "pnpm-lock.yaml",
        "tsconfig.base.json",
    ]

    # Patterns to skip even when inside an included dir
    SKIP = {
        "__pycache__", ".pythonlibs", "node_modules", "dist",
        ".cache", ".git", "translation_history.json",
        "artifact.edit.toml",
    }

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        # Walk included directories
        for rel_dir in INCLUDE_DIRS:
            abs_dir = os.path.join(ROOT, rel_dir)
            if not os.path.isdir(abs_dir):
                continue
            for dirpath, dirnames, filenames in os.walk(abs_dir):
                # Prune skipped dirs in-place so os.walk won't descend into them
                dirnames[:] = [d for d in dirnames if d not in SKIP]
                for fname in filenames:
                    if any(s in fname for s in SKIP):
                        continue
                    abs_file = os.path.join(dirpath, fname)
                    arc_name = os.path.relpath(abs_file, ROOT)
                    zf.write(abs_file, arc_name)
        # Add top-level files
        for rel_file in INCLUDE_FILES:
            abs_file = os.path.join(ROOT, rel_file)
            if os.path.isfile(abs_file):
                zf.write(abs_file, rel_file)

    buf.seek(0)
    return buf.read()

import streamlit as st
from utils.languages import SOURCE_LANGUAGE_NAMES, TARGET_LANGUAGE_NAMES, LANGUAGES
from utils.translator import translate_text
from utils.history import add_entry, get_history, clear_history
from utils.tts import text_to_speech_bytes

# ── Page configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="VAANI AI — Language Translator",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Reset & base ─────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background: #070714 !important;
    font-family: 'Inter', sans-serif;
}

[data-testid="stAppViewContainer"] {
    background: radial-gradient(ellipse at 20% 0%, #0d1854 0%, #070714 50%),
                radial-gradient(ellipse at 80% 100%, #0a1a40 0%, transparent 50%) !important;
    background-blend-mode: screen !important;
    min-height: 100vh;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }
[data-testid="stDecoration"] { display: none; }

/* ── Sidebar ──────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #08081e 0%, #0b0b24 100%) !important;
    border-right: 1px solid rgba(99, 102, 241, 0.15) !important;
}
[data-testid="stSidebar"] > div { padding-top: 1rem; }

/* ── Logo header ──────────────────────────────── */
.vaani-hero {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
    margin-bottom: 0.5rem;
}
.vaani-logo-ring {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 74px; height: 74px;
    border-radius: 22px;
    background: linear-gradient(135deg, #3b82f6, #6366f1, #8b5cf6);
    box-shadow: 0 0 40px rgba(99, 102, 241, 0.5), 0 0 80px rgba(59, 130, 246, 0.2);
    margin: 0 auto 1rem;
    font-size: 2rem;
    animation: pulse-glow 3s ease-in-out infinite;
}
@keyframes pulse-glow {
    0%, 100% { box-shadow: 0 0 40px rgba(99,102,241,0.5), 0 0 80px rgba(59,130,246,0.2); }
    50%       { box-shadow: 0 0 60px rgba(99,102,241,0.8), 0 0 120px rgba(59,130,246,0.35); }
}
.vaani-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.8rem;
    font-weight: 800;
    background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 50%, #38bdf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.5px;
    margin: 0;
    line-height: 1;
}
.vaani-tagline {
    color: #64748b;
    font-size: 0.9rem;
    margin-top: 0.5rem;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    font-weight: 500;
}
.vaani-badge-row {
    display: flex;
    justify-content: center;
    gap: 0.5rem;
    margin-top: 0.8rem;
    flex-wrap: wrap;
}
.vaani-badge {
    background: rgba(99,102,241,0.12);
    border: 1px solid rgba(99,102,241,0.25);
    color: #818cf8;
    border-radius: 50px;
    padding: 0.2rem 0.75rem;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.5px;
}

/* ── Glass cards ──────────────────────────────── */
.glass-card {
    background: linear-gradient(135deg,
        rgba(255,255,255,0.04) 0%,
        rgba(255,255,255,0.02) 100%);
    border: 1px solid rgba(99,102,241,0.18);
    border-radius: 16px;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
}
.lang-label {
    color: #94a3b8;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
}

/* ── Text areas ───────────────────────────────── */
textarea {
    background: rgba(15, 15, 40, 0.8) !important;
    border: 1px solid rgba(99, 102, 241, 0.2) !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
    font-size: 1rem !important;
    line-height: 1.65 !important;
    padding: 1rem !important;
    transition: border-color 0.2s ease !important;
    resize: vertical !important;
}
textarea:focus {
    border-color: rgba(99, 102, 241, 0.55) !important;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
    outline: none !important;
}

/* Output read-only area */
.output-box {
    background: linear-gradient(135deg, rgba(14,22,59,0.9) 0%, rgba(10,16,44,0.9) 100%);
    border: 1px solid rgba(56,189,248,0.2);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    min-height: 200px;
    color: #7dd3fc;
    font-size: 1rem;
    line-height: 1.7;
    white-space: pre-wrap;
    word-wrap: break-word;
    transition: border-color 0.2s ease;
}
.output-box.has-content {
    border-color: rgba(56,189,248,0.35);
    box-shadow: 0 0 30px rgba(14,165,233,0.08);
}
.output-placeholder {
    color: #334155;
    font-style: italic;
    font-size: 0.95rem;
}

/* ── Select boxes ─────────────────────────────── */
[data-testid="stSelectbox"] > div > div {
    background: rgba(15,15,40,0.85) !important;
    border: 1px solid rgba(99,102,241,0.25) !important;
    border-radius: 10px !important;
    color: #c7d2fe !important;
}

/* ── Buttons ──────────────────────────────────── */
.stButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    letter-spacing: 0.3px !important;
    transition: all 0.2s ease !important;
    border: none !important;
    padding: 0.55rem 1.1rem !important;
}

/* Primary – Translate */
.btn-translate > button {
    background: linear-gradient(135deg, #2563eb, #4f46e5) !important;
    color: #fff !important;
    box-shadow: 0 4px 20px rgba(79,70,229,0.4) !important;
    width: 100% !important;
    padding: 0.7rem 1.4rem !important;
    font-size: 1rem !important;
}
.btn-translate > button:hover {
    background: linear-gradient(135deg, #1d4ed8, #4338ca) !important;
    box-shadow: 0 6px 28px rgba(79,70,229,0.55) !important;
    transform: translateY(-1px) !important;
}

/* Swap */
.btn-swap > button {
    background: rgba(99,102,241,0.12) !important;
    color: #818cf8 !important;
    border: 1px solid rgba(99,102,241,0.3) !important;
    width: 100% !important;
    font-size: 1.1rem !important;
}
.btn-swap > button:hover {
    background: rgba(99,102,241,0.22) !important;
    color: #a5b4fc !important;
}

/* Secondary buttons */
.btn-copy > button, .btn-clear > button, .btn-speak > button {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: #94a3b8 !important;
    width: 100% !important;
}
.btn-copy > button:hover  { background: rgba(56,189,248,0.12) !important; color: #38bdf8 !important; border-color: rgba(56,189,248,0.3) !important; }
.btn-clear > button:hover { background: rgba(239,68,68,0.1)  !important; color: #f87171 !important; border-color: rgba(239,68,68,0.25) !important; }
.btn-speak > button:hover { background: rgba(168,85,247,0.12) !important; color: #c084fc !important; border-color: rgba(168,85,247,0.3) !important; }

/* Voice button */
.btn-voice > button {
    background: linear-gradient(135deg, rgba(20,83,184,0.35), rgba(79,70,229,0.25)) !important;
    border: 1px solid rgba(99,102,241,0.35) !important;
    color: #93c5fd !important;
    width: 100% !important;
}
.btn-voice > button:hover {
    background: linear-gradient(135deg, rgba(20,83,184,0.5), rgba(79,70,229,0.4)) !important;
    color: #bfdbfe !important;
}

/* ── Section labels ───────────────────────────── */
.section-label {
    color: #64748b;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin: 0.3rem 0 0.5rem;
}

/* ── Divider ──────────────────────────────────── */
.gradient-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(99,102,241,0.35), transparent);
    margin: 1.5rem 0;
}

/* ── Toast-style notices ──────────────────────── */
.notice-success {
    background: rgba(16,185,129,0.1);
    border: 1px solid rgba(16,185,129,0.25);
    border-radius: 8px;
    color: #34d399;
    padding: 0.5rem 0.8rem;
    font-size: 0.82rem;
    font-weight: 500;
    margin-top: 0.4rem;
}
.notice-error {
    background: rgba(239,68,68,0.1);
    border: 1px solid rgba(239,68,68,0.25);
    border-radius: 8px;
    color: #f87171;
    padding: 0.5rem 0.8rem;
    font-size: 0.82rem;
    margin-top: 0.4rem;
}

/* ── Char counter ─────────────────────────────── */
.char-count {
    color: #475569;
    font-size: 0.75rem;
    text-align: right;
    margin-top: 0.25rem;
}

/* ── History sidebar ──────────────────────────── */
.hist-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(99,102,241,0.12);
    border-radius: 10px;
    padding: 0.65rem 0.8rem;
    margin-bottom: 0.55rem;
    cursor: pointer;
    transition: border-color 0.15s ease, background 0.15s ease;
}
.hist-card:hover {
    border-color: rgba(99,102,241,0.3);
    background: rgba(99,102,241,0.07);
}
.hist-meta {
    color: #475569;
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.5px;
    margin-bottom: 0.3rem;
}
.hist-orig {
    color: #94a3b8;
    font-size: 0.8rem;
    line-height: 1.4;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.hist-trans {
    color: #60a5fa;
    font-size: 0.8rem;
    font-weight: 500;
    line-height: 1.4;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin-top: 0.15rem;
}

/* ── Footer ───────────────────────────────────── */
.vaani-footer {
    text-align: center;
    padding: 2rem 1rem 1.5rem;
    border-top: 1px solid rgba(99,102,241,0.12);
    margin-top: 2rem;
}
.vaani-footer-brand {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    background: linear-gradient(135deg, #60a5fa, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.vaani-footer-sub {
    color: #334155;
    font-size: 0.75rem;
    margin-top: 0.3rem;
}

/* ── Voice recording area ─────────────────────── */
[data-testid="stAudioInput"] {
    border-radius: 12px !important;
}

/* ── Spinner overlay ──────────────────────────── */
.translate-spinner {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    color: #818cf8;
    font-size: 0.88rem;
    padding: 0.8rem 0;
}

/* ── Mobile responsiveness ────────────────────── */
@media (max-width: 768px) {
    .vaani-title { font-size: 2rem; }
    .vaani-logo-ring { width: 56px; height: 56px; font-size: 1.5rem; }
}

/* ── Download ZIP button ──────────────────────── */
.btn-download > div > button,
.btn-download > div > button:hover,
.btn-download > div > button:focus {
    background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%) !important;
    color: #ffffff !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.5px !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.75rem 1.5rem !important;
    box-shadow: 0 0 24px rgba(34,197,94,0.5), 0 4px 16px rgba(0,0,0,0.4) !important;
    transition: all 0.2s ease !important;
    cursor: pointer !important;
}
.btn-download > div > button:hover {
    box-shadow: 0 0 40px rgba(34,197,94,0.75), 0 6px 20px rgba(0,0,0,0.5) !important;
    transform: translateY(-2px) !important;
}
</style>
""", unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────────
def _init_state():
    defaults = {
        "input_text":        "",
        "output_text":       "",
        "src_lang":          "Auto Detect",
        "tgt_lang":          "English",
        "tts_audio":         None,
        "copied":            False,
        "error_msg":         "",
        "show_voice":        False,
        "voice_transcript":  "",
        "char_count":        0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:0.5rem 0 1.2rem;">
        <div style="font-family:'Space Grotesk',sans-serif; font-size:1.15rem; font-weight:700;
                    background:linear-gradient(135deg,#60a5fa,#a78bfa);
                    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                    background-clip:text;">🌐 VAANI AI</div>
        <div style="color:#334155; font-size:0.7rem; letter-spacing:1px; margin-top:0.2rem;">
            RECENT TRANSLATIONS
        </div>
    </div>
    """, unsafe_allow_html=True)

    history = get_history()

    if history:
        if st.button("🗑️ Clear History", use_container_width=True, key="clear_hist_btn"):
            clear_history()
            st.rerun()

        for i, entry in enumerate(history[:20]):
            orig_short  = entry["original"][:55]  + ("…" if len(entry["original"]) > 55 else "")
            trans_short = entry["translated"][:55] + ("…" if len(entry["translated"]) > 55 else "")
            st.markdown(f"""
            <div class="hist-card">
                <div class="hist-meta">{entry.get('src','?')} → {entry.get('tgt','?')}  &nbsp;·&nbsp;  {entry.get('time','')}</div>
                <div class="hist-orig">{orig_short}</div>
                <div class="hist-trans">{trans_short}</div>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"↩ Restore", key=f"restore_{i}", use_container_width=True):
                st.session_state.input_text  = entry["original"]
                st.session_state.output_text = entry["translated"]
                st.session_state.src_lang    = entry.get("src", "Auto Detect")
                st.session_state.tgt_lang    = entry.get("tgt", "English")
                st.rerun()
    else:
        st.markdown("""
        <div style="text-align:center; color:#1e293b; font-size:0.82rem; padding:2rem 0;">
            No translations yet.<br>Start translating to build your history.
        </div>
        """, unsafe_allow_html=True)

    # ── Download project ──
    st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="color:#475569; font-size:0.7rem; letter-spacing:0.8px;
                text-transform:uppercase; text-align:center; margin-bottom:0.4rem;">
        Export Project
    </div>
    """, unsafe_allow_html=True)
    try:
        zip_bytes = _build_project_zip()
        st.download_button(
            label="⬇️  Download ZIP",
            data=zip_bytes,
            file_name="vaani-ai-project.zip",
            mime="application/zip",
            use_container_width=True,
            key="download_zip_btn",
        )
    except Exception as _e:
        st.caption(f"ZIP unavailable: {_e}")

    # ── Sidebar footer ──
    st.markdown("""
    <div style="text-align:center; margin-top:1rem;">
        <div style="color:#1e293b; font-size:0.68rem; letter-spacing:0.5px;">
            Powered by Google Translate<br>via deep-translator
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Main content ──────────────────────────────────────────────────────────────

# Hero header
st.markdown("""
<div class="vaani-hero">
    <div class="vaani-logo-ring">🌐</div>
    <div class="vaani-title">VAANI AI</div>
    <div class="vaani-tagline">AI-Powered Language Translator</div>
    <div class="vaani-badge-row">
        <span class="vaani-badge">110+ Languages</span>
        <span class="vaani-badge">Auto Detect</span>
        <span class="vaani-badge">Voice Input</span>
        <span class="vaani-badge">Text-to-Speech</span>
    </div>
</div>
<div class="gradient-divider"></div>
""", unsafe_allow_html=True)

# ── Download button (hero area) ───────────────────────────────────────────────
try:
    import base64 as _b64
    _zip_bytes = _build_project_zip()
    _b64_zip   = _b64.b64encode(_zip_bytes).decode()
    st.markdown(f"""
    <div style="display:flex; justify-content:center; margin: 0.6rem 0 1rem;">
        <a href="data:application/zip;base64,{_b64_zip}"
           download="vaani-ai-project.zip"
           style="
               display: inline-flex;
               align-items: center;
               gap: 0.5rem;
               background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
               color: #ffffff;
               font-family: 'Space Grotesk', sans-serif;
               font-size: 1.05rem;
               font-weight: 700;
               letter-spacing: 0.4px;
               text-decoration: none;
               padding: 0.75rem 2.5rem;
               border-radius: 12px;
               box-shadow: 0 0 28px rgba(34,197,94,0.55), 0 4px 16px rgba(0,0,0,0.4);
               transition: all 0.2s ease;
           "
           onmouseover="this.style.boxShadow='0 0 44px rgba(34,197,94,0.8), 0 6px 22px rgba(0,0,0,0.5)'; this.style.transform='translateY(-2px)'"
           onmouseout="this.style.boxShadow='0 0 28px rgba(34,197,94,0.55), 0 4px 16px rgba(0,0,0,0.4)'; this.style.transform='translateY(0)'"
        >
            ⬇️&nbsp; Download Project ZIP
        </a>
    </div>
    """, unsafe_allow_html=True)
except Exception as _ex:
    st.error(f"ZIP unavailable: {_ex}")

st.markdown("<div style='height:0.2rem'></div>", unsafe_allow_html=True)

# ── Language selector row ─────────────────────────────────────────────────────
col_src, col_swap, col_tgt = st.columns([5, 1, 5])

with col_src:
    st.markdown('<div class="lang-label">Source Language</div>', unsafe_allow_html=True)
    src_lang = st.selectbox(
        label="source_lang",
        options=SOURCE_LANGUAGE_NAMES,
        index=SOURCE_LANGUAGE_NAMES.index(st.session_state.src_lang)
            if st.session_state.src_lang in SOURCE_LANGUAGE_NAMES else 0,
        label_visibility="collapsed",
        key="src_select",
    )
    st.session_state.src_lang = src_lang

with col_swap:
    st.markdown("<div style='height:1.7rem'></div>", unsafe_allow_html=True)
    st.markdown('<div class="btn-swap">', unsafe_allow_html=True)
    if st.button("⇄", key="swap_btn", help="Swap languages", use_container_width=True):
        current_src = st.session_state.src_lang
        current_tgt = st.session_state.tgt_lang
        # Auto Detect can't be target — fall back to English
        new_src = current_tgt
        new_tgt = current_src if current_src != "Auto Detect" else "English"
        st.session_state.src_lang    = new_src
        st.session_state.tgt_lang    = new_tgt
        # Swap text as well
        st.session_state.input_text  = st.session_state.output_text
        st.session_state.output_text = ""
        st.session_state.tts_audio   = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with col_tgt:
    st.markdown('<div class="lang-label">Target Language</div>', unsafe_allow_html=True)
    tgt_lang = st.selectbox(
        label="target_lang",
        options=TARGET_LANGUAGE_NAMES,
        index=TARGET_LANGUAGE_NAMES.index(st.session_state.tgt_lang)
            if st.session_state.tgt_lang in TARGET_LANGUAGE_NAMES else
            TARGET_LANGUAGE_NAMES.index("English"),
        label_visibility="collapsed",
        key="tgt_select",
    )
    st.session_state.tgt_lang = tgt_lang


st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)


# ── Text areas ────────────────────────────────────────────────────────────────
left_col, right_col = st.columns(2, gap="large")

with left_col:
    st.markdown('<div class="section-label">Input Text</div>', unsafe_allow_html=True)

    input_text = st.text_area(
        label="input_area",
        value=st.session_state.input_text,
        height=240,
        placeholder="Type or paste text here…  (or use Voice Input below)",
        label_visibility="collapsed",
        key="input_area_widget",
    )
    st.session_state.input_text = input_text
    char_count = len(input_text)
    st.markdown(f'<div class="char-count">{char_count:,} characters</div>', unsafe_allow_html=True)

    # Voice input expander
    with st.expander("🎤  Voice Input", expanded=st.session_state.show_voice):
        st.markdown(
            '<div style="color:#64748b; font-size:0.8rem; margin-bottom:0.5rem;">'
            'Click the microphone, record your speech, then click <b>Use This Recording</b>.</div>',
            unsafe_allow_html=True,
        )
        audio_data = st.audio_input("Record voice", label_visibility="collapsed", key="voice_recorder")
        if audio_data is not None:
            use_voice = st.button("✅  Use This Recording", key="use_voice", use_container_width=True)
            if use_voice:
                with st.spinner("Transcribing audio…"):
                    try:
                        import speech_recognition as sr
                        r = sr.Recognizer()
                        audio_bytes = io.BytesIO(audio_data.read())
                        with sr.AudioFile(audio_bytes) as source:
                            audio_captured = r.record(source)
                        transcript = r.recognize_google(audio_captured)
                        st.session_state.input_text = transcript
                        st.session_state.show_voice = False
                        st.rerun()
                    except Exception as exc:
                        st.markdown(
                            f'<div class="notice-error">Transcription failed: {exc}</div>',
                            unsafe_allow_html=True,
                        )

with right_col:
    st.markdown('<div class="section-label">Translation</div>', unsafe_allow_html=True)

    output_text = st.session_state.output_text
    if output_text:
        st.markdown(
            f'<div class="output-box has-content">{output_text}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="output-box">'
            '<span class="output-placeholder">Translation will appear here…</span>'
            '</div>',
            unsafe_allow_html=True,
        )

    # TTS audio player (appears after translation + speak)
    if st.session_state.tts_audio:
        st.audio(st.session_state.tts_audio, format="audio/mp3", autoplay=False)


st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)


# ── Action buttons ────────────────────────────────────────────────────────────
b1, b2, b3, b4, b5 = st.columns([3, 2, 2, 2, 2], gap="small")

with b1:
    st.markdown('<div class="btn-translate">', unsafe_allow_html=True)
    translate_clicked = st.button(
        "🌐  Translate",
        key="translate_btn",
        use_container_width=True,
        help="Translate the input text",
    )
    st.markdown('</div>', unsafe_allow_html=True)

with b2:
    st.markdown('<div class="btn-copy">', unsafe_allow_html=True)
    copy_clicked = st.button("📋  Copy", key="copy_btn", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with b3:
    st.markdown('<div class="btn-clear">', unsafe_allow_html=True)
    clear_clicked = st.button("✕  Clear", key="clear_btn", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with b4:
    st.markdown('<div class="btn-speak">', unsafe_allow_html=True)
    speak_clicked = st.button("🔊  Speak", key="speak_btn", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with b5:
    st.markdown('<div class="btn-voice">', unsafe_allow_html=True)
    voice_toggle = st.button("🎤  Voice", key="voice_btn", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ── Button logic ──────────────────────────────────────────────────────────────

# TRANSLATE
if translate_clicked:
    text = st.session_state.input_text.strip()
    if not text:
        st.markdown('<div class="notice-error">⚠ Please enter text to translate.</div>', unsafe_allow_html=True)
    else:
        with st.spinner("Translating…"):
            result, error = translate_text(text, st.session_state.src_lang, st.session_state.tgt_lang)
        if error:
            st.markdown(f'<div class="notice-error">⚠ {error}</div>', unsafe_allow_html=True)
        else:
            st.session_state.output_text = result
            st.session_state.tts_audio   = None
            add_entry(text, result, st.session_state.src_lang, st.session_state.tgt_lang)
            st.rerun()

# COPY
if copy_clicked:
    if st.session_state.output_text:
        try:
            import pyperclip
            pyperclip.copy(st.session_state.output_text)
        except Exception:
            pass
        st.markdown('<div class="notice-success">✓ Translation copied to clipboard.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="notice-error">Nothing to copy — translate something first.</div>', unsafe_allow_html=True)

# CLEAR
if clear_clicked:
    st.session_state.input_text  = ""
    st.session_state.output_text = ""
    st.session_state.tts_audio   = None
    st.session_state.error_msg   = ""
    st.rerun()

# SPEAK
if speak_clicked:
    text_to_speak = st.session_state.output_text.strip()
    if not text_to_speak:
        st.markdown('<div class="notice-error">Nothing to speak — translate something first.</div>', unsafe_allow_html=True)
    else:
        with st.spinner("Generating audio…"):
            audio_bytes, err = text_to_speech_bytes(text_to_speak, st.session_state.tgt_lang)
        if err:
            st.markdown(f'<div class="notice-error">⚠ {err}</div>', unsafe_allow_html=True)
        else:
            st.session_state.tts_audio = audio_bytes
            st.rerun()

# VOICE TOGGLE
if voice_toggle:
    st.session_state.show_voice = not st.session_state.show_voice
    st.rerun()


# ── How-to tip ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="gradient-divider"></div>
<div style="display:flex; gap:2rem; justify-content:center; flex-wrap:wrap;
            padding:0.5rem 0; color:#334155; font-size:0.78rem;">
    <span>① Select source &amp; target languages</span>
    <span>②  Type or paste text  (or use 🎤 Voice)</span>
    <span>③  Click  <b style="color:#818cf8">Translate</b></span>
    <span>④  Copy or 🔊 listen</span>
</div>
""", unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="vaani-footer">
    <div class="vaani-footer-brand">✦ VAANI AI</div>
    <div class="vaani-footer-sub">
        AI-Powered Language Translator &nbsp;·&nbsp; 110+ Languages &nbsp;·&nbsp;
        Built with Streamlit &amp; deep-translator
    </div>
    <div style="color:#1e293b; font-size:0.68rem; margin-top:0.5rem;">
        © 2025 VAANI AI. Translations powered by Google Translate.
    </div>
</div>
""", unsafe_allow_html=True)
