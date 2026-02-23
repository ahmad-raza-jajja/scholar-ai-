"""
ScholarAI Elite v4 — Main Application
Elite Hacker UI | Groq Llama3 + RAG | Complete Features
"""

import os, sys, json, time, random, datetime, hashlib
import streamlit as st
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils.ai_engine import AIEngine
from utils.data_manager import DataManager, extract_text_from_pdf
from utils.rag_engine import RAGEngine

# ── Page Config ─────────────────────────────────────────
st.set_page_config(
    page_title="ScholarAI Elite",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Auth Helpers ─────────────────────────────────────────
DEMO_USERS = {
    "demo": {
        "password": hashlib.sha256("demo123".encode()).hexdigest(),
        "name": "Demo Student",
        "email": "demo@scholarai.com"
    }
}

def hash_pw(pw): return hashlib.sha256(pw.encode()).hexdigest()

def get_users():
    if "users_db" not in st.session_state:
        st.session_state.users_db = DEMO_USERS.copy()
    return st.session_state.users_db

def register_user(username, password, name, email):
    users = get_users()
    if username in users:
        return False, "Username already exists"
    users[username] = {"password": hash_pw(password), "name": name, "email": email}
    st.session_state.users_db = users
    return True, "Account created!"

def login_user(username, password):
    users = get_users()
    if username not in users:
        return False, "Username not found"
    if users[username]["password"] != hash_pw(password):
        return False, "Wrong password"
    return True, users[username]["name"]

# ── CSS — Elite Hacker UI ────────────────────────────────
def apply_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&family=Syne:wght@400;600;700;800&family=Space+Grotesk:wght@300;400;500;600;700&display=swap');

:root {
  --bg0: #010408;
  --bg1: #060d1a;
  --bg2: #091424;
  --bg3: #0d1f38;
  --c0: #00ffe0;
  --c1: #0070ff;
  --c2: #7000ff;
  --c3: #ff003c;
  --c4: #ff8c00;
  --tx1: #e8f4f8;
  --tx2: #6a9ab0;
  --tx3: #3a5a70;
  --glass: rgba(0, 255, 224, 0.04);
  --glass2: rgba(0, 112, 255, 0.06);
  --border: rgba(0, 255, 224, 0.12);
  --border2: rgba(0, 112, 255, 0.18);
  --glow0: rgba(0, 255, 224, 0.2);
  --glow1: rgba(0, 112, 255, 0.2);
  --glow2: rgba(112, 0, 255, 0.15);
  --font-mono: 'JetBrains Mono', monospace;
  --font-head: 'Syne', sans-serif;
  --font-body: 'Space Grotesk', sans-serif;
}

*, html, body { box-sizing: border-box; margin: 0; padding: 0; }
html, body, .stApp { background: var(--bg0) !important; color: var(--tx1); font-family: var(--font-body); }
#MainMenu, footer, header, .stDeployButton { display: none !important; }

/* ── Animated Grid Background ── */
.stApp::before {
  content: '';
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background:
    linear-gradient(rgba(0,255,224,0.025) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,255,224,0.025) 1px, transparent 1px);
  background-size: 50px 50px;
  pointer-events: none; z-index: 0;
  animation: gridShift 20s linear infinite;
}
@keyframes gridShift { 0% { background-position: 0 0; } 100% { background-position: 50px 50px; } }

/* Radial glow orbs */
.stApp::after {
  content: '';
  position: fixed; top: 20%; left: 60%; width: 600px; height: 600px;
  background: radial-gradient(circle, rgba(0,112,255,0.06) 0%, transparent 70%);
  pointer-events: none; z-index: 0;
  animation: orbFloat 8s ease-in-out infinite;
}
@keyframes orbFloat { 0%,100% { transform: translate(0,0); } 50% { transform: translate(-30px, 30px); } }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, var(--bg1) 0%, var(--bg0) 100%) !important;
  border-right: 1px solid var(--border) !important;
  box-shadow: 4px 0 40px rgba(0,255,224,0.05) !important;
}
[data-testid="stSidebar"] * { color: var(--tx1) !important; }
[data-testid="stSidebar"] .stButton > button {
  background: transparent !important;
  color: var(--tx2) !important;
  border: 1px solid transparent !important;
  border-radius: 6px !important;
  font-family: var(--font-body) !important;
  font-size: 0.84rem !important;
  font-weight: 500 !important;
  padding: 9px 14px !important;
  text-align: left !important;
  width: 100% !important;
  transition: all 0.18s ease !important;
  margin: 1px 0 !important;
  letter-spacing: 0.01em !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background: var(--glass) !important;
  border-color: var(--border) !important;
  color: var(--c0) !important;
  padding-left: 18px !important;
  box-shadow: 0 0 16px var(--glow0) !important;
}

/* ── Buttons ── */
.stButton > button {
  background: linear-gradient(135deg, var(--c1), var(--c2)) !important;
  color: #fff !important;
  border: none !important;
  border-radius: 8px !important;
  font-family: var(--font-body) !important;
  font-weight: 600 !important;
  font-size: 0.88rem !important;
  padding: 10px 22px !important;
  transition: all 0.2s ease !important;
  letter-spacing: 0.02em !important;
  position: relative; overflow: hidden;
}
.stButton > button::before {
  content: '';
  position: absolute; top: 0; left: -100%; width: 100%; height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
  transition: left 0.4s ease;
}
.stButton > button:hover::before { left: 100%; }
.stButton > button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 24px var(--glow1) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── Inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input {
  background: var(--bg2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
  color: var(--tx1) !important;
  font-family: var(--font-body) !important;
  font-size: 0.9rem !important;
  transition: all 0.2s !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
  border-color: var(--c0) !important;
  box-shadow: 0 0 0 2px var(--glow0), 0 0 20px var(--glow0) !important;
  outline: none !important;
}
.stSelectbox > div > div {
  background: var(--bg2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
  color: var(--tx1) !important;
}
label, .stTextInput label, .stSelectbox label, .stNumberInput label,
.stTextArea label, .stSlider label {
  color: var(--tx2) !important;
  font-size: 0.8rem !important;
  font-weight: 500 !important;
  letter-spacing: 0.05em !important;
  text-transform: uppercase !important;
  font-family: var(--font-mono) !important;
}

/* ── Progress ── */
.stProgress > div > div > div > div {
  background: linear-gradient(90deg, var(--c0), var(--c1)) !important;
  border-radius: 10px !important;
  box-shadow: 0 0 12px var(--glow0) !important;
}
.stProgress > div > div {
  background: var(--bg3) !important;
  border-radius: 10px !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
  background: var(--bg2) !important;
  border-radius: 10px !important;
  padding: 4px !important;
  border: 1px solid var(--border) !important;
  gap: 2px !important;
}
.stTabs [data-baseweb="tab"] {
  border-radius: 7px !important;
  color: var(--tx2) !important;
  font-family: var(--font-body) !important;
  font-weight: 500 !important;
  font-size: 0.85rem !important;
  transition: all 0.2s !important;
}
.stTabs [aria-selected="true"] {
  background: linear-gradient(135deg, var(--c1), var(--c2)) !important;
  color: #fff !important;
  box-shadow: 0 0 16px var(--glow1) !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
  background: var(--glass) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
  color: var(--tx1) !important;
  font-family: var(--font-body) !important;
}
.streamlit-expanderContent { border: 1px solid var(--border) !important; border-top: none !important; border-radius: 0 0 8px 8px !important; background: var(--bg2) !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--bg0); }
::-webkit-scrollbar-thumb { background: var(--c0)44; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--c0)88; }

/* ── Alerts ── */
.stSuccess > div { background: rgba(0,255,160,0.08) !important; border: 1px solid rgba(0,255,160,0.3) !important; border-radius: 8px !important; color: var(--tx1) !important; }
.stError > div { background: rgba(255,0,60,0.08) !important; border: 1px solid rgba(255,0,60,0.3) !important; border-radius: 8px !important; color: var(--tx1) !important; }
.stWarning > div { background: rgba(255,140,0,0.08) !important; border: 1px solid rgba(255,140,0,0.3) !important; border-radius: 8px !important; color: var(--tx1) !important; }
.stInfo > div { background: rgba(0,112,255,0.08) !important; border: 1px solid rgba(0,112,255,0.3) !important; border-radius: 8px !important; color: var(--tx1) !important; }

/* ── Radio / Checkbox ── */
.stRadio > div > label, .stCheckbox > label { color: var(--tx1) !important; font-family: var(--font-body) !important; }

/* ── Animations ── */
@keyframes fadeUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes scanLine { 0% { top: -2px; } 100% { top: 100%; } }
@keyframes glowPulse { 0%,100% { opacity: 0.6; } 50% { opacity: 1; } }
@keyframes borderGlow { 0%,100% { border-color: var(--border); } 50% { border-color: var(--c0)66; } }
.fade-up { animation: fadeUp 0.45s ease forwards; }
.fade-in { animation: fadeIn 0.3s ease forwards; }

/* ── Glass Cards ── */
.g-card {
  background: var(--glass);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 22px 24px;
  margin: 8px 0;
  backdrop-filter: blur(10px);
  position: relative; overflow: hidden;
  transition: all 0.25s ease;
}
.g-card::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0; height: 1px;
  background: linear-gradient(90deg, transparent, var(--c0)44, transparent);
}
.g-card:hover { border-color: var(--c0)44; transform: translateY(-2px); box-shadow: 0 8px 32px rgba(0,0,0,0.4), 0 0 24px var(--glow0); }

/* Scholarship card with left accent */
.s-card {
  background: var(--glass);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 18px 22px;
  margin: 10px 0;
  position: relative; overflow: hidden;
  transition: all 0.22s ease;
}
.s-card::before {
  content: '';
  position: absolute; left: 0; top: 0; width: 3px; height: 100%;
  background: linear-gradient(180deg, var(--c0), var(--c1));
  border-radius: 0 0 0 14px;
}
.s-card:hover { border-color: var(--c0)44; transform: translateX(4px); box-shadow: 0 4px 24px rgba(0,0,0,0.3); }

/* Scan effect on cards */
.s-card::after {
  content: '';
  position: absolute; top: -2px; left: 0; width: 100%; height: 2px;
  background: linear-gradient(90deg, transparent, var(--c0)66, transparent);
  opacity: 0;
  transition: opacity 0.3s;
}
.s-card:hover::after { opacity: 1; animation: scanLine 0.8s ease forwards; }

/* ── Metric Boxes ── */
.metric {
  background: var(--glass2);
  border: 1px solid var(--border2);
  border-radius: 14px;
  padding: 20px;
  text-align: center;
  position: relative; overflow: hidden;
  transition: all 0.25s ease;
}
.metric:hover { border-color: var(--c1)66; box-shadow: 0 0 32px var(--glow1); transform: translateY(-3px); }
.metric::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px; background: linear-gradient(90deg, transparent, var(--c1)66, transparent); }
.metric-val { font-size: 2.2rem; font-weight: 800; color: var(--c0); font-family: var(--font-mono); line-height: 1; letter-spacing: -0.02em; }
.metric-label { font-size: 0.68rem; color: var(--tx3); text-transform: uppercase; letter-spacing: 0.14em; margin-top: 6px; font-family: var(--font-mono); }

/* ── Hero Section ── */
.hero {
  background: linear-gradient(135deg, rgba(0,255,224,0.04), rgba(0,112,255,0.06), rgba(112,0,255,0.04));
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 52px 40px;
  text-align: center;
  position: relative; overflow: hidden;
  margin-bottom: 28px;
}
.hero::before {
  content: '';
  position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
  background: radial-gradient(ellipse at center, rgba(0,112,255,0.06) 0%, transparent 60%);
  pointer-events: none;
}
.hero::after {
  content: '';
  position: absolute; bottom: 0; left: 0; right: 0; height: 1px;
  background: linear-gradient(90deg, transparent, var(--c0)55, transparent);
}
.hero-badge {
  display: inline-block;
  background: rgba(0,255,224,0.08);
  border: 1px solid rgba(0,255,224,0.25);
  border-radius: 20px;
  padding: 5px 16px;
  font-size: 0.7rem;
  color: var(--c0);
  font-family: var(--font-mono);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  margin-bottom: 20px;
}
.hero-title {
  font-family: var(--font-head);
  font-size: 3.2rem;
  font-weight: 800;
  background: linear-gradient(135deg, var(--c0) 0%, var(--c1) 50%, var(--c2) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1.1;
  letter-spacing: -0.02em;
  margin-bottom: 12px;
}
.hero-sub { color: var(--tx2); font-size: 1rem; line-height: 1.6; max-width: 550px; margin: 0 auto 20px; }

/* ── Section Headers ── */
.sec-head {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--c0);
  text-transform: uppercase;
  letter-spacing: 0.15em;
  margin: 28px 0 16px;
  display: flex; align-items: center; gap: 12px;
}
.sec-head::before { content: '//'; color: var(--c1); font-weight: 300; }
.sec-head::after { content: ''; flex: 1; height: 1px; background: linear-gradient(90deg, var(--c0)33, transparent); }

/* ── Badges ── */
.badge { display: inline-block; font-size: 0.68rem; font-weight: 600; padding: 3px 10px; border-radius: 20px; letter-spacing: 0.06em; font-family: var(--font-mono); }
.badge-red { background: rgba(255,0,60,0.12); border: 1px solid rgba(255,0,60,0.35); color: #ff4d6d; }
.badge-orange { background: rgba(255,140,0,0.12); border: 1px solid rgba(255,140,0,0.35); color: #ff9f0a; }
.badge-green { background: rgba(0,255,160,0.12); border: 1px solid rgba(0,255,160,0.35); color: #00ffa0; }
.badge-blue { background: rgba(0,112,255,0.12); border: 1px solid rgba(0,112,255,0.35); color: #60a5ff; }
.badge-gray { background: rgba(100,130,150,0.12); border: 1px solid rgba(100,130,150,0.3); color: #7a9ab5; }

/* ── Chat Bubbles ── */
.chat-user {
  background: linear-gradient(135deg, rgba(0,112,255,0.12), rgba(0,112,255,0.06));
  border: 1px solid rgba(0,112,255,0.25);
  border-radius: 16px 16px 4px 16px;
  padding: 14px 18px;
  margin: 8px 0;
  margin-left: 80px;
  font-size: 0.91rem;
  color: var(--tx1);
  line-height: 1.6;
}
.chat-ai {
  background: var(--glass);
  border: 1px solid var(--border);
  border-radius: 16px 16px 16px 4px;
  padding: 14px 18px;
  margin: 8px 0;
  margin-right: 80px;
  font-size: 0.91rem;
  color: var(--tx1);
  white-space: pre-wrap;
  line-height: 1.7;
}
.chat-ai::before { content: ''; display: block; width: 6px; height: 6px; background: var(--c0); border-radius: 50%; margin-bottom: 8px; animation: glowPulse 2s ease-in-out infinite; }

/* ── Stepper ── */
.step-item {
  display: flex; align-items: flex-start;
  padding: 16px 18px;
  background: var(--glass);
  border: 1px solid var(--border);
  border-radius: 10px;
  margin: 6px 0;
  transition: all 0.2s;
}
.step-item:hover { border-color: var(--c0)44; }
.step-num {
  width: 32px; height: 32px; min-width: 32px;
  background: linear-gradient(135deg, var(--c0), var(--c1));
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 0.78rem; color: #000;
  font-family: var(--font-mono); margin-right: 14px; margin-top: 2px;
}
.step-title { font-weight: 600; font-size: 0.92rem; color: var(--tx1); }
.step-detail { font-size: 0.8rem; color: var(--tx2); margin-top: 4px; line-height: 1.5; }

/* ── Terminal / Mono ── */
.mono { font-family: var(--font-mono); color: var(--c0); font-size: 0.85rem; }
.terminal {
  background: var(--bg0);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 16px 20px;
  font-family: var(--font-mono);
  font-size: 0.82rem;
  color: var(--c0);
  line-height: 1.7;
  position: relative;
}
.terminal::before { content: '● ● ●'; position: absolute; top: 10px; left: 16px; font-size: 0.65rem; color: var(--tx3); letter-spacing: 4px; }
.terminal-body { margin-top: 18px; }

/* ── Login Page ── */
.login-wrap { max-width: 440px; margin: 50px auto; }
.login-logo { text-align: center; margin-bottom: 36px; }
.login-logo .brand { font-family: var(--font-head); font-size: 2.2rem; font-weight: 800; background: linear-gradient(135deg, var(--c0), var(--c1)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -0.02em; }
.login-logo .sub { color: var(--tx3); font-size: 0.78rem; margin-top: 4px; font-family: var(--font-mono); text-transform: uppercase; letter-spacing: 0.1em; }

/* ── Compare Grid ── */
.cmp-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 4px; margin: 3px 0; }
.cmp-lbl { font-size: 0.72rem; font-weight: 600; color: var(--tx3); text-transform: uppercase; letter-spacing: 0.08em; padding: 8px 10px; font-family: var(--font-mono); }
.cmp-val { font-size: 0.85rem; color: var(--tx1); padding: 9px 12px; background: var(--glass); border: 1px solid var(--border); border-radius: 6px; }
.cmp-hdr { font-size: 0.82rem; font-weight: 700; color: var(--c0); padding: 9px 12px; background: var(--glass); border: 1px solid var(--c0)33; border-radius: 6px; font-family: var(--font-mono); }

/* ── Status indicator ── */
.status-dot { display: inline-block; width: 7px; height: 7px; border-radius: 50%; margin-right: 6px; animation: glowPulse 2s ease-in-out infinite; }
.status-dot.online { background: var(--c0); box-shadow: 0 0 8px var(--c0); }
.status-dot.offline { background: #ff4d6d; box-shadow: 0 0 8px #ff4d6d; }
.status-dot.warn { background: #ff9f0a; box-shadow: 0 0 8px #ff9f0a; }

/* ── RAG indicator ── */
.rag-badge {
  display: inline-flex; align-items: center; gap: 6px;
  background: rgba(0,255,224,0.06);
  border: 1px solid rgba(0,255,224,0.2);
  border-radius: 20px;
  padding: 4px 12px;
  font-size: 0.68rem;
  color: var(--c0);
  font-family: var(--font-mono);
  letter-spacing: 0.08em;
}
</style>
""", unsafe_allow_html=True)

# ── Session Init ─────────────────────────────────────────
def init_ss():
    defaults = {
        "page": "Dashboard", "logged_in": False,
        "username": "", "display_name": "",
        "chat_history": [], "bookmarks": [],
        "interview_q": None, "interview_history": [],
        "cv_result": None, "sop_result": None,
        "rejection_result": None, "roadmap_text": None,
        "ielts_prompt": None,
        "api_keys": {"groq": "", "gemini": ""},
        "profile": {
            "name": "", "cgpa": 3.0, "field": "", "year": "3rd Year",
            "country": "", "ielts": 6.5, "research": "none", "leadership": "none"
        },
        "checklist": {
            "Transcripts Ordered": False, "IELTS Registered": False,
            "3 Referees Contacted": False, "SOP First Draft": False,
            "CV Updated": False, "Financial Docs Ready": False,
            "Personal Statement Done": False, "Research Proposal": False
        },
        "users_db": DEMO_USERS.copy(),
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# ── Cached Resources ─────────────────────────────────────
@st.cache_resource(show_spinner=False)
def get_dm():
    base = os.path.dirname(os.path.abspath(__file__))
    return DataManager(os.path.join(base, "data", "scholarships.csv"))

@st.cache_resource(show_spinner=False)
def get_rag():
    """Build RAG index once and cache it"""
    dm = get_dm()
    rag = RAGEngine()
    rag.build_index(dm.df)
    return rag

@st.cache_resource(show_spinner=False)  # ← YEH LINE ADD KARO - ZARURI HAI
def get_engine():
    # Try secrets with bracket notation first
    gk = ""
    mk = ""
    
    try:
        gk = str(st.secrets["GROQ_API_KEY"]).strip()
        if gk == "None":
            gk = ""
    except (KeyError, Exception):
        pass
    
    if not gk:
        try:
            gk = str(st.secrets.get("GROQ_API_KEY", "")).strip()
            if gk == "None":
                gk = ""
        except Exception:
            pass
    
    try:
        mk = str(st.secrets.get("GEMINI_API_KEY", "")).strip()
        if mk == "None":
            mk = ""
    except Exception:
        pass
    
    engine = AIEngine(groq_key=gk, gemini_key=mk)
    engine.set_rag(get_rag())
    return engine

# ── Helpers ──────────────────────────────────────────────
def H(text):
    st.markdown(f'<div class="sec-head fade-up">{text}</div>', unsafe_allow_html=True)

def card(html, hover=True):
    cls = "g-card fade-up"
    st.markdown(f'<div class="{cls}">{html}</div>', unsafe_allow_html=True)

# ── LOGIN PAGE ────────────────────────────────────────────
def page_login():
    col1, col2, col3 = st.columns([1, 1.3, 1])
    with col2:
        st.markdown("""
        <div class="login-logo fade-up">
            <div style="font-size:3.5rem;margin-bottom:10px;filter:drop-shadow(0 0 20px rgba(0,255,224,0.5));">🎓</div>
            <div class="brand">ScholarAI Elite</div>
            <div class="sub">⚡ AI · RAG · Groq Llama3 · v4.0</div>
        </div>
        """, unsafe_allow_html=True)

        tab_login, tab_signup = st.tabs(["🔑 Login", "✨ Sign Up"])

        with tab_login:
            st.markdown('<div class="g-card fade-up" style="margin-top:8px;">', unsafe_allow_html=True)
            st.markdown('<div style="font-size:0.78rem;color:var(--tx3);font-family:var(--font-mono);letter-spacing:0.1em;text-transform:uppercase;margin-bottom:12px;">// AUTHENTICATE</div>', unsafe_allow_html=True)
            uname = st.text_input("Username", placeholder="Enter username", key="li_user")
            pwd = st.text_input("Password", type="password", placeholder="Enter password", key="li_pwd")
            st.markdown('</div>', unsafe_allow_html=True)

            if st.button("⚡ CONNECT", use_container_width=True, key="login_btn"):
                if uname and pwd:
                    ok, result = login_user(uname, pwd)
                    if ok:
                        st.session_state.logged_in = True
                        st.session_state.username = uname
                        st.session_state.display_name = result
                        st.session_state.profile["name"] = result
                        st.success(f"✅ Access granted — Welcome, {result}!")
                        time.sleep(0.6)
                        st.rerun()
                    else:
                        st.error(f"❌ {result}")
                else:
                    st.warning("Enter credentials to continue")

            st.markdown("""
            <div class="terminal" style="margin-top:14px;">
                <div class="terminal-body">
                    <span style="color:var(--tx3);">$</span> demo credentials<br>
                    <span style="color:var(--c0);">user:</span> <span style="color:var(--tx1);">demo</span><br>
                    <span style="color:var(--c0);">pass:</span> <span style="color:var(--tx1);">demo123</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with tab_signup:
            st.markdown('<div class="g-card fade-up" style="margin-top:8px;">', unsafe_allow_html=True)
            st.markdown('<div style="font-size:0.78rem;color:var(--tx3);font-family:var(--font-mono);letter-spacing:0.1em;text-transform:uppercase;margin-bottom:12px;">// NEW ACCOUNT</div>', unsafe_allow_html=True)
            s_name = st.text_input("Full Name", placeholder="Your full name", key="su_name")
            s_email = st.text_input("Email", placeholder="your@email.com", key="su_email")
            s_user = st.text_input("Username", placeholder="Choose a username", key="su_user")
            s_pwd = st.text_input("Password", type="password", placeholder="Min 6 characters", key="su_pwd")
            s_pwd2 = st.text_input("Confirm Password", type="password", placeholder="Repeat password", key="su_pwd2")
            st.markdown('</div>', unsafe_allow_html=True)

            if st.button("✨ CREATE ACCOUNT", use_container_width=True, key="signup_btn"):
                if not all([s_name, s_email, s_user, s_pwd]):
                    st.warning("Fill all fields")
                elif len(s_pwd) < 6:
                    st.error("Password min 6 characters")
                elif s_pwd != s_pwd2:
                    st.error("Passwords don't match")
                else:
                    ok, msg = register_user(s_user, s_pwd, s_name, s_email)
                    if ok:
                        st.success("✅ Account created! Login now.")
                    else:
                        st.error(f"❌ {msg}")

# ── SIDEBAR ────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        # Logo
        st.markdown("""
        <div style="text-align:center;padding:16px 0 20px;">
            <div style="font-size:2.2rem;margin-bottom:6px;filter:drop-shadow(0 0 16px rgba(0,255,224,0.6));">🎓</div>
            <div style="font-family:'Syne',sans-serif;font-size:1.05rem;font-weight:800;background:linear-gradient(135deg,var(--c0),var(--c1));-webkit-background-clip:text;-webkit-text-fill-color:transparent;">SCHOLARAI ELITE</div>
            <div style="font-size:0.62rem;color:var(--tx3);font-family:'JetBrains Mono',monospace;letter-spacing:0.15em;text-transform:uppercase;margin-top:3px;">v4.0 · RAG POWERED</div>
        </div>
        """, unsafe_allow_html=True)

        # User + RAG status
        ai = get_engine()
        if ai.groq_client:
            api_status = '<span class="status-dot online"></span>Groq Active'
            api_color = "var(--c0)"
        else:
            api_status = '<span class="status-dot offline"></span>No API Key'
            api_color = "#ff4d6d"

        rag = get_rag()
        rag_status = f'<span class="status-dot online"></span>RAG: {len(rag.documents)} docs' if rag.is_built else '<span class="status-dot warn"></span>RAG offline'

        st.markdown(f"""
        <div class="g-card" style="padding:12px 16px;margin:4px 0 14px;">
            <div style="font-size:0.7rem;color:var(--tx3);font-family:var(--font-mono);letter-spacing:0.1em;text-transform:uppercase;">OPERATOR</div>
            <div style="font-weight:700;font-size:0.95rem;color:var(--c0);margin-top:4px;">👤 {st.session_state.display_name}</div>
            <div style="margin-top:10px;display:flex;flex-direction:column;gap:4px;">
                <div style="font-size:0.7rem;font-family:var(--font-mono);color:{api_color};">{api_status}</div>
                <div style="font-size:0.7rem;font-family:var(--font-mono);color:var(--c0);">{rag_status}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div style="height:1px;background:var(--border);margin:8px 0 12px;"></div>', unsafe_allow_html=True)

        # Navigation
        pages = [
            ("🏠", "Dashboard"), ("🔍", "Scholarships"), ("🤖", "AI Chat"),
            ("📄", "CV Analyzer"), ("✍️", "SOP Improve"), ("🗺️", "Roadmap"),
            ("⚠️", "Rejection Sim"), ("🎤", "IELTS Prep"), ("🎯", "Interview Prep"),
            ("📊", "Compare"), ("🔖", "Bookmarks"), ("⚙️", "Settings"),
        ]
        current = st.session_state.page
        for icon, label in pages:
            if current == label:
                st.markdown(f"""<div style="background:linear-gradient(135deg,rgba(0,112,255,0.15),rgba(112,0,255,0.1));border:1px solid rgba(0,112,255,0.3);border-left:3px solid var(--c1);border-radius:8px;padding:9px 14px;margin:2px 0;font-size:0.84rem;font-weight:600;color:var(--c1);font-family:'Space Grotesk',sans-serif;">{icon} &nbsp;{label}</div>""", unsafe_allow_html=True)
            else:
                if st.button(f"{icon}  {label}", key=f"nav_{label}", use_container_width=True):
                    st.session_state.page = label
                    st.rerun()

        st.markdown('<div style="height:1px;background:var(--border);margin:12px 0;"></div>', unsafe_allow_html=True)

        # Profile strength
        dm = get_dm()
        ps = dm.calculate_profile_strength(st.session_state.profile)
        sc = ps.get("score", 0)
        strength = ps.get("strength", "🔴 Weak")
        st.markdown(f'<div style="font-size:0.7rem;color:var(--tx3);font-family:var(--font-mono);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:6px;">PROFILE: {strength}</div>', unsafe_allow_html=True)
        st.progress(sc / 100)
        st.markdown(f'<div style="font-size:0.68rem;color:var(--tx3);font-family:var(--font-mono);text-align:right;margin-top:2px;">{sc}% complete</div>', unsafe_allow_html=True)

        st.markdown(f'<div style="font-size:0.68rem;color:var(--tx3);font-family:var(--font-mono);margin-top:8px;">🔖 {len(st.session_state.bookmarks)} saved</div>', unsafe_allow_html=True)

        st.markdown('<div style="height:1px;background:var(--border);margin:12px 0;"></div>', unsafe_allow_html=True)

        if st.button("🚪 LOGOUT", use_container_width=True, key="logout_btn"):
            for key in ["logged_in", "username", "display_name"]:
                st.session_state[key] = "" if key != "logged_in" else False
            st.rerun()

# ── PAGE: DASHBOARD ────────────────────────────────────────
def page_dashboard():
    dm = get_dm()
    rag = get_rag()
    ai = get_engine()
    name = st.session_state.display_name

    st.markdown(f"""
    <div class="hero fade-up">
        <div class="hero-badge">⚡ GROQ LLAMA3 · RAG · REAL-TIME AI</div>
        <div class="hero-title">ScholarAI Elite</div>
        <div class="hero-sub">Welcome back, <strong style="color:var(--c0);">{name}</strong> — Your AI scholarship intelligence platform is online</div>
        <div style="display:flex;justify-content:center;gap:12px;flex-wrap:wrap;margin-top:16px;">
            <div class="rag-badge">🔍 {len(rag.documents)} Scholarships Indexed</div>
            <div class="rag-badge">🤖 RAG {"Active" if rag.is_built else "Building..."}</div>
            <div class="rag-badge">⚡ {"Groq Connected" if ai.groq_client else "Setup Required"}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Profile setup
    if not st.session_state.profile.get("field"):
        st.info("⚡ Complete your profile below for personalized AI + RAG recommendations!")

    with st.expander("⚡ Quick Profile Setup", expanded=not st.session_state.profile.get("field")):
        c1, c2, c3 = st.columns(3)
        with c1:
            nm = st.text_input("Name", value=st.session_state.profile.get("name",""), key="dp_name")
            cgpa = st.number_input("CGPA (0-4.0)", 0.0, 4.0, float(st.session_state.profile.get("cgpa",3.0)), 0.1, key="dp_cgpa")
        with c2:
            field_opts = ["","Computer Science","Engineering","Business","Biology","Medicine","Arts","Economics","Law","Education","Psychology","Agriculture"]
            cur_field = st.session_state.profile.get("field","")
            field_idx = field_opts.index(cur_field) if cur_field in field_opts else 0
            field = st.selectbox("Field of Study", field_opts, key="dp_field", index=field_idx)
            year = st.selectbox("Current Year", ["1st Year","2nd Year","3rd Year","4th Year","Graduate","Working Professional"], key="dp_year")
        with c3:
            ielts = st.number_input("IELTS Score", 0.0, 9.0, float(st.session_state.profile.get("ielts",6.5)), 0.5, key="dp_ielts")
            country_opts = ["","USA","UK","Germany","Australia","Canada","Japan","South Korea","Sweden","China","Netherlands","Hungary"]
            country = st.selectbox("Target Country", country_opts, key="dp_country")
        c4, c5 = st.columns(2)
        with c4:
            research = st.selectbox("Research Experience", ["none","minimal","coursework projects","conference paper","published paper","multiple publications"], key="dp_res")
        with c5:
            leadership = st.selectbox("Leadership Experience", ["none","minimal","club member","club officer","founded organization","professional role"], key="dp_lead")

        if st.button("💾 Save Profile", use_container_width=True, key="dp_save"):
            st.session_state.profile.update({
                "name": nm or st.session_state.display_name, "cgpa": cgpa, "field": field,
                "year": year, "ielts": ielts, "country": country, "research": research, "leadership": leadership
            })
            st.success("✅ Profile saved! AI + RAG recommendations are now personalized.")
            st.rerun()

    # Metrics
    total = len(dm.df)
    now = pd.Timestamp.now()
    try: upcoming = int((dm.df['deadline'] > now).sum())
    except: upcoming = total
    ps = dm.calculate_profile_strength(st.session_state.profile)

    cols = st.columns(4)
    for col, (val, label) in zip(cols, [
        (str(total), "Scholarships in DB"),
        (str(upcoming), "Open Deadlines"),
        (str(len(st.session_state.bookmarks)), "Bookmarked"),
        (f"{ps.get('score',0)}%", "Profile Strength"),
    ]):
        with col:
            st.markdown(f'<div class="metric fade-up"><div class="metric-val">{val}</div><div class="metric-label">{label}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Quick access
    H("QUICK ACCESS")
    features = [
        ("🤖 AI Chat", "RAG-powered advisor", "AI Chat"),
        ("📄 CV Analyzer", "ATS score + fixes", "CV Analyzer"),
        ("✍️ SOP Improve", "High-impact rewrite", "SOP Improve"),
        ("🗺️ Roadmap", "12-month plan", "Roadmap"),
        ("⚠️ Rejection Sim", "Risk analysis", "Rejection Sim"),
        ("🎤 IELTS Prep", "Mock prompts", "IELTS Prep"),
        ("🎯 Interview Prep", "AI-scored Q&A", "Interview Prep"),
        ("📊 Compare", "Side-by-side", "Compare"),
    ]
    for row in range(0, len(features), 4):
        cols = st.columns(4)
        for i, (title, desc, pg) in enumerate(features[row:row+4]):
            with cols[i]:
                st.markdown(f'<div class="g-card" style="min-height:90px;cursor:pointer;"><div style="font-weight:700;font-size:0.88rem;margin-bottom:6px;color:var(--tx1);">{title}</div><div style="font-size:0.75rem;color:var(--tx3);">{desc}</div></div>', unsafe_allow_html=True)
                if st.button("Open →", key=f"qa_{pg}", use_container_width=True):
                    st.session_state.page = pg; st.rerun()

    # Checklist
    H("APPLICATION CHECKLIST")
    items = list(st.session_state.checklist.items())
    c1, c2 = st.columns(2)
    for i, (item, done) in enumerate(items):
        with (c1 if i < len(items)//2 else c2):
            new = st.checkbox(item, value=done, key=f"chk_{item}")
            st.session_state.checklist[item] = new
    done_n = sum(v for v in st.session_state.checklist.values())
    st.progress(done_n / len(st.session_state.checklist))
    st.caption(f"📋 {done_n}/{len(st.session_state.checklist)} tasks complete")

    # Timeline
    H("SCHOLARSHIP SUCCESS TIMELINE")
    steps = [
        ("Research & Target", "Identify 5-8 scholarships, research requirements, create tracking spreadsheet", "Month 1-2"),
        ("Profile Enhancement", "Strengthen CGPA, get IELTS 7+, join research projects, document leadership", "Month 3-5"),
        ("Document Preparation", "SOP, updated CV, official transcripts, reference letter briefs", "Month 6-7"),
        ("Application Submission", "Submit all applications before deadlines with proofread documents", "Month 8-10"),
        ("Interview Preparation", "Practice 20+ questions, research committees, prepare STAR examples", "Month 10-11"),
        ("Decision & Acceptance", "Receive offers, compare terms, prepare for relocation", "Month 12"),
    ]
    colors = ["var(--c0)","var(--c1)","var(--c2)","#00ffa0","#ff9f0a","#60a5ff"]
    for i, (title, detail, timing) in enumerate(steps):
        st.markdown(f'<div class="step-item fade-up"><div class="step-num" style="background:{colors[i]};color:#000;">{i+1}</div><div><div class="step-title">{title} <span style="font-size:0.7rem;color:var(--tx3);font-family:var(--font-mono);margin-left:8px;">// {timing}</span></div><div class="step-detail">{detail}</div></div></div>', unsafe_allow_html=True)

# ── PAGE: SCHOLARSHIPS ────────────────────────────────────
def page_scholarships():
    H("SCHOLARSHIP DATABASE — 2026 VERIFIED")
    dm = get_dm()

    with st.expander("🔧 Filters", expanded=True):
        c1,c2,c3,c4,c5 = st.columns(5)
        with c1: ctry = st.selectbox("Country", dm.get_countries(), key="f_ctry")
        with c2: fld = st.selectbox("Field", dm.get_fields(), key="f_fld")
        with c3: deg = st.selectbox("Degree", dm.get_degrees(), key="f_deg")
        with c4: gpa = st.slider("My CGPA", 0.0, 4.0, float(st.session_state.profile.get("cgpa",3.0)), 0.1, key="f_gpa")
        with c5: srch = st.text_input("Search", placeholder="keyword...", key="f_srch")

    filtered = dm.filter_scholarships(ctry, fld, deg, gpa, srch)
    st.markdown(f'<div style="font-size:0.78rem;color:var(--tx3);font-family:var(--font-mono);letter-spacing:0.08em;margin-bottom:12px;">// {len(filtered)} RESULTS FOUND</div>', unsafe_allow_html=True)

    if filtered.empty:
        card('<div style="text-align:center;padding:30px;color:var(--tx3);">No results. Try broader filters.</div>')
        return

    for idx, row in filtered.iterrows():
        name = str(row.get('name','Unknown'))
        ctry_v = str(row.get('country','N/A'))
        fld_v = str(row.get('field','N/A'))
        amt = str(row.get('amount','N/A'))
        deadline = row.get('deadline',None)
        gpa_r = str(row.get('gpa required','N/A'))
        lang = str(row.get('language requirement','N/A'))
        desc = str(row.get('description',''))
        url = str(row.get('url','#'))
        success = str(row.get('success rate','N/A'))
        deg_v = str(row.get('degree','N/A'))
        notes = str(row.get('notes 2026',''))
        badge_text, badge_color, days = dm.get_deadline_status(deadline)
        is_bm = name in st.session_state.bookmarks

        st.markdown(f"""
        <div class="s-card fade-up">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;">
                <div style="flex:1;">
                    <div style="font-size:1.02rem;font-weight:700;color:var(--tx1);font-family:'Syne',sans-serif;">{name}</div>
                    <div style="font-size:0.75rem;color:var(--tx3);margin-top:4px;font-family:var(--font-mono);">🌍 {ctry_v} &nbsp;·&nbsp; 📚 {fld_v} &nbsp;·&nbsp; 🎓 {deg_v}</div>
                </div>
                <span class="badge badge-{badge_color}">{badge_text}</span>
            </div>
            <div style="margin-top:10px;font-size:0.83rem;color:var(--tx2);line-height:1.55;">{desc[:180]}{'...' if len(desc)>180 else ''}</div>
            <div style="display:flex;gap:18px;margin-top:12px;flex-wrap:wrap;">
                <span style="font-size:0.78rem;color:var(--tx1);">💰 <b style="color:var(--c0);">{amt}</b></span>
                <span style="font-size:0.78rem;color:var(--tx1);">📊 GPA: <b>{gpa_r}+</b></span>
                <span style="font-size:0.78rem;color:var(--tx1);">🗣️ <b>{lang}</b></span>
                <span style="font-size:0.78rem;color:var(--tx1);">✅ Success: <b>{success}</b></span>
            </div>
            {f'<div style="margin-top:10px;font-size:0.75rem;color:var(--c0);background:var(--glass);border:1px solid var(--border);border-radius:6px;padding:6px 10px;font-family:var(--font-mono);">📌 {notes}</div>' if notes and notes != 'nan' else ''}
        </div>
        """, unsafe_allow_html=True)

        ca, cb, cc = st.columns([3,1,1])
        with ca: st.markdown(f'<div style="font-size:0.8rem;color:var(--tx2);padding:4px 0;">🔗 <a href="{url}" style="color:var(--c1);" target="_blank">Official Website</a></div>', unsafe_allow_html=True)
        with cb:
            bm_lbl = "❤️ Saved" if is_bm else "🔖 Save"
            if st.button(bm_lbl, key=f"bm_{idx}", use_container_width=True):
                if is_bm: st.session_state.bookmarks.remove(name)
                else: st.session_state.bookmarks.append(name)
                st.rerun()
        with cc:
            if st.button("📥 PDF", key=f"exp_{idx}", use_container_width=True):
                pdf = dm.export_to_pdf(f"Scholarship: {name}", [
                    {"heading":"Overview","body":f"Country: {ctry_v}\nField: {fld_v}\nDegree: {deg_v}\nAmount: {amt}"},
                    {"heading":"Requirements","body":f"GPA: {gpa_r}+\nLanguage: {lang}\nSuccess Rate: {success}"},
                    {"heading":"Description","body":desc},
                    {"heading":"Apply","body":f"URL: {url}"},
                ])
                st.download_button("⬇️ Download", pdf, f"{name[:30]}.pdf", "application/pdf", key=f"dl_{idx}")

# ── PAGE: AI CHAT ─────────────────────────────────────────
def page_ai_chat():
    H("AI SCHOLAR ASSISTANT — RAG ENHANCED")
    ai = get_engine()
    rag = get_rag()

    # Status bar
    if ai.groq_client:
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown('<div class="g-card" style="padding:12px 16px;"><span class="status-dot online"></span><span style="font-size:0.78rem;color:var(--c0);font-family:var(--font-mono);">GROQ LLAMA3-70B ACTIVE</span></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="g-card" style="padding:12px 16px;"><span class="status-dot online"></span><span style="font-size:0.78rem;color:var(--c0);font-family:var(--font-mono);">RAG INDEX: {len(rag.documents)} DOCS</span></div>', unsafe_allow_html=True)
        with c3: st.markdown('<div class="g-card" style="padding:12px 16px;"><span class="status-dot online"></span><span style="font-size:0.78rem;color:var(--c0);font-family:var(--font-mono);">CONTEXT-AWARE RESPONSES</span></div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="g-card" style="border-color:rgba(255,140,0,0.3);background:rgba(255,140,0,0.05);">
            <span class="status-dot warn"></span>
            <span style="font-size:0.84rem;color:#ff9f0a;font-family:var(--font-mono);">API KEY NOT SET — Go to ⚙️ Settings → Add your free Groq API key from console.groq.com</span>
        </div>
        """, unsafe_allow_html=True)

    # Quick questions
    st.markdown(f'<div style="font-size:0.72rem;color:var(--tx3);font-family:var(--font-mono);letter-spacing:0.1em;text-transform:uppercase;margin:16px 0 10px;">// QUICK QUESTIONS</div>', unsafe_allow_html=True)
    qs = [
        f"Which scholarships match my CGPA {st.session_state.profile.get('cgpa',3.0)}?",
        f"Career paths for {st.session_state.profile.get('field','CS') or 'CS'}?",
        "How to write a winning SOP?",
        "How to get strong reference letters?",
        "What to do 6 months before deadline?",
        "How to improve my IELTS fast?",
    ]
    c1,c2,c3 = st.columns(3)
    for i, (col, q) in enumerate(zip([c1,c2,c3,c1,c2,c3], qs)):
        with col:
            if st.button(q[:42]+"..." if len(q)>42 else q, key=f"qq_{i}", use_container_width=True):
                st.session_state.chat_history.append({"role":"user","content":q})
                with st.spinner("🧠 Retrieving context + generating response..."):
                    reply = ai.chat_response(q, st.session_state.profile, st.session_state.chat_history[:-1])
                st.session_state.chat_history.append({"role":"assistant","content":reply})
                st.rerun()

    st.markdown('<div style="height:1px;background:var(--border);margin:16px 0;"></div>', unsafe_allow_html=True)

    # Chat
    if not st.session_state.chat_history:
        st.markdown("""
        <div class="g-card" style="text-align:center;padding:60px 20px;">
            <div style="font-size:3rem;margin-bottom:14px;filter:drop-shadow(0 0 20px rgba(0,255,224,0.5));">🤖</div>
            <div style="font-family:'Syne',sans-serif;font-size:1.2rem;font-weight:700;color:var(--c0);margin-bottom:8px;">ScholarAI RAG Ready</div>
            <div style="color:var(--tx3);font-size:0.88rem;max-width:420px;margin:0 auto;line-height:1.6;">Ask anything about scholarships, IELTS, SOP writing, or career paths. I'll search the scholarship database first, then answer with specific context.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in st.session_state.chat_history:
            role = msg.get("role","user")
            content = msg.get("content","")
            if role == "user":
                st.markdown(f'<div class="chat-user fade-up"><span style="font-size:0.7rem;color:rgba(0,112,255,0.7);font-family:var(--font-mono);text-transform:uppercase;letter-spacing:0.08em;">YOU</span><br>{content}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-ai fade-up"><span style="font-size:0.7rem;color:var(--c0);font-family:var(--font-mono);text-transform:uppercase;letter-spacing:0.08em;">SCHOLARAI</span><br>{content}</div>', unsafe_allow_html=True)

    # Input form
    with st.form("chat_form", clear_on_submit=True):
        c1, c2 = st.columns([6,1])
        with c1:
            user_in = st.text_input("Message", placeholder="Ask about scholarships, IELTS, SOP, career paths... AI will search database first.", label_visibility="collapsed")
        with c2:
            sent = st.form_submit_button("Send ⚡", use_container_width=True)

    if sent and user_in.strip():
        st.session_state.chat_history.append({"role":"user","content":user_in})
        with st.spinner("🔍 Searching database → 🧠 Generating response..."):
            reply = ai.chat_response(user_in, st.session_state.profile, st.session_state.chat_history[:-1])
        st.session_state.chat_history.append({"role":"assistant","content":reply})
        st.rerun()

    if st.session_state.chat_history:
        c1,c2 = st.columns(2)
        with c1:
            if st.button("🗑️ Clear Chat", key="clr_chat"):
                st.session_state.chat_history = []; st.rerun()
        with c2:
            dm = get_dm()
            secs = [{"heading":f"{'You' if m['role']=='user' else 'ScholarAI'} ({i+1})","body":m.get("content","")} for i,m in enumerate(st.session_state.chat_history)]
            pdf = dm.export_to_pdf("AI Chat History", secs)
            st.download_button("📥 Export Chat PDF", pdf, "chat_history.pdf","application/pdf",key="chat_pdf")

# ── PAGE: CV ANALYZER ─────────────────────────────────────
def page_cv():
    H("CV ANALYZER & ATS SCORER")
    ai = get_engine()

    tab1, tab2 = st.tabs(["📤 Upload / Paste CV", "📊 Analysis Results"])

    with tab1:
        card("""<div style="font-family:'Syne',sans-serif;font-size:1rem;font-weight:700;color:var(--c0);margin-bottom:8px;">🤖 AI-Powered CV Analysis</div>
<div style="color:var(--tx2);font-size:0.85rem;">Upload CV as PDF or paste text. AI gives ATS score, 5 specific weaknesses, and scholarship-specific improvements.</div>""")

        method = st.radio("Input method", ["📁 Upload PDF", "📋 Paste Text"], horizontal=True)
        cv_text = ""

        if method == "📁 Upload PDF":
            up = st.file_uploader("Upload CV/Resume PDF", type=["pdf"])
            if up:
                with st.spinner("Extracting text..."):
                    cv_text = extract_text_from_pdf(up)
                if cv_text:
                    st.success("✅ Text extracted successfully!")
                    with st.expander("Preview extracted text"):
                        st.text(cv_text[:1200]+"..." if len(cv_text)>1200 else cv_text)
        else:
            cv_text = st.text_area("Paste CV text here", height=280, placeholder="Paste your full CV/Resume content — Education, Experience, Skills, Projects, Publications...", key="cv_paste")

        if cv_text and len(cv_text) > 100:
            if st.button("🔍 ANALYZE CV", use_container_width=True, key="analyze_cv"):
                with st.spinner("🤖 AI analyzing your CV... (15-30 seconds)"):
                    result = ai.analyze_cv(cv_text)
                    st.session_state.cv_result = result
                st.success("✅ Analysis complete! Check Results tab →")
                st.rerun()
        elif cv_text:
            st.warning("Add more CV content (minimum 100 characters)")

    with tab2:
        r = st.session_state.cv_result
        if not r:
            st.info("👈 Upload or paste your CV in the first tab to see analysis here.")
            return

        ats = r.get("ats_score", 0)
        grade = r.get("grade", "N/A")
        assess = r.get("assessment","")
        sc_color = "#ff4d6d" if ats<50 else "#ff9f0a" if ats<70 else "#00ffa0"

        c1,c2,c3 = st.columns([1,2,1])
        with c2:
            st.markdown(f"""
            <div class="g-card" style="text-align:center;border-color:{sc_color}44;">
                <div style="font-size:0.7rem;color:var(--tx3);font-family:var(--font-mono);text-transform:uppercase;letter-spacing:0.12em;margin-bottom:10px;">ATS COMPATIBILITY SCORE</div>
                <div style="font-size:5rem;font-weight:900;color:{sc_color};font-family:var(--font-mono);line-height:1;text-shadow:0 0 30px {sc_color}66;">{ats}</div>
                <div style="font-size:1.3rem;font-weight:700;color:{sc_color};margin-top:6px;">Grade: {grade}</div>
                <div style="margin-top:12px;font-size:0.84rem;color:var(--tx2);">{assess}</div>
            </div>
            """, unsafe_allow_html=True)
        st.progress(ats/100)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="sec-head">WEAKNESSES</div>', unsafe_allow_html=True)
            for i, w in enumerate(r.get("weaknesses",[]),1):
                st.markdown(f'<div class="g-card" style="border-left:3px solid #ff4d6d;padding:10px 14px;margin:5px 0;"><span style="color:#ff4d6d;font-weight:700;font-family:var(--font-mono);">{i:02d}</span> <span style="font-size:0.85rem;">{w}</span></div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="sec-head">IMPROVEMENTS</div>', unsafe_allow_html=True)
            for i, imp in enumerate(r.get("improvements",[]),1):
                st.markdown(f'<div class="g-card" style="border-left:3px solid #00ffa0;padding:10px 14px;margin:5px 0;"><span style="color:#00ffa0;font-weight:700;font-family:var(--font-mono);">{i:02d}</span> <span style="font-size:0.85rem;">{imp}</span></div>', unsafe_allow_html=True)

        c3,c4 = st.columns(2)
        with c3:
            st.markdown("**✅ Sections Found:**")
            for s in r.get("sections_found",[]): st.markdown(f'<div style="font-size:0.82rem;color:#00ffa0;padding:2px 0;">✅ {s}</div>', unsafe_allow_html=True)
        with c4:
            st.markdown("**❌ Missing Sections:**")
            for s in r.get("sections_missing",[]): st.markdown(f'<div style="font-size:0.82rem;color:#ff4d6d;padding:2px 0;">❌ {s}</div>', unsafe_allow_html=True)

        kws = r.get("missing_keywords",[])
        if kws:
            st.markdown("**🔑 Missing Keywords:**")
            st.markdown("  ".join(f'<code style="background:var(--bg3);border:1px solid var(--border);padding:3px 8px;border-radius:5px;color:var(--c0);font-family:var(--font-mono);font-size:0.78rem;">{k}</code>' for k in kws), unsafe_allow_html=True)

        dm = get_dm()
        pdf = dm.export_to_pdf("CV Analysis Report",[
            {"heading":"ATS Score","body":f"Score: {ats}/100\nGrade: {grade}\n{assess}"},
            {"heading":"Weaknesses","body":"\n".join(f"{i}. {w}" for i,w in enumerate(r.get("weaknesses",[]),1))},
            {"heading":"Improvements","body":"\n".join(f"{i}. {w}" for i,w in enumerate(r.get("improvements",[]),1))},
            {"heading":"Keywords Missing","body":", ".join(kws)},
        ])
        st.download_button("📥 Export PDF Report", pdf, "cv_analysis.pdf", "application/pdf", key="cv_pdf")

# ── PAGE: SOP IMPROVE ──────────────────────────────────────
def page_sop():
    H("SOP IMPROVE — HIGH IMPACT REWRITER")
    ai = get_engine()

    card("""<div style="font-family:'Syne',sans-serif;font-size:1rem;font-weight:700;color:var(--c0);margin-bottom:8px;">🚀 AI Statement of Purpose Rewriter</div>
<div style="color:var(--tx2);font-size:0.85rem;">Paste your SOP — AI rewrites with compelling opening, specific achievements, clear vision, and powerful conclusion. Get before/after impact scores.</div>""")

    c1,c2 = st.columns(2)
    with c1: target = st.text_input("Target Scholarship", placeholder="e.g. Chevening 2027", key="sop_target")
    with c2: focus = st.selectbox("Emphasis", ["Overall Quality","Research Focus","Leadership","Community Impact","Career Vision"], key="sop_focus")

    original = st.text_area("📝 Your Current SOP", height=280, placeholder="Paste your Statement of Purpose here...\n\nTip: Include background, motivation, research goals, future plans. The more detail, the better the rewrite.", key="sop_orig")

    if original and len(original) > 150:
        if st.button("🚀 REWRITE FOR HIGH IMPACT", use_container_width=True, key="sop_btn"):
            with st.spinner("✍️ AI rewriting your SOP... (20-40 seconds)"):
                result = ai.rewrite_sop(original, target)
                st.session_state.sop_result = result
            st.rerun()
    elif original:
        st.warning("Please paste a longer SOP (minimum 150 characters)")

    r = st.session_state.sop_result
    if r:
        bef = r.get("score_before",0); aft = r.get("score_after",0); imp = aft - bef
        c1,c2,c3 = st.columns(3)
        with c1: st.markdown(f'<div class="metric"><div class="metric-val" style="color:#ff4d6d;">{bef}</div><div class="metric-label">Score Before</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="metric"><div class="metric-val" style="color:#00ffa0;">{aft}</div><div class="metric-label">Score After</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="metric"><div class="metric-val" style="color:var(--c0);">+{imp}</div><div class="metric-label">Improvement</div></div>', unsafe_allow_html=True)
        st.progress(aft/100)

        st.markdown('<div class="sec-head">AI-REWRITTEN HIGH-IMPACT SOP</div>', unsafe_allow_html=True)
        rewritten = r.get("rewritten_sop","")
        st.markdown(f'<div class="g-card" style="border-left:4px solid #00ffa0;"><div style="white-space:pre-wrap;font-size:0.9rem;line-height:1.8;color:var(--tx1);">{rewritten}</div></div>', unsafe_allow_html=True)
        st.text_area("📋 Copy Rewritten SOP", rewritten, height=180, key="sop_copy")

        c1,c2 = st.columns(2)
        with c1:
            st.markdown("**🔄 Changes Made:**")
            for ch in r.get("changes",[]): st.markdown(f'<div style="font-size:0.82rem;color:#00ffa0;padding:2px 0;">✅ {ch}</div>', unsafe_allow_html=True)
        with c2:
            st.markdown("**💡 Further Suggestions:**")
            for sg in r.get("suggestions",[]): st.markdown(f'<div style="font-size:0.82rem;color:var(--c1);padding:2px 0;">→ {sg}</div>', unsafe_allow_html=True)

        dm = get_dm()
        pdf = dm.export_to_pdf("SOP Improvement Report",[
            {"heading":"Impact Scores","body":f"Before: {bef}/100\nAfter: {aft}/100\nImprovement: +{imp} points"},
            {"heading":"Rewritten SOP","body":rewritten},
            {"heading":"Changes","body":"\n".join(r.get("changes",[]))},
            {"heading":"Suggestions","body":"\n".join(r.get("suggestions",[]))},
        ])
        st.download_button("📥 Export SOP Report", pdf, "sop_report.pdf", "application/pdf", key="sop_pdf")

# ── PAGE: ROADMAP ──────────────────────────────────────────
def page_roadmap():
    H("FULL SCHOLARSHIP ROADMAP")
    ai = get_engine()

    c1,c2,c3 = st.columns(3)
    with c1: cur_yr = st.selectbox("Current Year", ["1st Year","2nd Year","3rd Year","4th Year","Graduate","Working Professional"], key="rm_yr")
    with c2: tgt_deg = st.selectbox("Target Degree", ["Masters","PhD","Postdoctoral","MBA","LLM"], key="rm_deg")
    with c3: tgt_yr = st.selectbox("Target Start", ["2026","2027","2028"], key="rm_tyr")
    fld = st.session_state.profile.get("field","") or st.text_input("Field of Study", placeholder="e.g. Computer Science", key="rm_fld_inp")

    if st.button("🗺️ GENERATE MY ROADMAP", use_container_width=True, key="rm_btn"):
        with st.spinner("🤖 Generating personalized roadmap..."):
            rm = ai.generate_roadmap(cur_yr, fld, tgt_deg, tgt_yr, st.session_state.profile)
            st.session_state.roadmap_text = rm
        st.rerun()

    if st.session_state.roadmap_text:
        st.markdown(f'<div class="g-card" style="border-left:4px solid var(--c0);"><div style="white-space:pre-wrap;font-size:0.88rem;line-height:1.85;color:var(--tx1);">{st.session_state.roadmap_text}</div></div>', unsafe_allow_html=True)
        dm = get_dm()
        pdf = dm.export_to_pdf("Scholarship Roadmap",[{"heading":"Your Personalized 12-Month Roadmap","body":st.session_state.roadmap_text}])
        st.download_button("📥 Download Roadmap PDF", pdf, "roadmap.pdf", "application/pdf", key="rm_pdf")

# ── PAGE: REJECTION SIM ────────────────────────────────────
def page_rejection():
    H("REJECTION RISK SIMULATOR")
    ai = get_engine()

    card("""<div style="font-family:'Syne',sans-serif;font-size:1rem;font-weight:700;color:#ff4d6d;margin-bottom:8px;">🚨 AI Rejection Risk Analysis</div>
<div style="color:var(--tx2);font-size:0.85rem;">AI analyzes your profile against real scholarship criteria to predict rejection risks — so you can fix them BEFORE submitting.</div>""")

    c1,c2,c3 = st.columns(3)
    with c1:
        cgpa = st.number_input("Your CGPA", 0.0, 4.0, float(st.session_state.profile.get("cgpa",3.0)), 0.1, key="rj_cgpa")
        ielts = st.number_input("IELTS Score", 0.0, 9.0, float(st.session_state.profile.get("ielts",6.5)), 0.5, key="rj_ielts")
    with c2:
        research = st.selectbox("Research Experience", ["none","minimal","coursework projects","conference paper","published paper","multiple publications"], key="rj_res")
        leadership = st.selectbox("Leadership", ["none","minimal","club member","club officer","founded organization"], key="rj_lead")
    with c3:
        target_sc = st.text_input("Target Scholarship", placeholder="e.g. Chevening 2027", key="rj_tgt")
        sop_st = st.selectbox("SOP Status", ["Not started","First draft","Reviewed draft","Final version"], key="rj_sop")

    if st.button("🔍 ANALYZE MY REJECTION RISK", use_container_width=True, key="rj_btn"):
        profile = {"cgpa":cgpa,"ielts":ielts,"research":research,"leadership":leadership,"target_scholarship":target_sc,"field":st.session_state.profile.get("field","General")}
        with st.spinner("🔬 AI analyzing your risks..."):
            result = ai.simulate_rejection(profile)
            st.session_state.rejection_result = result
        st.rerun()

    r = st.session_state.rejection_result
    if r:
        prob = r.get("success_probability",0)
        verdict = r.get("verdict","Unknown")
        vc = "#ff4d6d" if "High" in verdict else "#ff9f0a" if "Medium" in verdict else "#00ffa0"

        c1,c2,c3 = st.columns(3)
        with c1: st.markdown(f'<div class="metric"><div class="metric-val" style="color:{vc};">{prob}%</div><div class="metric-label">Success Probability</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="metric"><div class="metric-val" style="font-size:1rem;color:{vc};">{verdict}</div><div class="metric-label">Risk Level</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="metric"><div class="metric-val" style="font-size:0.78rem;">{r.get("estimated_timeline","N/A")}</div><div class="metric-label">Timeline</div></div>', unsafe_allow_html=True)
        st.progress(prob/100)

        st.markdown('<div class="sec-head">RISK FACTORS IDENTIFIED</div>', unsafe_allow_html=True)
        for i, risk in enumerate(r.get("risks",[])):
            sev = risk.get("severity","Medium")
            sc = "#ff4d6d" if sev=="High" else "#ff9f0a" if sev=="Medium" else "#00ffa0"
            bc = "red" if sev=="High" else "orange" if sev=="Medium" else "green"
            st.markdown(f"""
            <div class="g-card" style="border-left:4px solid {sc};">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                    <div style="font-weight:700;font-size:0.93rem;font-family:'Syne',sans-serif;">{i+1}. {risk.get('factor','')}</div>
                    <span class="badge badge-{bc}">{sev} RISK</span>
                </div>
                <div style="color:var(--tx2);font-size:0.83rem;margin-bottom:8px;">{risk.get('detail','')}</div>
                <div style="color:#00ffa0;font-size:0.83rem;font-weight:500;font-family:var(--font-mono);">▶ FIX: {risk.get('fix','')}</div>
            </div>
            """, unsafe_allow_html=True)

        top = r.get("top_recommendation","")
        if top:
            st.markdown(f'<div class="g-card" style="border:1px solid rgba(0,255,160,0.25);background:rgba(0,255,160,0.04);"><div style="font-size:0.7rem;color:var(--tx3);font-family:var(--font-mono);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:8px;">// TOP PRIORITY ACTION</div><div style="color:#00ffa0;font-size:0.92rem;">{top}</div></div>', unsafe_allow_html=True)

# ── PAGE: IELTS ────────────────────────────────────────────
def page_ielts():
    H("IELTS / TOEFL PREP MODULE")
    ai = get_engine()

    tab1, tab2, tab3 = st.tabs(["🎤 Speaking Mock", "📝 Study Tips", "📊 Score Calculator"])

    with tab1:
        card("""<div style="font-family:'Syne',sans-serif;font-size:1rem;font-weight:700;color:var(--c0);margin-bottom:8px;">Speaking Mock Generator</div>
<div style="color:var(--tx2);font-size:0.85rem;">Generate realistic IELTS Speaking prompts with band scoring guidance and vocabulary tips.</div>""")
        c1,c2 = st.columns(2)
        with c1: part = st.selectbox("Speaking Part", ["Part 2 (Long Turn - 2 min)","Part 1 (Introduction)","Part 3 (Discussion)"], key="ielts_part")
        with c2: topic = st.selectbox("Topic Area", ["Random","Education","Technology","Environment","Culture","Work & Career","Health","Society","Family","Travel"], key="ielts_topic")

        if st.button("🎲 GENERATE MOCK PROMPT", use_container_width=True, key="ielts_gen"):
            with st.spinner("Generating prompt..."):
                prompt = ai.generate_ielts_prompt(part, topic)
                st.session_state.ielts_prompt = prompt
            st.rerun()

        if st.session_state.ielts_prompt:
            st.markdown(f'<div class="g-card" style="border-left:4px solid var(--c0);"><div style="white-space:pre-wrap;font-size:0.88rem;line-height:1.75;color:var(--tx1);">{st.session_state.ielts_prompt}</div></div>', unsafe_allow_html=True)
            ans = st.text_area("📝 Practice Answer:", height=140, placeholder="Write your practice response here...", key="ielts_ans")
            if ans and st.button("📊 EVALUATE ANSWER", key="ielts_eval"):
                with st.spinner("Evaluating..."):
                    ev = ai.evaluate_answer(st.session_state.ielts_prompt[:200], ans)
                total = ev.get("total",0)
                ec = "#00ffa0" if total>75 else "#ff9f0a" if total>60 else "#ff4d6d"
                st.markdown(f'<div class="metric" style="text-align:center;margin:12px 0;"><div class="metric-val" style="color:{ec};">{total}/100</div><div class="metric-label">Band Score: {ev.get("grade","N/A")}</div></div>', unsafe_allow_html=True)
                c1,c2 = st.columns(2)
                with c1:
                    for s in ev.get("strengths",[]): st.markdown(f'<div style="font-size:0.82rem;color:#00ffa0;padding:2px 0;">✅ {s}</div>', unsafe_allow_html=True)
                with c2:
                    for i in ev.get("improvements",[]): st.markdown(f'<div style="font-size:0.82rem;color:var(--c1);padding:2px 0;">→ {i}</div>', unsafe_allow_html=True)
                st.info(f"💡 {ev.get('model_answer_tip','')}")

    with tab2:
        tips_data = {
            "📖 Reading": ["Skim first for main ideas, then scan for specific answers","True/False/Not Given: 'Not Given' = info not in text","Read questions BEFORE the passage","Manage time: max 20 minutes per section"],
            "✍️ Writing Task 1": ["Always write an overview paragraph — most candidates skip this","Compare specific data points, not just describe everything","Paraphrase the question for introduction — never copy"],
            "✍️ Writing Task 2": ["State position clearly in INTRODUCTION","Each body paragraph: topic + 2 supporting points + specific example","Use connectors: Furthermore, In contrast, Consequently"],
            "👂 Listening": ["Read questions during 30-second preview time","Answers appear in ORDER in the audio","Watch for distractors: answer often comes after correction"],
        }
        for section, tips in tips_data.items():
            with st.expander(f"**{section}**"):
                for t in tips: st.markdown(f'<div style="font-size:0.83rem;color:var(--tx2);padding:3px 0;">• {t}</div>', unsafe_allow_html=True)

    with tab3:
        H("BAND SCORE ESTIMATOR")
        c1,c2,c3,c4 = st.columns(4)
        with c1: r_s = st.slider("Reading", 1.0, 9.0, 6.5, 0.5, key="ielts_r")
        with c2: w_s = st.slider("Writing", 1.0, 9.0, 6.0, 0.5, key="ielts_w")
        with c3: l_s = st.slider("Listening", 1.0, 9.0, 7.0, 0.5, key="ielts_l")
        with c4: sp_s = st.slider("Speaking", 1.0, 9.0, 6.5, 0.5, key="ielts_sp")
        overall = round((r_s+w_s+l_s+sp_s)/4*2)/2
        oc = "#ff4d6d" if overall<6.5 else "#ff9f0a" if overall<7.0 else "#00ffa0"
        verdict = "✅ Meets most scholarship requirements" if overall>=7.0 else "⚠️ Meets minimum (6.5 required)" if overall>=6.5 else "❌ Below requirements — retake needed"
        st.markdown(f'<div class="g-card" style="text-align:center;border:2px solid {oc}44;"><div style="font-size:0.7rem;color:var(--tx3);font-family:var(--font-mono);text-transform:uppercase;letter-spacing:0.12em;margin-bottom:10px;">OVERALL BAND SCORE</div><div style="font-size:4.5rem;font-weight:900;color:{oc};font-family:var(--font-mono);text-shadow:0 0 30px {oc}55;">{overall}</div><div style="color:var(--tx2);margin-top:10px;">{verdict}</div></div>', unsafe_allow_html=True)

# ── PAGE: INTERVIEW ────────────────────────────────────────
def page_interview():
    H("INTERVIEW PREP MODE")
    ai = get_engine()

    IQS = [
        "Tell me about yourself and your academic journey.",
        "Why did you choose this specific scholarship?",
        "What is your most significant academic achievement?",
        "Where do you see yourself in 10 years?",
        "How will you contribute to Pakistan after completing your studies?",
        "Describe a time you faced a significant challenge and how you overcame it.",
        "What makes you stronger than other applicants?",
        "How does this program align with your long-term career goals?",
        "Describe your leadership experience and its impact.",
        "What is your plan if you don't get this scholarship?",
        "Why did you choose this country for your studies?",
        "Tell me about a failure and what you learned from it.",
    ]

    mode = st.radio("Mode", ["🎯 Practice Single Question", "📋 Full Mock Interview (5 Questions)"], horizontal=True, key="iv_mode")

    if mode == "🎯 Practice Single Question":
        if not st.session_state.interview_q:
            st.session_state.interview_q = random.choice(IQS)

        sc_type = st.selectbox("Scholarship Style", ["General","Chevening","Fulbright","Gates Cambridge","Rhodes","DAAD"], key="iv_style")
        st.markdown(f"""
        <div class="g-card" style="border-left:4px solid var(--c2);">
            <div style="font-size:0.68rem;color:var(--tx3);font-family:var(--font-mono);text-transform:uppercase;letter-spacing:0.12em;margin-bottom:10px;">// INTERVIEW QUESTION · {sc_type.upper()}</div>
            <div style="font-size:1.08rem;font-weight:600;color:var(--tx1);line-height:1.55;font-family:'Syne',sans-serif;">"{st.session_state.interview_q}"</div>
        </div>
        """, unsafe_allow_html=True)

        answer = st.text_area("✍️ Your Answer (aim 200-280 words):", height=150, key="iv_ans")

        c1,c2 = st.columns(2)
        with c1:
            if st.button("📊 EVALUATE ANSWER", use_container_width=True, key="iv_eval") and answer:
                with st.spinner("🤖 Evaluating..."):
                    ev = ai.evaluate_answer(st.session_state.interview_q, answer)
                c1s,c2s,c3s,c4s = st.columns(4)
                for col, (lbl, sc_k) in zip([c1s,c2s,c3s,c4s],[("Clarity","clarity"),("Relevance","relevance"),("Evidence","evidence"),("Comm.","communication")]):
                    sc_v = ev.get(sc_k,0)
                    ec = "#00ffa0" if sc_v>=20 else "#ff9f0a" if sc_v>=15 else "#ff4d6d"
                    with col: st.markdown(f'<div class="metric"><div class="metric-val" style="font-size:1.6rem;color:{ec};">{sc_v}</div><div class="metric-label">{lbl}/25</div></div>', unsafe_allow_html=True)
                total = ev.get("total",0)
                tc = "#00ffa0" if total>75 else "#ff9f0a" if total>60 else "#ff4d6d"
                st.markdown(f'<div class="g-card" style="text-align:center;border-color:{tc}44;"><span style="font-size:2.2rem;font-weight:900;color:{tc};font-family:var(--font-mono);">{total}/100</span><span style="font-size:1rem;color:var(--tx2);margin-left:12px;">Grade: {ev.get("grade","N/A")}</span></div>', unsafe_allow_html=True)
                c1a,c2a = st.columns(2)
                with c1a:
                    for s in ev.get("strengths",[]): st.markdown(f'<div style="font-size:0.82rem;color:#00ffa0;padding:2px 0;">✅ {s}</div>', unsafe_allow_html=True)
                with c2a:
                    for i in ev.get("improvements",[]): st.markdown(f'<div style="font-size:0.82rem;color:var(--c1);padding:2px 0;">→ {i}</div>', unsafe_allow_html=True)
                tip = ev.get("model_answer_tip","")
                if tip: st.info(f"💡 **Pro Tip:** {tip}")
        with c2:
            if st.button("🔄 NEXT QUESTION", use_container_width=True, key="iv_next"):
                st.session_state.interview_q = random.choice(IQS); st.rerun()

    else:
        if "mock_qs" not in st.session_state:
            st.session_state.mock_qs = random.sample(IQS, 5)
            st.session_state.mock_idx = 0
            st.session_state.mock_ans = []

        idx = st.session_state.mock_idx
        qs = st.session_state.mock_qs

        if idx < len(qs):
            st.progress(idx/len(qs))
            st.caption(f"Question {idx+1} of {len(qs)}")
            st.markdown(f'<div class="g-card" style="border-left:4px solid var(--c2);"><div style="font-size:0.68rem;color:var(--tx3);font-family:var(--font-mono);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:8px;">// Q{idx+1}</div><div style="font-size:1.05rem;font-weight:600;font-family:\'Syne\',sans-serif;">"{qs[idx]}"</div></div>', unsafe_allow_html=True)
            ans = st.text_area("Your answer:", height=120, key=f"mock_a_{idx}")
            if st.button("Next →", use_container_width=True, key=f"mock_n_{idx}") and ans:
                st.session_state.mock_ans.append({"q":qs[idx],"a":ans})
                st.session_state.mock_idx += 1; st.rerun()
        else:
            st.success("🎉 Mock interview complete!")
            for i, qa in enumerate(st.session_state.mock_ans):
                with st.expander(f"Q{i+1}: {qa['q'][:60]}..."):
                    st.markdown(f"**Your Answer:** {qa['a']}")
            if st.button("🔄 Restart Interview"):
                del st.session_state.mock_qs, st.session_state.mock_idx, st.session_state.mock_ans; st.rerun()

# ── PAGE: COMPARE ──────────────────────────────────────────
def page_compare():
    H("COMPARE SCHOLARSHIPS")
    dm = get_dm()
    ai = get_engine()
    names = dm.get_all_names()
    if len(names) < 2:
        st.warning("Not enough scholarships in database."); return

    c1,c2 = st.columns(2)
    with c1: s1 = st.selectbox("Scholarship A", names, key="cmp_s1")
    with c2: s2_opts = [n for n in names if n!=s1]; s2 = st.selectbox("Scholarship B", s2_opts, key="cmp_s2")

    if st.button("⚡ COMPARE NOW", use_container_width=True, key="cmp_btn"):
        cmp = dm.compare_scholarships(s1, s2)
        if not cmp:
            st.error("Could not load comparison data."); return

        st.markdown(f'<div class="cmp-grid"><div class="cmp-lbl">Criteria</div><div class="cmp-hdr">{s1[:28]}</div><div class="cmp-hdr">{s2[:28]}</div></div>', unsafe_allow_html=True)
        for key, data in cmp.items():
            lbl = data.get("label", key).replace("_"," ").title()
            v1 = str(data.get(s1,"N/A")); v2 = str(data.get(s2,"N/A"))
            st.markdown(f'<div class="cmp-grid"><div class="cmp-lbl">{lbl}</div><div class="cmp-val">{v1}</div><div class="cmp-val">{v2}</div></div>', unsafe_allow_html=True)

        st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)
        prof = st.session_state.profile
        with st.spinner("🤖 AI analyzing best fit for your profile..."):
            ap = f"Compare {s1} vs {s2} for a student: CGPA: {prof.get('cgpa',3.0)}, IELTS: {prof.get('ielts',6.5)}, Field: {prof.get('field','General')}. Give specific recommendation: which is better match, which is more accessible, final verdict."
            analysis = ai.chat_response(ap, prof, [])
        st.markdown(f'<div class="g-card" style="border-left:4px solid var(--c2);"><div style="font-size:0.7rem;color:var(--tx3);font-family:var(--font-mono);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:10px;">// AI RECOMMENDATION FOR YOUR PROFILE</div><div style="white-space:pre-wrap;font-size:0.88rem;line-height:1.7;color:var(--tx1);">{analysis}</div></div>', unsafe_allow_html=True)

# ── PAGE: BOOKMARKS ────────────────────────────────────────
def page_bookmarks():
    H("SAVED SCHOLARSHIPS")
    bm = st.session_state.bookmarks
    dm = get_dm()

    if not bm:
        st.markdown('<div class="g-card" style="text-align:center;padding:60px;"><div style="font-size:3rem;margin-bottom:12px;filter:drop-shadow(0 0 16px rgba(0,255,224,0.4));">🔖</div><div style="font-family:\'Syne\',sans-serif;font-weight:700;font-size:1.1rem;color:var(--c0);margin-bottom:8px;">No Saved Scholarships</div><div style="color:var(--tx3);font-size:0.85rem;">Go to Scholarships and click 🔖 Save on programs you are interested in.</div></div>', unsafe_allow_html=True)
        return

    for nm in bm:
        row_df = dm.df[dm.df['name'].str.lower() == nm.lower()]
        if row_df.empty: continue
        row = row_df.iloc[0]
        badge_text, badge_color, _ = dm.get_deadline_status(row.get('deadline'))
        st.markdown(f"""
        <div class="s-card fade-up">
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
                <div>
                    <div style="font-size:1.02rem;font-weight:700;font-family:'Syne',sans-serif;">{nm}</div>
                    <div style="font-size:0.75rem;color:var(--tx3);font-family:var(--font-mono);margin-top:3px;">🌍 {row.get('country','N/A')} &nbsp;·&nbsp; 💰 {row.get('amount','N/A')} &nbsp;·&nbsp; 📊 GPA {row.get('gpa required','N/A')}+</div>
                </div>
                <span class="badge badge-{badge_color}">{badge_text}</span>
            </div>
            <div style="margin-top:8px;font-size:0.82rem;color:var(--tx2);">{str(row.get('description',''))[:200]}...</div>
        </div>
        """, unsafe_allow_html=True)
        c1,c2 = st.columns([4,1])
        with c1: st.markdown(f'<div style="font-size:0.8rem;padding:4px 0;"><a href="{row.get("url","#")}" style="color:var(--c1);" target="_blank">🔗 Official Website</a></div>', unsafe_allow_html=True)
        with c2:
            if st.button("❌ Remove", key=f"rm_bm_{nm}", use_container_width=True):
                st.session_state.bookmarks.remove(nm); st.rerun()

    if st.button("📥 EXPORT ALL BOOKMARKS PDF", use_container_width=True, key="bm_pdf_btn"):
        secs = []
        for nm in bm:
            row_df = dm.df[dm.df['name'].str.lower()==nm.lower()]
            if not row_df.empty:
                r = row_df.iloc[0]
                secs.append({"heading":nm,"body":f"Country: {r.get('country','N/A')}\nAmount: {r.get('amount','N/A')}\nGPA: {r.get('gpa required','N/A')}+\nLanguage: {r.get('language requirement','N/A')}\nURL: {r.get('url','N/A')}"})
        pdf = dm.export_to_pdf("My Bookmarked Scholarships", secs)
        st.download_button("⬇️ Download PDF", pdf, "bookmarks.pdf", "application/pdf", key="bm_dl")

# ── PAGE: SETTINGS ─────────────────────────────────────────
def page_settings():
    H("SETTINGS & CONFIGURATION")
    tab1, tab2, tab3 = st.tabs(["🔑 API Keys", "👤 Profile", "ℹ️ About"])

    with tab1:
        card("""<div style="font-family:'Syne',sans-serif;font-size:1rem;font-weight:700;color:var(--c0);margin-bottom:8px;">🔑 API Key Configuration</div>
<div style="color:var(--tx2);font-size:0.85rem;">Add your Groq API key to enable full AI + RAG features. Free key from console.groq.com — takes 30 seconds.</div>""")

        ai = get_engine()
        if ai.groq_key:
            st.markdown('<div class="g-card" style="border-color:rgba(0,255,160,0.3);background:rgba(0,255,160,0.04);padding:12px 16px;"><span class="status-dot online"></span><span style="font-size:0.82rem;color:#00ffa0;font-family:var(--font-mono);">GROQ API KEY ACTIVE — AI FEATURES FULLY ENABLED</span></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="g-card" style="border-color:rgba(255,140,0,0.3);background:rgba(255,140,0,0.04);padding:12px 16px;"><span class="status-dot warn"></span><span style="font-size:0.82rem;color:#ff9f0a;font-family:var(--font-mono);">NO API KEY — Add below OR add to Streamlit Secrets as GROQ_API_KEY</span></div>', unsafe_allow_html=True)

        gk = st.text_input("🟢 Groq API Key (FREE - Recommended)", value=st.session_state.api_keys.get("groq",""), type="password", help="Get free key at console.groq.com")
        st.markdown('<div style="font-size:0.75rem;color:var(--tx3);margin-top:4px;font-family:var(--font-mono);">→ console.groq.com → Sign Up → API Keys → Create API Key (starts with gsk_)</div>', unsafe_allow_html=True)

        mk = st.text_input("🔵 Gemini 1.5 Pro Key (Optional)", value=st.session_state.api_keys.get("gemini",""), type="password")

        if st.button("💾 SAVE API KEYS", use_container_width=True, key="save_keys"):
            st.session_state.api_keys["groq"] = gk
            st.session_state.api_keys["gemini"] = mk
            st.success("✅ API keys saved! AI features reloaded.")

        H("STREAMLIT CLOUD DEPLOYMENT")
        st.markdown("""
        <div class="terminal">
            <div class="terminal-body">
                <span style="color:var(--tx3);"># For Streamlit Cloud — Add to Secrets:</span><br>
                <span style="color:var(--c0);">GROQ_API_KEY</span> = <span style="color:#ff9f0a;">"gsk_your_key_here"</span><br>
                <span style="color:var(--tx3);"># share.streamlit.io → App → Settings → Secrets</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        H("MODEL STATUS")
        ak = ai.groq_key; mk2 = ai.gemini_key
        rag = get_rag()
        c1,c2,c3 = st.columns(3)
        with c1: st.markdown(f'<div class="metric"><div style="font-size:1.6rem;margin-bottom:6px;">🟢</div><div class="metric-val" style="font-size:1rem;color:{"#00ffa0" if ak else "#ff9f0a"};">{"ACTIVE" if ak else "FALLBACK"}</div><div class="metric-label">Groq Llama3-70B</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="metric"><div style="font-size:1.6rem;margin-bottom:6px;">🔵</div><div class="metric-val" style="font-size:1rem;color:{"#00ffa0" if mk2 else "#6b7280"};">{"ACTIVE" if mk2 else "NOT SET"}</div><div class="metric-label">Gemini 1.5 Pro</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="metric"><div style="font-size:1.6rem;margin-bottom:6px;">🔍</div><div class="metric-val" style="font-size:1rem;color:#00ffa0;">{"ACTIVE" if rag.is_built else "BUILDING"}</div><div class="metric-label">RAG ({len(rag.documents)} docs)</div></div>', unsafe_allow_html=True)

    with tab2:
        p = st.session_state.profile
        c1,c2 = st.columns(2)
        with c1:
            nm = st.text_input("Full Name", p.get("name",""), key="st_name")
            cgpa = st.number_input("CGPA", 0.0, 4.0, float(p.get("cgpa",3.0)), 0.1, key="st_cgpa")
            fld = st.selectbox("Field", ["","Computer Science","Engineering","Business","Biology","Medicine","Arts","Economics","Law","Education","Psychology","Agriculture"], key="st_field")
        with c2:
            ielts = st.number_input("IELTS", 0.0, 9.0, float(p.get("ielts",6.5)), 0.5, key="st_ielts")
            country = st.selectbox("Target Country", ["","USA","UK","Germany","Australia","Canada","Japan","South Korea","Sweden","China","Netherlands","Hungary"], key="st_country")
            year = st.selectbox("Year", ["1st Year","2nd Year","3rd Year","4th Year","Graduate","Working Professional"], key="st_year")
        r2 = st.selectbox("Research Experience", ["none","minimal","coursework projects","conference paper","published paper","multiple publications"], key="st_res")
        l2 = st.selectbox("Leadership Experience", ["none","minimal","club member","club officer","founded organization","professional role"], key="st_lead")
        if st.button("💾 UPDATE PROFILE", use_container_width=True, key="st_save"):
            st.session_state.profile.update({"name":nm,"cgpa":cgpa,"field":fld,"year":year,"ielts":ielts,"country":country,"research":r2,"leadership":l2})
            st.success("✅ Profile updated!"); st.rerun()

    with tab3:
        st.markdown("""
        <div class="g-card">
            <div style="font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:800;background:linear-gradient(135deg,var(--c0),var(--c1));-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:14px;">ScholarAI Elite v4.0</div>
            <div style="color:var(--tx2);font-size:0.88rem;line-height:1.7;margin-bottom:16px;">Enterprise-grade AI scholarship intelligence platform with RAG for Pakistani students targeting international scholarships.</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="sec-head">TECH STACK</div>', unsafe_allow_html=True)
        stack = [
            ("🤖 Groq Llama3-70B", "Primary AI — Chat, SOP, Interview, Rejection, Roadmap"),
            ("🔍 RAG Engine", "TF-IDF semantic search over 16 verified 2026 scholarships"),
            ("🔵 Gemini 1.5 Pro", "Optional — PDF processing, vision, complex reasoning"),
            ("📊 Local Fallback", "Profile-based logic when APIs unavailable"),
        ]
        for name_s, desc_s in stack:
            st.markdown(f'<div class="g-card" style="padding:12px 16px;margin:4px 0;display:flex;gap:10px;align-items:center;"><div style="font-weight:600;font-size:0.88rem;color:var(--c0);min-width:180px;font-family:var(--font-mono);">{name_s}</div><div style="font-size:0.82rem;color:var(--tx2);">{desc_s}</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="sec-head">INSTALL DEPENDENCIES</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="terminal">
            <div class="terminal-body">
                pip install streamlit groq google-generativeai pandas fpdf2 pdfplumber
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── MAIN ───────────────────────────────────────────────────
def main():
    init_ss()
    apply_css()

    if not st.session_state.logged_in:
        page_login()
        return

    render_sidebar()

    pages = {
        "Dashboard": page_dashboard,
        "Scholarships": page_scholarships,
        "AI Chat": page_ai_chat,
        "CV Analyzer": page_cv,
        "SOP Improve": page_sop,
        "Roadmap": page_roadmap,
        "Rejection Sim": page_rejection,
        "IELTS Prep": page_ielts,
        "Interview Prep": page_interview,
        "Compare": page_compare,
        "Bookmarks": page_bookmarks,
        "Settings": page_settings,
    }
    pages.get(st.session_state.page, page_dashboard)()


if __name__ == "__main__":
    main()
