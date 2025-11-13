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
    background: linear-gradient(145deg, #e8f9fa 0%, #dfe9ee 35%, #eef2f7 100%) !important;
    background-attachment: fixed;
    color: #1c2b33 !important;
    font-family: 'Inter', sans-serif;
}

/* Main Glass Card */
.glass {
    background: rgba(255, 255, 255, 0.58);
    border-radius: 16px;
    padding: 22px;
    border: 1px solid rgba(200, 220, 230, 0.6);
    backdrop-filter: blur(14px);
    box-shadow:
        0 8px 25px rgba(12, 60, 70, 0.08),
        0 4px 10px rgba(0, 0, 0, 0.04);
}

/* Title Gradient - Teal + Navy */
.title {
    font-size: 30px;
    font-weight: 800;
    text-align: center;
    background: linear-gradient(90deg, #006a7a, #0099a8, #005f7a);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.3px;
}

/* Subtitle */
.subtitle {
    text-align:center;
    color:#4e6068;
    font-size:14px;
    margin-top:-6px;
}

/* Stylish teal buttons */
.stButton>button {
    border: none;
    border-radius: 12px;
    font-weight: 700;
    padding: 10px 22px;
    color: white;
    background: linear-gradient(135deg, #008c9e, #4ebac4);
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
    background: rgba(255,255,255,0.75) !important;
    padding: 14px !important;
    color: #1c2b33 !important;
    box-shadow: inset 0px 0px 8px rgba(0,0,0,0.04);
}

/* Output Box */
.result {
    background: rgba(255,255,255,0.75);
    border-radius: 16px;
    padding: 18px;
    border: 1px solid rgba(200,220,225,0.7);
    font-size: 16px;
    color:#1c2b33;
    box-shadow: 
        0 6px 20px rgba(17,50,60,0.08);
    white-space: pre-wrap;
}

/* Flags – clean professional */
.flag {
    width: 38px;
    height: 26px;
    border-radius: 6px;
    border: 1px solid rgba(160,190,200,0.6);
    box-shadow: 0px 3px 8px rgba(0,100,120,0.12);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.52) !important;
    border-right: 1px solid rgba(200,220,230,0.6);
    backdrop-filter: blur(12px);
}

/* Footer */
.footer {
    text-align:center;
    font-size:14px;
    margin-top:20px;
    color:#006a7a;
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
    return f"<img src='https://flagcdn.com/w40/{country_code.lower()}.png' class='flag' alt='flag'/>"

# -------------------------
# Particle trail
# -------------------------
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
            st.error("Translator unavailable.")
            result = ""
        else:
            with st.spinner("Translating text..."):
                try:
                    if model_type == "helsinki":
                        out = translator(text, max_length=512)
                        if isinstance(out, list):
                            result = out[0].get("translation_text", str(out[0]))
                        elif isinstance(out, dict):
                            result = out.get("translation_text", str(out))
                        else:
                            result = str(out)
                    elif model_type == "m2m":
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

        st.markdown(f"<div class='result'>{result}</div>", unsafe_allow_html=True)

        if show_conf:
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
