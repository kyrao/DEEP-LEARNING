# app.py
"""
Polyglot — Aurora Gradient UI — Improved layout & alignment
Run: streamlit run app.py
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
# Helper: flag img
# -------------------------
def flag_img(country_code: str, width: int = 38, height: int = 26) -> str:
    return f"<img src='https://flagcdn.com/w{width}/{country_code.lower()}.png' "\
           f"style='width:{width}px;height:{height}px;border-radius:6px;border:1px solid rgba(255,255,255,0.6);margin-right:10px'/>"

# -------------------------
# Advanced CSS (Aurora + improved layout)
# -------------------------
st.markdown(
    """
    <style>
    /* --- base --- */
    html, body, [class*="css"] {
        font-family: "Inter", sans-serif !important;
        color: #0f1724 !important;
    }
    /* Animated aurora background (subtle) */
    .aurora-bg {
        position: fixed;
        inset: 0;
        z-index: -1;
        background: linear-gradient(135deg, #EEF1FF 0%, #E8F4FF 30%, #F6E9FF 60%, #FFF7FE 100%);
        background-size: 400% 400%;
        animation: aurora 18s ease infinite;
        filter: saturate(1.03) contrast(1.01);
    }
    @keyframes aurora {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* App container spacing */
    section[data-testid="stAppViewContainer"] { padding-top: 22px; padding-bottom: 40px; }

    /* Sidebar styling (kept translucent) */
    [data-testid="stSidebar"] {
        background: rgba(255,255,255,0.72) !important;
        border-right: 1px solid rgba(255,255,255,0.6);
        backdrop-filter: blur(6px);
    }

    /* Header card */
    .header-card {
        display:flex;
        align-items:center;
        justify-content:space-between;
        padding:18px 22px;
        border-radius:14px;
        background: linear-gradient(180deg, rgba(255,255,255,0.80), rgba(255,255,255,0.70));
        box-shadow: 0 8px 28px rgba(45,57,98,0.08);
        border: 1px solid rgba(255,255,255,0.6);
        margin-bottom:18px;
    }
    .app-title {
        font-size:28px;
        font-weight:800;
        background: linear-gradient(90deg,#7B2FF7,#4C8DFF,#6A5BFF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing:-0.3px;
        margin:0;
    }
    .app-sub {
        font-size:13px;
        color:#5B5F72;
        margin:2px 0 0 0;
    }

    /* Language pill cards */
    .lang-card {
        display:flex;
        gap:12px;
        align-items:center;
        padding:8px 12px;
        border-radius:12px;
        background: rgba(255,255,255,0.85);
        border: 1px solid rgba(255,255,255,0.6);
        box-shadow: 0 6px 18px rgba(44,58,110,0.06);
    }
    .lang-label {
        font-size:13px;
        color:#6B6F80;
        margin-bottom:2px;
    }
    .lang-name {
        font-size:15px;
        font-weight:700;
        margin:0;
    }

    /* main glass card */
    .glass {
        background: rgba(255,255,255,0.75);
        border-radius: 16px;
        padding: 20px;
        border: 1px solid rgba(255,255,255,0.6);
        box-shadow: 0 10px 40px rgba(31,38,135,0.10);
    }

    /* Columns layout tweaks for different widths */
    .left-col, .right-col { padding:8px; }

    /* Input area */
    textarea { 
        border-radius:12px !important;
        border: 1px solid rgba(200,200,210,0.6) !important;
        padding:14px !important;
        font-size:15px !important;
        resize: vertical;
        min-height:220px;
        background: rgba(255,255,255,0.9) !important;
    }

    /* Result panel */
    .result {
        border-radius:12px;
        padding:16px;
        min-height:220px;
        background: linear-gradient(180deg, rgba(255,255,255,0.92), rgba(250,250,255,0.92));
        border: 1px solid rgba(220,220,235,0.7);
        box-shadow: 0 6px 20px rgba(18,24,40,0.04);
        white-space: pre-wrap;
        font-size:16px;
        color:#0f1724;
    }

    /* Buttons */
    .stButton>button {
        border-radius:12px;
        padding:10px 16px;
        font-weight:700;
        color:white;
        background: linear-gradient(135deg,#A066FF,#4C8DFF);
        box-shadow: 0 8px 28px rgba(76,141,255,0.28);
        border: none;
    }
    .stButton>button:hover { transform: translateY(-2px); }

    /* download & tts small buttons */
    .mini-btn .stButton>button {
        border-radius:10px;
        padding:8px 12px;
        font-weight:600;
        background: #FFFFFF;
        color:#26303f;
        border:1px solid rgba(200,200,210,0.6);
        box-shadow: 0 4px 12px rgba(7,10,25,0.03);
    }

    /* confidence progress visual */
    .conf-wrap { display:flex; gap:12px; align-items:center; margin-top:12px; }
    .conf-label { font-size:13px; color:#5D5D71; }

    /* Footer */
    .footer { text-align:center; color:#5B5F72; margin-top:18px; font-size:13px; }

    /* responsive tweaks */
    @media (max-width: 880px) {
        .header-card { flex-direction: column; gap:12px; align-items:flex-start; }
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# background div (aurora)
components.html("<div class='aurora-bg'></div>", height=1)

# -------------------------
# Header (with language cards)
# -------------------------
st.markdown(
    """
    <div class="header-card">
      <div>
        <div class="app-title">🌐 Polyglot</div>
        <div class="app-sub">Aurora theme — premium AI translator</div>
      </div>
      <div style="display:flex;gap:12px;align-items:center;">
        <!-- Left language placeholder - will be replaced by Streamlit widgets below -->
        <div class="lang-card" id="left-lang">
          <!-- flag + label injected in streamlit columns -->
          <div style="display:flex;flex-direction:column;">
            <div class="lang-label">Source</div>
            <div style="display:flex;align-items:center;">
              <!-- flag and name appear from streamlit -->
            </div>
          </div>
        </div>

        <div style="width:8px"></div>

        <div class="lang-card" id="right-lang">
          <div style="display:flex;flex-direction:column;">
            <div class="lang-label">Target</div>
            <div style="display:flex;align-items:center;">
            </div>
          </div>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -------------------------
# Controls: put actual selectboxes in top columns so alignment is perfect
# -------------------------
col1, col2, col3 = st.columns([2.2, 2.2, 1.6], gap="large")

with col1:
    # Source language selectbox (keeps Auto Detect)
    src_lang = st.selectbox("Source language", ["Auto Detect"] + list(COUNTRY_CODE.keys()), index=1, key="src_select")
with col2:
    tgt_lang = st.selectbox("Target language", list(COUNTRY_CODE.keys()), index=0, key="tgt_select")
with col3:
    # swap button
    if st.button("↔️ Swap"):
        # swap values in the session state
        s = st.session_state.get("src_select", "Auto Detect")
        t = st.session_state.get("tgt_select", list(COUNTRY_CODE.keys())[0])
        # swap
        try:
            # find keys and set
            st.session_state["src_select"], st.session_state["tgt_select"] = t, s
            src_lang = st.session_state["src_select"]
            tgt_lang = st.session_state["tgt_select"]
            st.success("Languages swapped")
        except Exception:
            pass

# Inject flags + labels into header language cards by printing markup right after selects:
left_flag = COUNTRY_CODE.get(src_lang, "gb")
right_flag = COUNTRY_CODE.get(tgt_lang, "gb")
left_markup = f"<div style='display:flex;align-items:center;gap:10px;'><img src='https://flagcdn.com/w40/{left_flag}.png' style='width:38px;height:26px;border-radius:6px;border:1px solid rgba(255,255,255,0.6);'/>" \
              f"<div style='display:flex;flex-direction:column;'><span style='font-size:13px;color:#6B6F80;'>Source</span><strong style='font-size:15px'>{src_lang}</strong></div></div>"
right_markup = f"<div style='display:flex;align-items:center;gap:10px;'><img src='https://flagcdn.com/w40/{right_flag}.png' style='width:38px;height:26px;border-radius:6px;border:1px solid rgba(255,255,255,0.6);'/>" \
               f"<div style='display:flex;flex-direction:column;'><span style='font-size:13px;color:#6B6F80;'>Target</span><strong style='font-size:15px'>{tgt_lang}</strong></div></div>"

# Small hack: display the header language card info aligned to the right using markdown
right_col_for_header = st.container()
right_col_for_header.markdown(
    f"""
    <div style="display:flex;gap:12px;justify-content:flex-end;margin-top:-48px;">
      <div class="lang-card">{left_markup}</div>
      <div class="lang-card">{right_markup}</div>
    </div>
    """, unsafe_allow_html=True
)

# -------------------------
# Sidebar controls (optional) - keep your extras there
# -------------------------
with st.sidebar:
    st.title("Settings")
    temperature = st.slider("Translation Temperature", 0.0, 1.0, 0.3, 0.05)
    show_conf = st.checkbox("Show Confidence Score", value=True)
    enable_tts = st.checkbox("Enable Text-to-Speech", value=False)
    st.markdown("---")
    st.markdown("Model fallback: Helsinki → facebook/m2m100_418M")

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
# Main content card (two column layout)
# -------------------------
st.markdown('<div class="glass">', unsafe_allow_html=True)
left, right = st.columns([1.6, 1], gap="large")

with left:
    st.markdown("### Input")
    text = st.text_area("Enter text to translate:", height=260, key="src_text")
    # grouped controls
    with st.container():
        col_a, col_b = st.columns([1, 1], gap="small")
        with col_a:
            translate_btn = st.button("🚀 Translate")
        with col_b:
            st.download_button("⬇️ Download (input)", data=text if text else "", file_name="input.txt", key="down_in",
                               mime="text/plain")

with right:
    st.markdown("### Output")
    # placeholder for result
    result_box = st.empty()
    # small action buttons beneath
    colx, coly = st.columns([1, 1], gap="small")
    with colx:
        st.button("Copy (not implemented)", disabled=True)
    with coly:
        # placeholder for tts download if enabled later
        pass

# -------------------------
# Translation logic and output rendering
# -------------------------
if translate_btn:
    if not text or not text.strip():
        st.warning("Please enter some text to translate.")
    else:
        src_iso = "auto" if src_lang == "Auto Detect" else LANG_ISO.get(src_lang, "en")
        tgt_iso = LANG_ISO.get(tgt_lang, "en")
        with st.spinner("Loading translator..."):
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

        # render in right column result box
        with right:
            st.markdown(f"<div class='result'>{result}</div>", unsafe_allow_html=True)
            if show_conf:
                conf = round(max(0.55, 1 - temperature * 0.45), 3)
                st.progress(conf)
                st.caption(f"Confidence: {conf*100:.1f}%")

            st.download_button("⬇️ Download Translation", data=result, file_name="translation.txt", mime="text/plain")

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
<div class="footer">
  <strong>Polyglot</strong> — Aurora theme • Premium UI
</div>
""", unsafe_allow_html=True)
