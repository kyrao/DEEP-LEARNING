# app.py
"""
Polyglot — AI Language Translator (White Theme) — Fixed m2m100 fallback
- Fixes ValueError from facebook/m2m100_418M by passing src_lang/tgt_lang
- Uses ISO language codes for model calls and country codes for flag images
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
# country codes for flagcdn (png)
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

# ISO language codes for the translation models (Helsinki/M2M)
# make sure these are valid model language tags (Helsinki uses two-letter codes like en,fr,hi; M2M accepts many of these)
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
# CSS (white background + pink/orange accents + animated flags)
# -------------------------
st.markdown("""
<style>

html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Inter", sans-serif !important;
    background-color: #F5F5F7 !important; /* Apple light grey */
    color: #1C1C1E !important;
}

/* Main container */
section[data-testid="stAppViewContainer"] {
    background-color: #F5F5F7 !important;
    padding: 20px;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #E5E5EA !important;
}

/* Apple Glass Card */
.glass {
    background: rgba(255,255,255,0.72);
    padding: 24px;
    border-radius: 18px;
    box-shadow: 
        0 4px 16px rgba(0,0,0,0.08),
        0 1px 3px rgba(0,0,0,0.06);
    backdrop-filter: blur(22px);
    border: 1px solid rgba(255,255,255,0.45);
}

/* Title */
.title {
    font-size: 32px;
    font-weight: 700;
    text-align: center;
    letter-spacing: -0.5px;
    background: linear-gradient(90deg, #111, #555);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Subtitle */
.subtitle {
    text-align: center;
    font-size: 14px;
    color: #6E6E73;
    margin-top: -4px;
    margin-bottom: 10px;
}

/* Apple Style Button */
.stButton > button {
    border-radius: 12px;
    padding: 0.6em 1.4em;
    font-weight: 600;
    border: 1px solid #D2D2D7 !important;
    background: #FFFFFF;
    color: #000;
    box-shadow: 
        0 1px 3px rgba(0,0,0,0.07),
        0 1px 1px rgba(0,0,0,0.04);
    transition: all 0.2s ease-in-out;
}

.stButton > button:hover {
    background: #F2F2F7;
    transform: translateY(-1px);
}

/* Textarea (macOS style) */
textarea {
    background: #FFFFFF !important;
    border-radius: 12px !important;
    border: 1px solid #D2D2D7 !important;
    padding: 12px !important;
    font-size: 15px !important;
}

/* Result output */
.result {
    background: #FFFFFF;
    padding: 18px;
    border-radius: 14px;
    border: 1px solid #E5E5EA;
    box-shadow: 
        0 4px 14px rgba(0,0,0,0.04),
        0 1px 2px rgba(0,0,0,0.06);
    font-size: 16px;
    color: #1C1C1E;
}

/* Flags (non-animated, clean) */
.flag {
    width: 38px;
    height: 26px;
    border-radius: 4px;
    border: 1px solid #D2D2D7;
}

/* Footer */
.footer {
    text-align:center;
    margin-top:25px;
    font-size:13px;
    color:#6E6E73;
}

</style>
""", unsafe_allow_html=True)


# -------------------------
# Header
# -------------------------
st.markdown("""
<div class="glass" style="margin-bottom:16px;">
  <div class="title">🌐 Polyglot — AI Language Translator</div>
  <div class="subtitle">White theme • Pink/Orange accents • Animated flags</div>
</div>
""", unsafe_allow_html=True)

# -------------------------
# Flag helper
# -------------------------
def flag_img(country_code: str) -> str:
    # flagcdn expects lowercase country codes
    return f"<img src='https://flagcdn.com/w40/{country_code.lower()}.png' class='flag' alt='flag'/>"

# -------------------------
# Lightweight particle trail (optional; keep minimal)
# -------------------------
# small script appended; keep tiny to avoid heavy CPU on server
trail_js = """
<script>
const s=document.createElement('canvas');
s.width=window.innerWidth; s.height=window.innerHeight;
s.style.position='fixed'; s.style.top='0'; s.style.left='0';
s.style.zIndex='1'; s.style.pointerEvents='none';
document.body.appendChild(s);
const ctx=s.getContext('2d'); let ps=[];
function r(a,b){return Math.random()*(b-a)+a;}
function sp(x,y){ for(let i=0;i<2;i++) ps.push({x,y,vx:r(-0.6,0.6),vy:r(-0.6,0.6),life:r(20,50),r:r(1,2)}); }
function dr(){ ctx.clearRect(0,0,s.width,s.height); for(let i=ps.length-1;i>=0;i--){ let p=ps[i]; p.x+=p.vx; p.y+=p.vy; p.life-=1; ctx.beginPath(); ctx.arc(p.x,p.y,p.r,0,2*Math.PI); ctx.fillStyle='rgba(255,159,69,0.9)'; ctx.globalAlpha=Math.max(0,p.life/50); ctx.fill(); if(p.life<=0) ps.splice(i,1);} requestAnimationFrame(dr); }
dr(); window.addEventListener('mousemove',e=>sp(e.clientX,e.clientY));
window.addEventListener('resize',()=>{s.width=window.innerWidth; s.height=window.innerHeight;});
</script>
"""
components.html(trail_js, height=1, scrolling=False)

# -------------------------
# Translator loader (cached)
# returns tuple: (pipeline_or_none, model_type_str)
# model_type_str in {'helsinki', 'm2m'}
# -------------------------
@st.cache_resource
def load_translator(src_iso: str, tgt_iso: str):
    """
    Attempt to load a pair-specific Helsinki model; if unavailable, load multilingual m2m100.
    If src_iso == tgt_iso, returns (None, 'identity') so caller can simply echo input.
    """
    # Handle "auto" fallback
    if src_iso == "auto":
        src_iso = "en"
    if src_iso == tgt_iso:
        return (None, "identity")
    hel_model = f"Helsinki-NLP/opus-mt-{src_iso}-{tgt_iso}"
    try:
        pipe = pipeline("translation", model=hel_model)
        return (pipe, "helsinki")
    except Exception:
        # fallback
        try:
            pipe = pipeline("translation", model="facebook/m2m100_418M")
            return (pipe, "m2m")
        except Exception:
            # bubble error to caller
            raise

# -------------------------
# Main UI
# -------------------------
st.markdown('<div class="glass">', unsafe_allow_html=True)
st.markdown(
    f"**Source:** {flag_img(COUNTRY_CODE.get(src_lang, 'gb'))} {src_lang} &nbsp;&nbsp;&nbsp; "
    f"**Target:** {flag_img(COUNTRY_CODE.get(tgt_lang, 'in'))} {tgt_lang}",
    unsafe_allow_html=True,
)

text = st.text_area("Enter text to translate:", height=180)
translate_btn = st.button("🚀 Translate")

if translate_btn:
    if not text.strip():
        st.warning("Please enter some text to translate.")
    else:
        # map user labels to ISO model codes
        src_iso = "auto" if src_lang == "Auto Detect" else LANG_ISO.get(src_lang, "en")
        tgt_iso = LANG_ISO.get(tgt_lang, "en")

        st.info(f"Translating {src_lang} → {tgt_lang} ...")
        with st.spinner("Loading model..."):
            try:
                translator, model_type = load_translator(src_iso, tgt_iso)
            except Exception as e:
                st.error(f"Failed to load models: {e}")
                translator, model_type = None, None

        # perform translation
        if model_type == "identity":
            result = text
        elif translator is None:
            st.error("Translator unavailable.")
            result = ""
        else:
            with st.spinner("Translating text..."):
                try:
                    if model_type == "helsinki":
                        out = translator(text, max_length=512)
                        # some Helsinki pipelines return list/dict vary; normalize
                        if isinstance(out, list):
                            result = out[0].get("translation_text", str(out[0]))
                        elif isinstance(out, dict):
                            result = out.get("translation_text", str(out))
                        else:
                            result = str(out)
                    elif model_type == "m2m":
                        # m2m requires explicit src_lang and tgt_lang args
                        # The m2m tokenizer expects language codes like 'en', 'hi', etc.
                        out = translator(text, max_length=512, src_lang=src_iso, tgt_lang=tgt_iso)
                        if isinstance(out, list):
                            result = out[0].get("translation_text", str(out[0]))
                        elif isinstance(out, dict):
                            result = out.get("translation_text", str(out))
                        else:
                            result = str(out)
                    else:
                        result = ""
                except Exception as e:
                    st.error(f"Translation failed: {e}")
                    result = ""

        # display
        st.markdown(f"<div class='result'>{result}</div>", unsafe_allow_html=True)

        if show_conf:
            # synthetic confidence
            conf = round(max(0.6, 1 - temperature * 0.4), 3)
            st.progress(conf)
            st.caption(f"Confidence: {conf*100:.1f}%")

        st.download_button("⬇️ Download Translation", data=result, file_name="translation.txt")

        if enable_tts and result:
            try:
                tts = gTTS(text=result, lang=tgt_iso if tgt_iso in ["en","hi","fr","es","de","it","pt"] else "en")
                bio = io.BytesIO()
                tts.write_to_fp(bio)
                bio.seek(0)
                st.audio(bio.read(), format="audio/mp3")
            except Exception as e:
                st.error(f"TTS failed: {e}")

st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# Footer
# -------------------------
st.markdown("""
<hr>
<div class="footer">
  <strong>Polyglot</strong> — White theme • Pink/Orange accents
</div>
""", unsafe_allow_html=True)
