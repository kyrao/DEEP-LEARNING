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
# Sidebar settings
# -------------------------
st.sidebar.title("🌐 Polyglot Settings")

src_lang = st.sidebar.selectbox("Source Language", ["Auto Detect"] + list(COUNTRY_CODE.keys()), index=1)
tgt_lang = st.sidebar.selectbox("Target Language", list(COUNTRY_CODE.keys()), index=0)
temperature = st.sidebar.slider("Translation Temperature", 0.0, 1.0, 0.3, 0.05)
show_conf = st.sidebar.checkbox("Show Confidence Score", value=True)
enable_tts = st.sidebar.checkbox("Enable Text-to-Speech", value=False)

if st.sidebar.button("↔️ Swap Languages"):
    src_lang, tgt_lang = tgt_lang, src_lang
    st.sidebar.success("Languages swapped!")

# -------------------------
# Custom Styles (Modern Theme)
# -------------------------
st.markdown("""
<style>
html, body, [class*="css"], .block-container {
    background-color: #f7f9fa !important;
    color: #222831 !important;
    font-family: "Segoe UI", Arial, sans-serif !important;
}
.stButton>button {
    background: #183153;
    color: #f7f9fa !important;
    border-radius: 7px;
    border: none;
    font-weight: 600;
    padding: 0.65em 1.1em;
    transition: background 0.13s;
    margin-bottom: 2px;
}
.stButton>button:hover {
    background: #222831;
    color: #f7f9fa !important;
}
section[data-testid="stSidebar"] {
    background-color: #e3e6ea !important;
    color: #222831 !important;
}
.title {
    font-size: 27px;
    font-weight: 700;
    color: #183153;
    text-align: center;
    margin-bottom: 4px;
}
.subtitle {
    text-align: center;
    color: #38618c;
    margin-top: 0;
    margin-bottom: 10px;
}
.result {
    font-size: 16px;
    color: #222831;
    white-space: pre-wrap;
    background: #eef1f5;
    border-radius: 8px;
    padding: 15px 15px;
    margin-top: 8px;
    border: 1.5px solid #dae1e7;
}
.footer {
    text-align: center;
    font-size: 13px;
    color: #38618c;
    margin-top: 20px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# Header
# -------------------------
st.markdown("""
<div class="title">🌐 Polyglot — AI Language Translator</div>
<div class="subtitle">Modern theme • Navy accent • Accessible & clean UI</div>
""", unsafe_allow_html=True)

# -------------------------
# Flag helper
# -------------------------
def flag_img(country_code: str) -> str:
    return f"<img src='https://flagcdn.com/w40/{country_code.lower()}.png' style='width:30px;height:20px;border-radius:3px;margin-right:6px;' alt='flag'/>"

# -------------------------
# Translator loader (cached)
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
# Main UI
# -------------------------
st.markdown(f"""
**Source:** {flag_img(COUNTRY_CODE.get(src_lang, 'gb'))} {src_lang} &nbsp;&nbsp;&nbsp; 
**Target:** {flag_img(COUNTRY_CODE.get(tgt_lang, 'in'))} {tgt_lang}
""", unsafe_allow_html=True)

text = st.text_area("Enter text to translate:", height=180)
translate_btn = st.button("Translate")

if translate_btn:
    if not text.strip():
        st.warning("Please enter some text.")
    else:
        src_iso = "auto" if src_lang == "Auto Detect" else LANG_ISO.get(src_lang, "en")
        tgt_iso = LANG_ISO.get(tgt_lang, "en")
        st.info(f"Translating {src_lang} → {tgt_lang} ...")
        with st.spinner("Loading model..."):
            try:
                translator, model_type = load_translator(src_iso, tgt_iso)
            except Exception as e:
                st.error(f"Failed to load models: {e}")
                translator, model_type = None, None
        if model_type == "identity":
            result = text
        elif translator is None:
            result = ""
        else:
            try:
                if model_type == "helsinki":
                    out = translator(text, max_length=512)
                    result = out[0]["translation_text"] if isinstance(out, list) else out["translation_text"]
                else:
                    out = translator(text, max_length=512, src_lang=src_iso, tgt_lang=tgt_iso)
                    result = out[0]["translation_text"] if isinstance(out, list) else out["translation_text"]
            except Exception as e:
                st.error(f"Translation failed: {e}")
                result = ""

        st.markdown(f"<div class='result'>{result}</div>", unsafe_allow_html=True)

        if show_conf:
            conf = round(max(0.6, 1 - temperature * 0.4), 3)
            st.progress(conf)
            st.caption(f"Confidence: {conf*100:.1f}%")

        st.download_button("Download Translation", result, "translation.txt")

        if enable_tts and result:
            try:
                tts = gTTS(text=result, lang=tgt_iso if tgt_iso in ["en","hi","fr","es","de","it","pt"] else "en")
                bio = io.BytesIO()
                tts.write_to_fp(bio)
                bio.seek(0)
                st.audio(bio.read(), format="audio/mp3")
            except Exception:
                st.error("TTS failed.")

# -------------------------
# Footer
# -------------------------
st.markdown("""
<hr>
<div class="footer">
  <strong>Polyglot</strong> — Modern theme • Navy accent
</div>
""", unsafe_allow_html=True)
