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
    font-family: "Inter", sans-serif !important;
    background: linear-gradient(135deg, #EEF1FF, #DDEBFF, #F2E9FF);
    background-size: 300% 300%;
    animation: auroraBG 18s ease infinite;
    color: #1A1A1A !important;
}

/* Smooth animated background */
@keyframes auroraBG {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* Main app container */
section[data-testid="stAppViewContainer"] {
    padding: 20px;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.55) !important;
    backdrop-filter: blur(14px);
    border-right: 1px solid rgba(255,255,255,0.35);
}

/* Glass card with aurora glow */
.glass {
    background: rgba(255,255,255,0.65);
    border-radius: 18px;
    padding: 26px;
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.55);
    box-shadow: 
        0 8px 32px rgba(31,38,135,0.20),
        0 2px 8px rgba(0,0,0,0.08);
}

/* Title with aurora gradient text */
.title {
    font-size: 34px;
    font-weight: 800;
    text-align: center;
    background: linear-gradient(90deg, #7B2FF7, #4C8DFF, #6A5BFF);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px;
}

/* Subtitle */
.subtitle {
    text-align: center;
    font-size: 15px;
    color: #5D5D71;
    margin-top: -6px;
}

/* Aurora Gradient Button */
.stButton > button {
    border-radius: 14px;
    padding: 0.7em 1.4em;
    font-weight: 600;
    color: white;
    border: none;
    background: linear-gradient(135deg, #A066FF, #4C8DFF);
    box-shadow: 0 6px 20px rgba(76,141,255,0.35);
    transition: 0.25s ease-in-out;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 28px rgba(76,141,255,0.45);
}

/* Textarea (clean card feel) */
textarea {
    border-radius: 14px !important;
    border: 1px solid rgba(255,255,255,0.55) !important;
    background: rgba(255,255,255,0.75) !important;
    box-shadow: 0 4px 18px rgba(0,0,0,0.06);
    padding: 14px !important;
}

/* Output result container */
.result {
    background: rgba(255,255,255,0.75);
    backdrop-filter: blur(12px);
    border-radius: 14px;
    padding: 18px;
    font-size: 17px;
    border: 1px solid rgba(255,255,255,0.45);
    box-shadow: 0 4px 18px rgba(0,0,0,0.06);
}

/* Flags (keep minimal, clean) */
.flag {
    width: 40px;
    height: 28px;
    border-radius: 6px;
    border: 1px solid rgba(255,255,255,0.55);
    box-shadow: 0 3px 10px rgba(0,0,0,0.1);
}

/* Footer */
.footer {
    text-align:center;
    margin-top:20px;
    font-size:14px;
    color:#5D5D71;
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
