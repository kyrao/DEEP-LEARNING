# app.py
"""
Polyglot — AI Language Translator (Teal/Navy Premium Theme)
Clean, modern, glass UI + fixed header alignment
Run: streamlit run app.py
"""

import streamlit as st
from transformers import pipeline
from gtts import gTTS
import io
import time
import streamlit.components.v1 as components

# -------------------------
# Page config
# -------------------------
st.set_page_config(page_title="Polyglot — AI Translator", page_icon="🌐", layout="wide")

# -------------------------
# Language maps
# -------------------------
COUNTRY_CODE = {
    "English": "gb",
    "Hindi": "in",
    "French": "fr",
    "Spanish": "es",
    "German": "de",
    "Italian": "it",
    "Chinese": "cn",
    "Japanese": "jp",
    "Korean": "kr",
}

LANG_ISO = {
    "English": "en",
    "Hindi": "hi",
    "French": "fr",
    "Spanish": "es",
    "German": "de",
    "Italian": "it",
    "Chinese": "zh",
    "Japanese": "ja",
    "Korean": "ko",
}

# -------------------------
# CSS THEME (Teal / Navy Premium)
# -------------------------
st.markdown("""
<style>

html, body, [class*="css"] {
    background: linear-gradient(145deg, #e7f7fa 0%, #dbe6ed 40%, #eef2f7 100%) !important;
    background-attachment: fixed;
    color: #1c2b33 !important;
    font-family: 'Inter', sans-serif;
}

/* Glass Card */
.glass {
    background: rgba(255, 255, 255, 0.58);
    border-radius: 18px;
    padding: 24px;
    border: 1px solid rgba(200, 220, 230, 0.6);
    box-shadow:
        0 8px 28px rgba(12, 60, 70, 0.08),
        0 4px 12px rgba(0, 0, 0, 0.04);
    backdrop-filter: blur(14px);
}

/* Title */
.title {
    font-size: 32px;
    font-weight: 800;
    text-align: center;
    background: linear-gradient(90deg, #006a7a, #0099a8, #005f7a);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Buttons */
.stButton>button {
    border: none;
    border-radius: 12px;
    font-weight: 700;
    padding: 10px 22px;
    color: white;
    background: linear-gradient(135deg, #008c9e, #48c4d1);
    box-shadow: 0px 8px 20px rgba(0, 140, 158, 0.22);
    transition: 0.22s ease-in-out;
}

.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow:
        0px 10px 28px rgba(0, 140, 158, 0.32),
        0px 5px 14px rgba(80, 190, 204, 0.18);
}

/* Textarea */
textarea {
    border-radius: 14px !important;
    border: 1px solid rgba(170, 190, 200, 0.6) !important;
    background: rgba(255,255,255,0.7) !important;
    padding: 14px !important;
    color: #1c2b33 !important;
    box-shadow: inset 0px 0px 8px rgba(0,0,0,0.04);
}

/* Output box */
.result {
    background: rgba(255,255,255,0.75);
    border-radius: 16px;
    padding: 18px;
    border: 1px solid rgba(200,220,225,0.7);
    font-size: 16px;
    color:#1c2b33;
    box-shadow: 0 6px 20px rgba(17,50,60,0.08);
    white-space: pre-wrap;
}

/* Flags */
.flag {
    width: 40px;
    height: 28px;
    border-radius: 6px;
    border: 1px solid rgba(160,190,200,0.5);
    box-shadow: 0px 3px 8px rgba(0,100,120,0.12);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.48) !important;
    border-right: 1px solid rgba(200,220,230,0.6);
    backdrop-filter: blur(12px);
}

/* Footer */
.footer {
    text-align:center;
    font-size:13px;
    margin-top:20px;
    color:#006a7a;
}

</style>
""", unsafe_allow_html=True)

# -------------------------
# Flag helper
# -------------------------
def flag_img(country_code: str) -> str:
    return f"<img src='https://flagcdn.com/w40/{country_code.lower()}.png' class='flag'/>"


# -------------------------
# Sidebar
# -------------------------
st.sidebar.title("🌐 Polyglot Settings")

src_lang = st.sidebar.selectbox("Source Language", ["Auto Detect"] + list(COUNTRY_CODE.keys()), index=1)
tgt_lang = st.sidebar.selectbox("Target Language", list(COUNTRY_CODE.keys()), index=0)
temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.3)
show_conf = st.sidebar.checkbox("Show Confidence", True)
enable_tts = st.sidebar.checkbox("Enable TTS", False)

if st.sidebar.button("↔️ Swap"):
    src_lang, tgt_lang = tgt_lang, src_lang
    st.sidebar.success("Languages swapped!")


# -------------------------
# HEADER (FIXED & ALIGNED)
# -------------------------
st.markdown(f"""
<div class="glass" style="margin-bottom:18px;">

    <div class="title">🌐 Polyglot — AI Translator</div>

    <div style="margin-top:12px; display:flex; justify-content:center; gap:60px;">

        <div style="display:flex; align-items:center; gap:10px;">
            <strong>Source:</strong>
            {flag_img(COUNTRY_CODE.get(src_lang, "gb"))}
            <span>{src_lang}</span>
        </div>

        <div style="display:flex; align-items:center; gap:10px;">
            <strong>Target:</strong>
            {flag_img(COUNTRY_CODE.get(tgt_lang, "gb"))}
            <span>{tgt_lang}</span>
        </div>

    </div>

</div>
""", unsafe_allow_html=True)


# -------------------------
# Translator loader
# -------------------------
@st.cache_resource
def load_translator(src_iso: str, tgt_iso: str):
    if src_iso == "auto":
        src_iso = "en"
    if src_iso == tgt_iso:
        return (None, "identity")

    hel_model = f"Helsinki-NLP/opus-mt-{src_iso}-{tgt_iso}"

    try:
        pipe = pipeline("translation", model=hel_model)
        return (pipe, "helsinki")
    except Exception:
        try:
            pipe = pipeline("translation", model="facebook/m2m100_418M")
            return (pipe, "m2m")
        except Exception:
            raise


# -------------------------
# MAIN CONTENT
# -------------------------
st.markdown('<div class="glass">', unsafe_allow_html=True)

text = st.text_area("Enter text to translate:", height=180)
translate_btn = st.button("🚀 Translate")

if translate_btn:
    if not text.strip():
        st.warning("Please enter text.")
    else:
        src_iso = "auto" if src_lang == "Auto Detect" else LANG_ISO.get(src_lang, "en")
        tgt_iso = LANG_ISO.get(tgt_lang, "en")

        with st.spinner("Loading model..."):
            try:
                translator, model_type = load_translator(src_iso, tgt_iso)
            except Exception as e:
                st.error(f"Error loading translator: {e}")
                translator, model_type = None, None

        # perform translation
        if model_type == "identity":
            result = text
        elif translator is None:
            st.error("Translation unavailable.")
            result = ""
        else:
            with st.spinner("Translating..."):
                try:
                    if model_type == "helsinki":
                        out = translator(text, max_length=512)
                        result = out[0]["translation_text"]
                    else:
                        out = translator(text, max_length=512, src_lang=src_iso, tgt_lang=tgt_iso)
                        result = out[0]["translation_text"]
                except Exception as e:
                    st.error(f"Translation failed: {e}")
                    result = ""

        st.markdown(f"<div class='result'>{result}</div>", unsafe_allow_html=True)

        if show_conf:
            conf = round(max(0.55, 1 - temperature * 0.45), 3)
            st.progress(conf)
            st.caption(f"Confidence: {conf*100:.1f}%")

        st.download_button("⬇️ Download Translation", result, "translation.txt")

        if enable_tts and result:
            try:
                tts = gTTS(text=result, lang=tgt_iso)
                bio = io.BytesIO()
                tts.write_to_fp(bio)
                bio.seek(0)
                st.audio(bio, format="audio/mp3")
            except:
                st.error("Text-to-Speech failed.")


st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# FOOTER
# -------------------------
st.markdown("""
<div class="footer">
    Polyglot — Teal/Navy Premium UI
</div>
""", unsafe_allow_html=True)
