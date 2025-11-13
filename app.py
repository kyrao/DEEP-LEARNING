# app.py
"""
Polyglot — AI Language Translator (Teal Premium Theme)
"""

import streamlit as st
from transformers import pipeline
from gtts import gTTS
import io
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
# TEAL PREMIUM THEME CSS
# -------------------------
st.markdown("""
<style>

html, body, [class*="css"] {
    background: linear-gradient(145deg, #e8f9fa 0%, #dfe9ee 40%, #eef2f7 100%) !important;
    color: #1c2b33 !important;
    font-family: 'Inter', sans-serif;
    background-attachment: fixed;
}

/* Glass card */
.glass {
    background: rgba(255, 255, 255, 0.55);
    border-radius: 18px;
    padding: 22px;
    border: 1px solid rgba(190, 210, 220, 0.6);
    box-shadow:
        0px 8px 20px rgba(12, 60, 70, 0.08),
        0px 4px 10px rgba(0, 0, 0, 0.04);
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
    color: white !important;
    background: linear-gradient(135deg, #008c9e, #4ac2d0);
    box-shadow: 0px 6px 16px rgba(0, 140, 158, 0.25);
    transition: 0.22s ease-in-out;
}

.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow:
        0px 10px 22px rgba(0, 140, 158, 0.35),
        0px 6px 14px rgba(80, 190, 204, 0.12);
}

/* Textarea */
textarea {
    border-radius: 14px !important;
    background: rgba(255,255,255,0.75) !important;
    border: 1px solid rgba(170,190,200,0.6) !important;
    padding: 14px !important;
    color: #1c2b33 !important;
    box-shadow: inset 0px 0px 8px rgba(0,0,0,0.04);
}

/* Result */
.result {
    background: rgba(255,255,255,0.72);
    border-radius: 16px;
    border: 1px solid rgba(200,220,225,0.6);
    padding: 18px;
    font-size: 16px;
    box-shadow: 0px 6px 20px rgba(17,50,60,0.08);
}

/* Flag styling */
.flag {
    width: 40px;
    height: 28px;
    border-radius: 6px;
    border: 1px solid rgba(160,190,200,0.6);
    box-shadow: 0px 4px 10px rgba(0,100,120,0.12);
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
    font-size:14px;
    color:#006a7a;
    margin-top:20px;
}

</style>
""", unsafe_allow_html=True)


# -------------------------
# HEADER (Perfect + Working)
# -------------------------
src_flag = COUNTRY_CODE.get(src_lang, "gb")
tgt_flag = COUNTRY_CODE.get(tgt_lang, "gb")

header_html = f"""
<div class="glass" style="margin-bottom:20px; padding:28px;">

    <div class="title">🌐 Polyglot — AI Language Translator</div>

    <div style="margin-top:20px; display:flex; justify-content:center; gap:80px; align-items:center; font-size:18px;">

        <div style="display:flex; align-items:center; gap:10px;">
            <strong>Source:</strong>
            <img src="https://flagcdn.com/w40/{src_flag}.png" class="flag">
            <span>{src_lang}</span>
        </div>

        <div style="display:flex; align-items:center; gap:10px;">
            <strong>Target:</strong>
            <img src="https://flagcdn.com/w40/{tgt_flag}.png" class="flag">
            <span>{tgt_lang}</span>
        </div>

    </div>

</div>
"""

st.markdown(header_html, unsafe_allow_html=True)

# -------------------------
# Particle animation
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
function dr(){ ctx.clearRect(0,0,s.width,s.height); for(let i=ps.length-1;i>=0;i--){ let p=ps[i]; p.x+=p.vx; p.y+=p.vy; p.life-=1; ctx.beginPath(); ctx.arc(p.x,p.y,p.r,0,2*Math.PI); ctx.fillStyle='rgba(0,167,187,0.7)'; ctx.globalAlpha=Math.max(0,p.life/50); ctx.fill(); if(p.life<=0) ps.splice(i,1);} requestAnimationFrame(dr); }
dr(); window.addEventListener('mousemove',e=>sp(e.clientX,e.clientY));
window.addEventListener('resize',()=>{s.width=window.innerWidth; s.height=window.innerHeight;});
</script>
"""
components.html(trail_js, height=1, scrolling=False)


# -------------------------
# MAIN GLASS CARD
# -------------------------
st.markdown('<div class="glass" style="padding:20px;">', unsafe_allow_html=True)

text = st.text_area("Enter text to translate:", height=180)
translate_btn = st.button("🚀 Translate")

# -------------------------
# TRANSLATOR LOGIC (unchanged)
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
    except:
        try:
            pipe = pipeline("translation", model="facebook/m2m100_418M")
            return (pipe, "m2m")
        except:
            raise

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
            except:
                st.error("Model loading failed.")
                translator, model_type = None, None

        if model_type == "identity":
            result = text
        elif translator is None:
            result = ""
        else:
            out = translator(
                text, max_length=512,
                **({"src_lang": src_iso, "tgt_lang": tgt_iso} if model_type=="m2m" else {})
            )
            result = out[0].get("translation_text", str(out))

        st.markdown(f"<div class='result'>{result}</div>", unsafe_allow_html=True)

        if show_conf:
            conf = round(max(0.55, 1 - temperature * 0.4), 3)
            st.progress(conf)
            st.caption(f"Confidence: {conf*100:.1f}%")

        st.download_button("⬇️ Download Translation", result, "translation.txt")

        if enable_tts:
            try:
                tts = gTTS(text=result, lang=tgt_iso)
                bio = io.BytesIO()
                tts.write_to_fp(bio)
                bio.seek(0)
                st.audio(bio, format="audio/mp3")
            except:
                st.error("TTS failed.")

st.markdown('</div>', unsafe_allow_html=True)


# -------------------------
# FOOTER
# -------------------------
st.markdown("""
<div class="footer">
  Polyglot — Teal Premium UI
</div>
""", unsafe_allow_html=True)
