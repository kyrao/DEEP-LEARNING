import streamlit as st
from transformers import pipeline
from gtts import gTTS
import io

# -------------------------
# Page config
# -------------------------
st.set_page_config(page_title="Polyglot — AI Translator", page_icon="🌐", layout="wide")

# -------------------------
# Custom Styles
# -------------------------
st.markdown("""
<style>
html, body, [class*="css"], .block-container {
    background-color: #f7f9fa !important;
    color: #222831 !important;
    font-family: "Segoe UI", Arial, sans-serif !important;
}
.stButton>button, .stDownloadButton>button {
    background: #183153;
    color: #f7f9fa !important;
    border-radius: 7px;
    border: none;
    font-weight: 600;
    padding: 0.65em 1.1em;
    transition: background 0.13s;
    margin-bottom: 2px;
}
.stButton>button:hover, .stDownloadButton>button:hover {
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
    text-align: left;
    margin-bottom: 4px;
}
.subtitle {
    text-align: left;
    color: #38618c;
    margin-top: 0;
    margin-bottom: 10px;
}
.result {
    font-size: 16px;
    color: #222831;
    background: #eef1f5;
    border-radius: 8px;
    padding: 16px 16px;
    margin-top: 8px;
    border: 1.5px solid #dae1e7;
    box-shadow: 0 2px 8px rgba(24,49,83,0.08);
}
.copy-btn {
    float: right;
    cursor: pointer;
    padding: 2px 8px;
    font-size: 15px;
    border-radius: 4px;
    background: #dae1e7;
    color: #222831;
    margin-left: 8px;
}
.copy-btn:hover {
    background: #b6c5d9;
}
hr { border: none; border-top: 1px solid #dae1e7; margin: 1.5em 0; }
.footer {
    text-align: center;
    font-size: 13px;
    color: #38618c;
    margin-top: 20px;
}
.language-tag {
    font-size: 14px;
    background: #e3e6ea;
    color: #183153;
    border-radius: 5px;
    padding: 5px 10px;
    margin-left: 6px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# Language maps
# -------------------------
COUNTRY_CODE = {
    "English": "gb", "Hindi": "in", "French": "fr", "Spanish": "es", "German": "de",
    "Italian": "it", "Chinese": "cn", "Japanese": "jp", "Korean": "kr",
}
LANG_ISO = {
    "English": "en", "Hindi": "hi", "French": "fr", "Spanish": "es", "German": "de",
    "Italian": "it", "Chinese": "zh", "Japanese": "ja", "Korean": "ko",
}

def flag_img(code):
    return f"<img src='https://flagcdn.com/w40/{code.lower()}.png' style='width:28px;height:19px;border-radius:3px;margin-right:6px;' alt='flag'/>"

# -------------------------
# Translator loader (cached)
# -------------------------
@st.cache_resource
def load_translator(src_iso, tgt_iso):
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
# Branding, Onboarding, Layout
# -------------------------
col1, col2 = st.columns([1, 6])
with col1:
    st.image("https://cdn-icons-png.flaticon.com/512/2819/2819283.png", width=48)
with col2:
    st.markdown("<div class='title'>Polyglot — AI Language Translator</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Modern design • Navy accent • Accessible & efficient</div>", unsafe_allow_html=True)
st.info("Enter text, select your languages, and get instant translations. Use advanced settings for confidence and speech output.")

# -------------------------
# Layout: Language selection, Input, Output
# -------------------------
lang_col, input_col, output_col = st.columns([2, 3, 3])

with lang_col:
    src_lang = st.selectbox("Source Language", ["Auto Detect"] + list(COUNTRY_CODE.keys()), index=1)
    tgt_lang = st.selectbox("Target Language", list(COUNTRY_CODE.keys()), index=0)
    if st.button("↔️ Swap Languages", help="Swap source and target languages"):
        src_lang, tgt_lang = tgt_lang, src_lang
        st.success("Languages swapped!")

with input_col:
    text = st.text_area("Enter text to translate:", height=145)
    translate_btn = st.button("Translate 🌐", use_container_width=True)

# Advanced settings
with st.expander("Advanced Settings"):
    temperature = st.slider("Translation Temperature", 0.0, 1.0, 0.3, 0.05)
    show_conf = st.checkbox("Show Confidence Score", value=True)
    enable_tts = st.checkbox("Enable Text-to-Speech", value=False)

# Result and Output
with output_col:
    if translate_btn:
        if not text.strip():
            st.warning("Please enter some text.")
        else:
            src_iso = "auto" if src_lang == "Auto Detect" else LANG_ISO.get(src_lang, "en")
            tgt_iso = LANG_ISO.get(tgt_lang, "en")
            st.markdown(
                f"**From:** {flag_img(COUNTRY_CODE.get(src_lang, 'gb'))}<span class='language-tag'>{src_lang}</span> &nbsp;"
                f"**To:** {flag_img(COUNTRY_CODE.get(tgt_lang, 'gb'))}<span class='language-tag'>{tgt_lang}</span>",
                unsafe_allow_html=True)
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
            # Highlight result
            st.markdown(
                f"<div class='result'>{result}"
                f"<button class='copy-btn' onclick=\"navigator.clipboard.writeText('{result.replace('\'','\\\'').replace('\"','\\\"')}');\">📋 Copy</button></div>",
                unsafe_allow_html=True)
            # Confidence
            if show_conf:
                conf = round(max(0.6, 1 - temperature * 0.4), 3)
                st.progress(conf)
                st.caption(f"Confidence: {conf*100:.1f}%")
            # Download
            st.download_button("Download Translation", result, "translation.txt")
            # TTS (Speech)
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
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
<div class='footer'>
    Polyglot Translator — Streamlit Demo Project<br>
    Crafted by Kartikay Yadav and Jheelam Hossain (2025)
</div>
""", unsafe_allow_html=True)
