"""
ScholarAI Elite v3 — Complete Application
Login/Signup | Cyberpunk UI | All Features Fixed
"""

import os, sys, json, time, random, datetime, hashlib
import streamlit as st
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils.ai_engine import AIEngine
from utils.data_manager import DataManager, extract_text_from_pdf

# ── Page Config ─────────────────────────────────────────
st.set_page_config(page_title="ScholarAI Elite", page_icon="🎓", layout="wide", initial_sidebar_state="expanded")

# ── Users DB (session-based, replace with real DB in production) ─
DEMO_USERS = {
    "demo": {"password": hashlib.sha256("demo123".encode()).hexdigest(), "name": "Demo Student", "email": "demo@scholarai.com"},
}

def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

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

# ── CSS ──────────────────────────────────────────────────
def apply_css(dark: bool):
    if dark:
        bg        = "#050a14"
        bg2       = "#0a1628"
        bg3       = "#0f1f3d"
        glass     = "rgba(0,240,255,0.03)"
        gborder   = "rgba(0,240,255,0.12)"
        tx1       = "#e0f4ff"
        tx2       = "#7bafc4"
        acc       = "#00f0ff"
        acc2      = "#7b2fff"
        acc3      = "#ff2d78"
        glow      = "rgba(0,240,255,0.15)"
        card_sh   = "rgba(0,0,0,0.6)"
        grid_c    = "rgba(0,240,255,0.04)"
        input_bg  = "rgba(0,240,255,0.05)"
        btn_txt   = "#000"
    else:
        bg        = "#f0f6ff"
        bg2       = "#ffffff"
        bg3       = "#e8f0fe"
        glass     = "rgba(37,99,235,0.05)"
        gborder   = "rgba(37,99,235,0.18)"
        tx1       = "#0f172a"
        tx2       = "#334155"
        acc       = "#2563eb"
        acc2      = "#7c3aed"
        acc3      = "#e11d48"
        glow      = "rgba(37,99,235,0.12)"
        card_sh   = "rgba(37,99,235,0.10)"
        grid_c    = "rgba(37,99,235,0.04)"
        input_bg  = "rgba(37,99,235,0.04)"
        btn_txt   = "#ffffff"

    st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Share+Tech+Mono&family=Inter:wght@300;400;500;600;700&display=swap');

:root{{--acc:{acc};--acc2:{acc2};--acc3:{acc3};--tx1:{tx1};--tx2:{tx2};--bg:{bg};--bg2:{bg2};--bg3:{bg3};--glass:{glass};--gborder:{gborder};--glow:{glow};--card_sh:{card_sh};--grid_c:{grid_c};--input_bg:{input_bg};--btn_txt:{btn_txt};}}

html,body,.stApp{{background:{bg}!important;font-family:'Inter',sans-serif;color:{tx1};}}
#MainMenu,footer,header,.stDeployButton{{display:none!important;visibility:hidden!important;}}

/* Grid background */
.stApp::before{{content:'';position:fixed;top:0;left:0;width:100%;height:100%;background-image:linear-gradient({grid_c} 1px,transparent 1px),linear-gradient(90deg,{grid_c} 1px,transparent 1px);background-size:40px 40px;pointer-events:none;z-index:0;}}

/* Sidebar */
[data-testid="stSidebar"]{{background:{bg2}!important;border-right:1px solid {gborder};box-shadow:4px 0 20px {glow};}}
[data-testid="stSidebar"] *{{color:{tx1}!important;}}
[data-testid="stSidebar"] .stButton>button{{background:transparent!important;color:{tx2}!important;border:1px solid {gborder}!important;border-radius:8px!important;font-family:'Inter',sans-serif!important;font-weight:500!important;font-size:0.87rem!important;padding:8px 12px!important;text-align:left!important;transition:all 0.2s!important;margin:2px 0!important;}}
[data-testid="stSidebar"] .stButton>button:hover{{background:{glass}!important;border-color:{acc}!important;color:{acc}!important;box-shadow:0 0 12px {glow}!important;}}

/* Main buttons */
.stButton>button{{background:linear-gradient(135deg,{acc},{acc2})!important;color:{btn_txt}!important;border:none!important;border-radius:8px!important;font-family:'Inter',sans-serif!important;font-weight:600!important;padding:8px 20px!important;transition:all 0.2s!important;position:relative;overflow:hidden;}}
.stButton>button:hover{{opacity:0.88!important;transform:translateY(-1px)!important;box-shadow:0 4px 20px {glow}!important;}}

/* Inputs */
.stTextInput>div>div>input,.stTextArea>div>div>textarea,.stNumberInput>div>div>input{{background:{input_bg}!important;border:1px solid {gborder}!important;border-radius:8px!important;color:{tx1}!important;font-family:'Inter',sans-serif!important;}}
.stTextInput>div>div>input:focus,.stTextArea>div>div>textarea:focus{{border-color:{acc}!important;box-shadow:0 0 0 2px {glow}!important;}}
.stSelectbox>div>div{{background:{input_bg}!important;border:1px solid {gborder}!important;border-radius:8px!important;color:{tx1}!important;}}
label,.stTextInput label,.stSelectbox label,.stNumberInput label,.stTextArea label,.stSlider label{{color:{tx2}!important;font-size:0.85rem!important;font-weight:500!important;}}

/* Progress bar */
.stProgress>div>div>div>div{{background:linear-gradient(90deg,{acc},{acc2})!important;border-radius:10px;box-shadow:0 0 8px {glow};}}

/* Tabs */
.stTabs [data-baseweb="tab-list"]{{background:{bg2};border-radius:10px;padding:4px;border:1px solid {gborder};}}
.stTabs [data-baseweb="tab"]{{border-radius:7px;color:{tx2};font-family:'Inter',sans-serif;font-weight:500;}}
.stTabs [aria-selected="true"]{{background:linear-gradient(135deg,{acc},{acc2})!important;color:{btn_txt}!important;}}

/* Scrollbar */
::-webkit-scrollbar{{width:5px;}}
::-webkit-scrollbar-track{{background:{bg};}}
::-webkit-scrollbar-thumb{{background:{acc}66;border-radius:3px;}}

/* Expander */
.streamlit-expanderHeader{{background:{glass}!important;border:1px solid {gborder}!important;border-radius:8px!important;color:{tx1}!important;}}

/* Radio */
.stRadio>div>label{{color:{tx2}!important;}}

/* Checkbox */
.stCheckbox>label{{color:{tx1}!important;}}

/* Caption */
.stCaption,.caption{{color:{tx2}!important;font-size:0.8rem!important;}}

/* Alerts */
.stSuccess>div{{background:rgba(16,185,129,0.1)!important;border:1px solid rgba(16,185,129,0.3)!important;color:{tx1}!important;border-radius:8px!important;}}
.stError>div{{background:rgba(239,68,68,0.1)!important;border:1px solid rgba(239,68,68,0.3)!important;color:{tx1}!important;border-radius:8px!important;}}
.stWarning>div{{background:rgba(245,158,11,0.1)!important;border:1px solid rgba(245,158,11,0.3)!important;color:{tx1}!important;border-radius:8px!important;}}
.stInfo>div{{background:rgba(59,130,246,0.1)!important;border:1px solid rgba(59,130,246,0.3)!important;color:{tx1}!important;border-radius:8px!important;}}

/* Animation */
@keyframes fadeUp{{from{{opacity:0;transform:translateY(16px)}}to{{opacity:1;transform:translateY(0)}}}}
@keyframes glowPulse{{0%,100%{{box-shadow:0 0 8px {glow}}}50%{{box-shadow:0 0 24px {glow},0 0 48px {glow}}}}}
@keyframes scanLine{{0%{{top:-100%}}100%{{top:100%}}}}
.fade-up{{animation:fadeUp 0.4s ease forwards;}}

/* Glass card */
.g-card{{background:{glass};border:1px solid {gborder};border-radius:14px;padding:22px;margin:10px 0;backdrop-filter:blur(12px);box-shadow:0 4px 24px {card_sh};transition:all 0.25s;position:relative;overflow:hidden;}}
.g-card:hover{{border-color:{acc}66;box-shadow:0 6px 32px {card_sh},0 0 0 1px {acc}22;transform:translateY(-2px);}}
.g-card::before{{content:'';position:absolute;top:0;left:0;width:100%;height:1px;background:linear-gradient(90deg,transparent,{acc}44,transparent);}}

/* Scholar card */
.s-card{{background:{glass};border:1px solid {gborder};border-radius:16px;padding:18px 20px;margin:8px 0;backdrop-filter:blur(10px);position:relative;overflow:hidden;transition:all 0.2s;}}
.s-card::before{{content:'';position:absolute;left:0;top:0;width:3px;height:100%;background:linear-gradient(180deg,{acc},{acc2});}}
.s-card:hover{{border-color:{acc}55;transform:translateX(3px);}}

/* Metric */
.metric{{background:{glass};border:1px solid {gborder};border-radius:12px;padding:16px 20px;text-align:center;backdrop-filter:blur(8px);}}
.metric-val{{font-size:2rem;font-weight:700;color:{acc};font-family:'Orbitron',monospace;line-height:1;}}
.metric-label{{font-size:0.72rem;color:{tx2};text-transform:uppercase;letter-spacing:0.1em;margin-top:4px;}}

/* Hero */
.hero{{background:linear-gradient(135deg,{acc}11,{acc2}11,{acc3}08);border:1px solid {gborder};border-radius:20px;padding:40px;text-align:center;position:relative;overflow:hidden;margin-bottom:24px;}}
.hero::after{{content:'';position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:400px;height:400px;background:radial-gradient(circle,{acc}08 0%,transparent 70%);pointer-events:none;}}
.hero-title{{font-family:'Orbitron',monospace;font-size:2.8rem;font-weight:900;background:linear-gradient(135deg,{acc},{acc2},{acc3});-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin:0;letter-spacing:0.02em;}}
.hero-sub{{color:{tx2};font-size:1rem;margin-top:10px;font-family:'Inter',sans-serif;}}
.hero-tag{{display:inline-block;background:{glass};border:1px solid {gborder};border-radius:20px;padding:4px 14px;font-size:0.78rem;color:{acc};font-family:'Share Tech Mono',monospace;margin-top:12px;letter-spacing:0.05em;}}

/* Section header */
.sec-head{{font-family:'Orbitron',monospace;font-size:1.2rem;font-weight:700;color:{acc};margin:20px 0 14px;display:flex;align-items:center;gap:10px;letter-spacing:0.05em;}}
.sec-head::after{{content:'';flex:1;height:1px;background:linear-gradient(90deg,{acc}55,transparent);margin-left:10px;}}

/* Badges */
.badge-red{{display:inline-block;background:rgba(239,68,68,0.15);border:1px solid rgba(239,68,68,0.4);color:#ef4444;font-size:0.7rem;font-weight:600;padding:3px 10px;border-radius:20px;letter-spacing:0.04em;}}
.badge-orange{{display:inline-block;background:rgba(245,158,11,0.15);border:1px solid rgba(245,158,11,0.4);color:#f59e0b;font-size:0.7rem;font-weight:600;padding:3px 10px;border-radius:20px;letter-spacing:0.04em;}}
.badge-green{{display:inline-block;background:rgba(16,185,129,0.15);border:1px solid rgba(16,185,129,0.4);color:#10b981;font-size:0.7rem;font-weight:600;padding:3px 10px;border-radius:20px;letter-spacing:0.04em;}}
.badge-blue{{display:inline-block;background:rgba(59,130,246,0.15);border:1px solid rgba(59,130,246,0.4);color:#3b82f6;font-size:0.7rem;font-weight:600;padding:3px 10px;border-radius:20px;letter-spacing:0.04em;}}
.badge-gray{{display:inline-block;background:rgba(107,114,128,0.15);border:1px solid rgba(107,114,128,0.4);color:#6b7280;font-size:0.7rem;font-weight:600;padding:3px 10px;border-radius:20px;letter-spacing:0.04em;}}

/* Chat */
.chat-user{{background:linear-gradient(135deg,{acc}15,{acc}08);border:1px solid {acc}33;border-radius:14px 14px 4px 14px;padding:12px 16px;margin:6px 0;margin-left:60px;font-size:0.93rem;color:{tx1};}}
.chat-ai{{background:{glass};border:1px solid {gborder};border-radius:14px 14px 14px 4px;padding:12px 16px;margin:6px 0;margin-right:60px;font-size:0.93rem;color:{tx1};white-space:pre-wrap;line-height:1.65;}}

/* Stepper */
.step-item{{display:flex;align-items:flex-start;margin:6px 0;padding:14px 16px;background:{glass};border:1px solid {gborder};border-radius:10px;}}
.step-num{{width:30px;height:30px;background:linear-gradient(135deg,{acc},{acc2});border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:0.8rem;color:#000;flex-shrink:0;margin-right:12px;margin-top:2px;font-family:'Orbitron',monospace;}}
.step-title{{font-weight:600;font-size:0.92rem;color:{tx1};}}
.step-detail{{font-size:0.8rem;color:{tx2};margin-top:3px;}}

/* Code mono */
.mono{{font-family:'Share Tech Mono',monospace;color:{acc};font-size:0.88rem;}}

/* Login page */
.login-wrap{{max-width:420px;margin:60px auto;}}
.login-logo{{text-align:center;margin-bottom:30px;}}
.login-logo .title{{font-family:'Orbitron',monospace;font-size:2rem;font-weight:900;background:linear-gradient(135deg,{acc},{acc2});-webkit-background-clip:text;-webkit-text-fill-color:transparent;}}
.login-logo .sub{{color:{tx2};font-size:0.85rem;margin-top:4px;}}

/* Nav active button */
.nav-active .stButton>button{{background:linear-gradient(135deg,{acc},{acc2})!important;color:#000!important;box-shadow:0 0 16px {glow}!important;}}

/* Compare table */
.cmp-grid{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;margin:4px 0;}}
.cmp-lbl{{font-size:0.78rem;font-weight:600;color:{tx2};text-transform:uppercase;letter-spacing:0.06em;padding:8px 10px;}}
.cmp-val{{font-size:0.88rem;color:{tx1};padding:8px 10px;background:{glass};border:1px solid {gborder};border-radius:7px;}}
.cmp-hdr{{font-size:0.88rem;font-weight:700;color:{acc};padding:8px 10px;background:{glass};border:1px solid {acc}44;border-radius:7px;font-family:'Orbitron',monospace;}}
</style>""", unsafe_allow_html=True)

# ── Session Init ────────────────────────────────────────
def init_ss():
    defaults = {
        "dark_mode": True, "page": "Dashboard", "logged_in": False,
        "username": "", "display_name": "",
        "chat_history": [], "bookmarks": [], "interview_q": None,
        "interview_history": [], "cv_result": None, "sop_result": None,
        "rejection_result": None, "roadmap_text": None, "ielts_prompt": None,
        "api_keys": {"groq": "", "gemini": ""},
        "profile": {"name":"","cgpa":3.0,"field":"","year":"3rd Year","country":"","ielts":6.5,"research":"none","leadership":"none"},
        "checklist": {"Transcripts Ordered":False,"IELTS Registered":False,"3 Referees Contacted":False,
                      "SOP First Draft":False,"CV Updated":False,"Financial Docs Ready":False,
                      "Personal Statement Done":False,"Research Proposal":False},
        "users_db": DEMO_USERS.copy(),
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# ── Engine factory ───────────────────────────────────────
@st.cache_resource(show_spinner=False)
def get_engine(gk: str, mk: str) -> AIEngine:
    return AIEngine(groq_key=gk, gemini_key=mk)

@st.cache_resource(show_spinner=False)
def get_dm() -> DataManager:
    base = os.path.dirname(os.path.abspath(__file__))
    return DataManager(os.path.join(base, "data", "scholarships.csv"))

# ── LOGIN PAGE ───────────────────────────────────────────
def page_login():
    apply_css(st.session_state.dark_mode)

    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        st.markdown("""
        <div class="login-logo fade-up">
            <div style="font-size:3rem;margin-bottom:8px;">🎓</div>
            <div class="title">ScholarAI Elite</div>
            <div class="sub">AI-Powered International Scholarship Intelligence</div>
        </div>
        """, unsafe_allow_html=True)

        tab_login, tab_signup = st.tabs(["🔑 Login", "✨ Create Account"])

        with tab_login:
            st.markdown('<div class="g-card fade-up">', unsafe_allow_html=True)
            st.markdown("**Welcome back!** Login to your account")
            st.markdown("</div>", unsafe_allow_html=True)

            uname = st.text_input("Username", placeholder="Enter username", key="li_user")
            pwd = st.text_input("Password", type="password", placeholder="Enter password", key="li_pwd")

            if st.button("🚀 Login", use_container_width=True, key="login_btn"):
                if uname and pwd:
                    ok, result = login_user(uname, pwd)
                    if ok:
                        st.session_state.logged_in = True
                        st.session_state.username = uname
                        st.session_state.display_name = result
                        st.session_state.profile["name"] = result
                        st.success(f"Welcome back, {result}! 🎉")
                        time.sleep(0.8)
                        st.rerun()
                    else:
                        st.error(f"❌ {result}")
                else:
                    st.warning("Please enter username and password")

            st.markdown("---")
            st.caption("**Demo Account:** username: `demo` | password: `demo123`")

        with tab_signup:
            st.markdown('<div class="g-card fade-up">', unsafe_allow_html=True)
            st.markdown("**Join ScholarAI Elite** — Start your scholarship journey")
            st.markdown("</div>", unsafe_allow_html=True)

            s_name = st.text_input("Full Name", placeholder="Your full name", key="su_name")
            s_email = st.text_input("Email", placeholder="your@email.com", key="su_email")
            s_user = st.text_input("Username", placeholder="Choose a username", key="su_user")
            s_pwd = st.text_input("Password", type="password", placeholder="Min 6 characters", key="su_pwd")
            s_pwd2 = st.text_input("Confirm Password", type="password", placeholder="Repeat password", key="su_pwd2")

            if st.button("✨ Create Account", use_container_width=True, key="signup_btn"):
                if not all([s_name, s_email, s_user, s_pwd]):
                    st.warning("Please fill all fields")
                elif len(s_pwd) < 6:
                    st.error("Password must be at least 6 characters")
                elif s_pwd != s_pwd2:
                    st.error("Passwords don't match")
                else:
                    ok, msg = register_user(s_user, s_pwd, s_name, s_email)
                    if ok:
                        st.success("✅ Account created! Please login.")
                    else:
                        st.error(f"❌ {msg}")

        # Theme toggle on login page
        st.markdown("<br>", unsafe_allow_html=True)
        dark = st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode, key="login_theme")
        if dark != st.session_state.dark_mode:
            st.session_state.dark_mode = dark
            st.rerun()

# ── SIDEBAR ──────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        # Logo
        st.markdown(f"""
        <div style="text-align:center;padding:10px 0 16px;">
            <div style="font-size:2rem;margin-bottom:4px;">🎓</div>
            <div style="font-family:'Orbitron',monospace;font-size:1rem;font-weight:700;background:linear-gradient(135deg,var(--acc),var(--acc2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;">SCHOLARAI ELITE</div>
            <div style="font-size:0.7rem;color:var(--tx2);margin-top:2px;letter-spacing:0.1em;">AI SCHOLARSHIP INTELLIGENCE</div>
        </div>
        """, unsafe_allow_html=True)

        # User info
        st.markdown(f"""
        <div class="g-card" style="padding:12px 16px;margin:4px 0 12px;">
            <div style="font-size:0.78rem;color:var(--tx2);">Logged in as</div>
            <div style="font-weight:600;font-size:0.95rem;color:var(--acc);">👤 {st.session_state.display_name}</div>
        </div>
        """, unsafe_allow_html=True)

        # Theme toggle
        c1, c2 = st.columns([2, 1])
        with c1: st.caption("Interface Mode")
        with c2:
            dark = st.toggle("🌙", value=st.session_state.dark_mode, key="sb_theme")
            if dark != st.session_state.dark_mode:
                st.session_state.dark_mode = dark
                st.rerun()

        st.markdown("---")

        # Navigation
        pages = [
            ("🏠", "Dashboard"), ("🔍", "Scholarships"), ("🤖", "AI Chat"),
            ("📄", "CV Analyzer"), ("✍️", "SOP Improve"), ("🗺️", "Roadmap"),
            ("⚠️", "Rejection Sim"), ("🎤", "IELTS Prep"), ("🎯", "Interview Prep"),
            ("📊", "Compare"), ("🔖", "Bookmarks"), ("⚙️", "Settings"),
        ]
        current = st.session_state.page
        for icon, label in pages:
            is_active = current == label
            btn_key = f"nav_{label}"
            if is_active:
                st.markdown(f"""<div style="background:linear-gradient(135deg,var(--acc)22,var(--acc2)22);border:1px solid var(--acc)44;border-radius:8px;padding:8px 12px;margin:2px 0;font-size:0.87rem;font-weight:600;color:var(--acc);">{icon} {label}</div>""", unsafe_allow_html=True)
            else:
                if st.button(f"{icon}  {label}", key=btn_key, use_container_width=True):
                    st.session_state.page = label
                    st.rerun()

        st.markdown("---")

        # Profile strength
        dm = get_dm()
        ps = dm.calculate_profile_strength(st.session_state.profile)
        sc = ps.get("score", 0)
        st.markdown(f"**Profile:** {ps.get('strength','🔴 Weak')}")
        st.progress(sc / 100)
        st.caption(f"{sc}% complete")

        st.markdown("---")
        st.caption(f"🔖 {len(st.session_state.bookmarks)} bookmarked")

        if st.button("🚪 Logout", use_container_width=True, key="logout_btn", type="secondary"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.display_name = ""
            st.rerun()

# ── Helpers ──────────────────────────────────────────────
def engine():
    gk = st.session_state.api_keys.get("groq","")
    mk = st.session_state.api_keys.get("gemini","")
    return get_engine(gk, mk)

def H(text):
    st.markdown(f'<div class="sec-head">{text}</div>', unsafe_allow_html=True)

def card(content):
    st.markdown(f'<div class="g-card fade-up">{content}</div>', unsafe_allow_html=True)

# ── PAGE: DASHBOARD ──────────────────────────────────────
def page_dashboard():
    dm = get_dm()
    name = st.session_state.display_name

    st.markdown(f"""
    <div class="hero fade-up">
        <div class="hero-title">ScholarAI Elite</div>
        <div class="hero-sub">Welcome back, <strong>{name}</strong> — Your AI scholarship advisor is ready</div>
        <div class="hero-tag">⚡ Groq Llama3 + Gemini 1.5 Pro + Advanced Analytics</div>
    </div>
    """, unsafe_allow_html=True)

    # Profile quick setup
    if not st.session_state.profile.get("field"):
        st.info("⚡ Complete your profile for personalized AI recommendations!")

    with st.expander("⚡ Quick Profile Setup", expanded=not st.session_state.profile.get("field")):
        c1, c2, c3 = st.columns(3)
        with c1:
            nm = st.text_input("Name", value=st.session_state.profile.get("name",""), key="dp_name")
            cgpa = st.number_input("CGPA (0-4.0)", 0.0, 4.0, float(st.session_state.profile.get("cgpa",3.0)), 0.1, key="dp_cgpa")
        with c2:
            field = st.selectbox("Field of Study", ["","Computer Science","Engineering","Business","Biology","Medicine","Arts","Economics","Law","Education","Psychology","Agriculture"], key="dp_field", index=0)
            year = st.selectbox("Current Year", ["1st Year","2nd Year","3rd Year","4th Year","Graduate","Working Professional"], key="dp_year")
        with c3:
            ielts = st.number_input("IELTS Score", 0.0, 9.0, float(st.session_state.profile.get("ielts",6.5)), 0.5, key="dp_ielts")
            country = st.selectbox("Target Country", ["","USA","UK","Germany","Australia","Canada","Japan","South Korea","Sweden","China","Netherlands","Hungary"], key="dp_country")
        c4, c5 = st.columns(2)
        with c4: research = st.selectbox("Research Experience", ["none","minimal","coursework projects","conference paper","published paper","multiple publications"], key="dp_res")
        with c5: leadership = st.selectbox("Leadership Experience", ["none","minimal","club member","club officer","founded organization","professional role"], key="dp_lead")

        if st.button("💾 Save Profile", use_container_width=True, key="dp_save"):
            st.session_state.profile.update({"name":nm or st.session_state.display_name,"cgpa":cgpa,"field":field,"year":year,"ielts":ielts,"country":country,"research":research,"leadership":leadership})
            st.success("✅ Profile saved! AI recommendations are now personalized.")
            st.rerun()

    # Metrics
    total = len(dm.df)
    now = pd.Timestamp.now()
    try: upcoming = int((dm.df['deadline'] > now).sum())
    except: upcoming = total
    ps = dm.calculate_profile_strength(st.session_state.profile)

    cols = st.columns(4)
    for col, (val, label, icon) in zip(cols, [
        (str(total), "Scholarships", "🏆"),
        (str(upcoming), "Open Deadlines", "📅"),
        (str(len(st.session_state.bookmarks)), "Bookmarked", "🔖"),
        (f"{ps.get('score',0)}%", "Profile Strength", "💪"),
    ]):
        with col:
            st.markdown(f'<div class="metric fade-up"><div style="font-size:1.3rem;margin-bottom:4px;">{icon}</div><div class="metric-val">{val}</div><div class="metric-label">{label}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Quick access grid
    H("🚀 Quick Access")
    features = [
        ("🤖 AI Chat", "Scholarship advisor chatbot", "AI Chat"),
        ("📄 CV Analyzer", "ATS score + improvements", "CV Analyzer"),
        ("✍️ SOP Improve", "High-impact SOP rewrite", "SOP Improve"),
        ("🗺️ Roadmap", "12-month personalized plan", "Roadmap"),
        ("⚠️ Rejection Sim", "Find your risk factors", "Rejection Sim"),
        ("🎤 IELTS Prep", "Mock prompts + tips", "IELTS Prep"),
        ("🎯 Interview Prep", "AI-scored Q&A practice", "Interview Prep"),
        ("📊 Compare", "Side-by-side comparison", "Compare"),
    ]
    for row in range(0, len(features), 4):
        cols = st.columns(4)
        for i, (title, desc, pg) in enumerate(features[row:row+4]):
            with cols[i]:
                icon = title.split()[0]
                st.markdown(f'<div class="g-card" style="min-height:90px;cursor:pointer;"><div style="font-weight:700;margin-bottom:6px;">{title}</div><div style="font-size:0.78rem;color:var(--tx2);">{desc}</div></div>', unsafe_allow_html=True)
                if st.button("Open →", key=f"qa_{pg}", use_container_width=True):
                    st.session_state.page = pg
                    st.rerun()

    # Application Checklist
    H("✅ Application Checklist")
    items = list(st.session_state.checklist.items())
    c1, c2 = st.columns(2)
    for i, (item, done) in enumerate(items):
        with (c1 if i < len(items)//2 else c2):
            new = st.checkbox(item, value=done, key=f"chk_{item}")
            st.session_state.checklist[item] = new
    done_n = sum(v for v in st.session_state.checklist.values())
    st.progress(done_n / len(st.session_state.checklist))
    st.caption(f"📋 {done_n}/{len(st.session_state.checklist)} tasks completed")

    # Timeline
    H("📅 Scholarship Success Timeline")
    steps = [
        ("Research & Target", "Identify 5-8 scholarships, research requirements, create tracking spreadsheet", "Month 1-2"),
        ("Profile Enhancement", "Strengthen CGPA, get IELTS 7+, join research projects, document leadership", "Month 3-5"),
        ("Document Preparation", "SOP, updated CV, official transcripts, reference letter briefs", "Month 6-7"),
        ("Application Submission", "Submit all applications before deadlines with proofread documents", "Month 8-10"),
        ("Interview Preparation", "Practice 20+ questions, research committees, prepare examples", "Month 10-11"),
        ("Decision & Acceptance", "Receive offers, compare terms, prepare for relocation", "Month 12"),
    ]
    colors = ["#00f0ff","#7b2fff","#ff2d78","#10b981","#f59e0b","#3b82f6"]
    for i, (title, detail, timing) in enumerate(steps):
        st.markdown(f'<div class="step-item fade-up"><div class="step-num" style="background:{colors[i]};">{i+1}</div><div class="step-content"><div class="step-title">{title} <span style="font-size:0.72rem;color:var(--tx2);font-weight:400;margin-left:8px;">📅 {timing}</span></div><div class="step-detail">{detail}</div></div></div>', unsafe_allow_html=True)

# ── PAGE: SCHOLARSHIPS ───────────────────────────────────
def page_scholarships():
    H("🔍 Scholarship Database — 2026 Verified")
    dm = get_dm()

    with st.expander("🔧 Filters", expanded=True):
        c1,c2,c3,c4,c5 = st.columns(5)
        with c1: ctry = st.selectbox("Country", dm.get_countries(), key="f_ctry")
        with c2: fld = st.selectbox("Field", dm.get_fields(), key="f_fld")
        with c3: deg = st.selectbox("Degree", dm.get_degrees(), key="f_deg")
        with c4: gpa = st.slider("My CGPA", 0.0, 4.0, float(st.session_state.profile.get("cgpa",3.0)), 0.1, key="f_gpa")
        with c5: srch = st.text_input("Search", placeholder="keyword...", key="f_srch")

    filtered = dm.filter_scholarships(ctry, fld, deg, gpa, srch)
    st.markdown(f"**Found {len(filtered)} scholarships**")

    if filtered.empty:
        st.info("No results. Try broader filters.")
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
                <div>
                    <div style="font-size:1.05rem;font-weight:700;color:var(--tx1);">{name}</div>
                    <div style="font-size:0.78rem;color:var(--tx2);margin-top:3px;">🌍 {ctry_v} &nbsp;|&nbsp; 📚 {fld_v} &nbsp;|&nbsp; 🎓 {deg_v}</div>
                </div>
                <span class="badge-{badge_color}">{badge_text}</span>
            </div>
            <div style="margin-top:10px;font-size:0.83rem;color:var(--tx2);line-height:1.5;">{desc}</div>
            <div style="display:flex;gap:16px;margin-top:10px;flex-wrap:wrap;">
                <span style="font-size:0.8rem;color:var(--tx1);">💰 <b>{amt}</b></span>
                <span style="font-size:0.8rem;color:var(--tx1);">📊 GPA: <b>{gpa_r}+</b></span>
                <span style="font-size:0.8rem;color:var(--tx1);">🗣️ <b>{lang}</b></span>
                <span style="font-size:0.8rem;color:var(--tx1);">✅ Success: <b>{success}</b></span>
            </div>
            {f'<div style="margin-top:8px;font-size:0.75rem;color:var(--acc);background:var(--glass);border:1px solid var(--gborder);border-radius:6px;padding:6px 10px;">📌 {notes}</div>' if notes and notes != 'nan' else ''}
        </div>
        """, unsafe_allow_html=True)

        ca, cb, cc = st.columns([3,1,1])
        with ca: st.markdown(f"🔗 [Official Website]({url})")
        with cb:
            bm_lbl = "❤️ Saved" if is_bm else "🔖 Save"
            if st.button(bm_lbl, key=f"bm_{idx}", use_container_width=True):
                if is_bm: st.session_state.bookmarks.remove(name)
                else: st.session_state.bookmarks.append(name)
                st.rerun()
        with cc:
            if st.button("📥 Export", key=f"exp_{idx}", use_container_width=True):
                dm2 = get_dm()
                pdf = dm2.export_to_pdf(f"Scholarship: {name}",[
                    {"heading":"Overview","body":f"Country: {ctry_v}\nField: {fld_v}\nDegree: {deg_v}\nAmount: {amt}"},
                    {"heading":"Requirements","body":f"GPA: {gpa_r}+\nLanguage: {lang}\nSuccess Rate: {success}"},
                    {"heading":"Description","body":desc},
                    {"heading":"2026 Notes","body":notes},
                    {"heading":"Apply","body":f"URL: {url}"},
                ])
                st.download_button("⬇️ PDF", pdf, f"{name[:30]}.pdf","application/pdf",key=f"dl_{idx}")

# ── PAGE: AI CHAT ────────────────────────────────────────
def page_ai_chat():
    H("🤖 AI Scholar Assistant")
    ai = engine()

    # Status
    has_groq = bool(st.session_state.api_keys.get("groq",""))
    has_secret = bool(ai.groq_key)
    if has_secret or has_groq:
        st.success("✅ Groq Llama3 Active — Full AI Mode")
    else:
        st.warning("⚠️ No API key found. Using fallback intelligence. Add Groq key in ⚙️ Settings for best results.")

    # Quick questions
    st.markdown("**💡 Quick Questions:**")
    qs = [
        f"Which scholarships can I get with CGPA {st.session_state.profile.get('cgpa',3.0)}?",
        f"Career paths for {st.session_state.profile.get('field','my field') or 'my field'}?",
        "How to write a winning SOP?",
        "How to get strong reference letters?",
        "What to do 6 months before deadline?",
        "How to improve my IELTS score fast?",
    ]
    c1,c2,c3 = st.columns(3)
    for i, (col, q) in enumerate(zip([c1,c2,c3,c1,c2,c3], qs)):
        with col:
            if st.button(q[:45]+"..." if len(q)>45 else q, key=f"qq_{i}", use_container_width=True):
                st.session_state.chat_history.append({"role":"user","content":q})
                with st.spinner("🧠 AI thinking..."):
                    reply = ai.chat_response(q, st.session_state.profile, st.session_state.chat_history[:-1])
                st.session_state.chat_history.append({"role":"assistant","content":reply})
                st.rerun()

    st.markdown("---")

    # Chat display
    if not st.session_state.chat_history:
        st.markdown("""
        <div class="g-card" style="text-align:center;padding:50px 20px;">
            <div style="font-size:3rem;margin-bottom:12px;">🤖</div>
            <div style="font-size:1.1rem;font-weight:700;margin-bottom:8px;color:var(--acc);">ScholarAI Ready</div>
            <div style="color:var(--tx2);font-size:0.9rem;">Ask me anything about scholarships, IELTS, SOP writing, career paths, or interview prep. I give specific answers based on YOUR profile.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in st.session_state.chat_history:
            role = msg.get("role","user")
            content = msg.get("content","")
            if role == "user":
                st.markdown(f'<div class="chat-user fade-up">👤 <b>You:</b> {content}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-ai fade-up">🤖 <b>ScholarAI:</b>\n\n{content}</div>', unsafe_allow_html=True)

    # Input
    with st.form("chat_form", clear_on_submit=True):
        c1, c2 = st.columns([6,1])
        with c1: user_in = st.text_input("Ask ScholarAI...", placeholder="e.g. What career suits CGPA 3.2 Computer Science student targeting Germany?", label_visibility="collapsed")
        with c2: sent = st.form_submit_button("Send →", use_container_width=True)

    if sent and user_in.strip():
        st.session_state.chat_history.append({"role":"user","content":user_in})
        with st.spinner("🧠 ScholarAI thinking..."):
            reply = ai.chat_response(user_in, st.session_state.profile, st.session_state.chat_history[:-1])
        st.session_state.chat_history.append({"role":"assistant","content":reply})
        st.rerun()

    if st.session_state.chat_history:
        c1,c2 = st.columns(2)
        with c1:
            if st.button("🗑️ Clear Chat", key="clr_chat"): st.session_state.chat_history=[]; st.rerun()
        with c2:
            dm = get_dm()
            secs = [{"heading":f"{'You' if m['role']=='user' else 'ScholarAI'} ({i+1})","body":m.get("content","")} for i,m in enumerate(st.session_state.chat_history)]
            pdf = dm.export_to_pdf("AI Chat History", secs)
            st.download_button("📥 Export Chat PDF", pdf, "chat_history.pdf","application/pdf",key="chat_pdf")

# ── PAGE: CV ANALYZER ────────────────────────────────────
def page_cv():
    H("📄 CV Analyzer & ATS Scorer")
    ai = engine()

    tab1, tab2 = st.tabs(["📤 Upload CV", "📊 Analysis Results"])

    with tab1:
        card("""<h4 style='color:var(--acc);margin:0 0 8px;'>🤖 AI-Powered CV Analysis</h4>
<p style='color:var(--tx2);font-size:0.88rem;margin:0;'>Upload your CV as PDF or paste text. AI will give ATS score, identify 5 specific weaknesses, and suggest improvements for scholarship applications.</p>""")

        method = st.radio("Input method", ["📁 Upload PDF", "📋 Paste Text"], horizontal=True)
        cv_text = ""

        if method == "📁 Upload PDF":
            up = st.file_uploader("Upload CV/Resume PDF", type=["pdf"])
            if up:
                with st.spinner("Extracting text..."): cv_text = extract_text_from_pdf(up)
                if cv_text:
                    st.success("✅ Text extracted!")
                    with st.expander("Preview"): st.text(cv_text[:1200]+"..." if len(cv_text)>1200 else cv_text)
        else:
            cv_text = st.text_area("Paste CV text", height=280, placeholder="Paste your full CV/Resume content here — include Education, Experience, Skills, Projects, Publications...")

        if cv_text and len(cv_text) > 100:
            if st.button("🔍 Analyze CV", use_container_width=True, key="analyze_cv"):
                with st.spinner("🤖 AI analyzing your CV... (15-30 seconds)"):
                    result = ai.analyze_cv(cv_text)
                    st.session_state.cv_result = result
                st.success("✅ Done! Check Results tab.")
                st.rerun()
        elif cv_text:
            st.warning("Add more content (min 100 characters)")

    with tab2:
        r = st.session_state.cv_result
        if not r:
            st.info("👈 Upload or paste CV in first tab to see analysis here.")
            return

        ats = r.get("ats_score", 0)
        grade = r.get("grade", "N/A")
        assess = r.get("assessment","")
        sc_color = "#ef4444" if ats<50 else "#f59e0b" if ats<70 else "#10b981"

        c1,c2,c3 = st.columns([1,2,1])
        with c2:
            st.markdown(f"""
            <div class="g-card" style="text-align:center;border-color:{sc_color}44;">
                <div style="font-size:0.8rem;color:var(--tx2);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:8px;font-family:'Orbitron',monospace;">ATS Compatibility Score</div>
                <div style="font-size:4.5rem;font-weight:900;color:{sc_color};font-family:'Orbitron',monospace;line-height:1;">{ats}</div>
                <div style="font-size:1.2rem;font-weight:700;color:{sc_color};margin-top:4px;">Grade: {grade}</div>
                <div style="margin-top:12px;font-size:0.85rem;color:var(--tx2);">{assess}</div>
            </div>
            """, unsafe_allow_html=True)
        st.progress(ats/100)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 🚨 5 Key Weaknesses")
            for i, w in enumerate(r.get("weaknesses",[]),1):
                st.markdown(f'<div class="g-card" style="border-left:3px solid #ef4444;padding:10px 14px;margin:5px 0;"><span style="color:#ef4444;font-weight:700;">{i}.</span> {w}</div>', unsafe_allow_html=True)
        with c2:
            st.markdown("### ✅ Improvements")
            for i, imp in enumerate(r.get("improvements",[]),1):
                st.markdown(f'<div class="g-card" style="border-left:3px solid #10b981;padding:10px 14px;margin:5px 0;"><span style="color:#10b981;font-weight:700;">{i}.</span> {imp}</div>', unsafe_allow_html=True)

        c3,c4 = st.columns(2)
        with c3:
            st.markdown("**✅ Sections Found:**")
            for s in r.get("sections_found",[]): st.markdown(f"✅ {s}")
        with c4:
            st.markdown("**❌ Missing Sections:**")
            for s in r.get("sections_missing",[]): st.markdown(f"❌ {s}")

        kws = r.get("missing_keywords",[])
        if kws:
            st.markdown("**🔑 Missing Keywords:**")
            st.markdown("  ".join(f'<code style="background:var(--glass);border:1px solid var(--gborder);padding:3px 8px;border-radius:5px;color:var(--acc);font-family:Share Tech Mono,monospace;">{k}</code>' for k in kws), unsafe_allow_html=True)

        dm = get_dm()
        pdf = dm.export_to_pdf("CV Analysis Report",[
            {"heading":"ATS Score","body":f"Score: {ats}/100\nGrade: {grade}\n{assess}"},
            {"heading":"Weaknesses","body":"\n".join(f"{i}. {w}" for i,w in enumerate(r.get("weaknesses",[]),1))},
            {"heading":"Improvements","body":"\n".join(f"{i}. {w}" for i,w in enumerate(r.get("improvements",[]),1))},
            {"heading":"Keywords Missing","body":", ".join(kws)},
        ])
        st.download_button("📥 Export PDF", pdf,"cv_analysis.pdf","application/pdf",key="cv_pdf")

# ── PAGE: SOP IMPROVE ────────────────────────────────────
def page_sop():
    H("✍️ SOP Improve AI")
    ai = engine()

    card("""<h4 style='color:var(--acc);margin:0 0 8px;'>🚀 High-Impact SOP Rewriter</h4>
<p style='color:var(--tx2);font-size:0.88rem;margin:0;'>Paste your Statement of Purpose — AI rewrites it with compelling opening, specific achievements, clear vision, and powerful conclusion. Get before/after impact scores.</p>""")

    c1,c2 = st.columns(2)
    with c1: target = st.text_input("Target Scholarship", placeholder="e.g. Chevening 2027", key="sop_target")
    with c2: focus = st.selectbox("Emphasis", ["Overall Quality","Research Focus","Leadership","Community Impact","Career Vision"], key="sop_focus")

    original = st.text_area("📝 Your Current SOP", height=280, placeholder="Paste your Statement of Purpose here...\n\nTip: Include your background, motivation, research goals, and future plans. The more you give, the better the rewrite.", key="sop_orig")

    if original and len(original) > 150:
        if st.button("🚀 Rewrite for High Impact", use_container_width=True, key="sop_btn"):
            with st.spinner("✍️ AI rewriting your SOP... (20-40 seconds)"):
                result = ai.rewrite_sop(original, target)
                st.session_state.sop_result = result
            st.rerun()
    elif original:
        st.warning("Please paste a longer SOP (min 150 characters) for best results.")

    r = st.session_state.sop_result
    if r:
        bef = r.get("score_before",0); aft = r.get("score_after",0)
        imp = aft - bef
        c1,c2,c3 = st.columns(3)
        with c1: st.markdown(f'<div class="metric"><div class="metric-val" style="color:#ef4444;">{bef}</div><div class="metric-label">Before</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="metric"><div class="metric-val" style="color:#10b981;">{aft}</div><div class="metric-label">After</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="metric"><div class="metric-val" style="color:var(--acc);">+{imp}</div><div class="metric-label">Improvement</div></div>', unsafe_allow_html=True)
        st.progress(aft/100)

        st.markdown("### ✨ AI-Rewritten High-Impact SOP")
        rewritten = r.get("rewritten_sop","")
        st.markdown(f'<div class="g-card" style="border-left:4px solid #10b981;"><div style="white-space:pre-wrap;font-size:0.92rem;line-height:1.75;color:var(--tx1);">{rewritten}</div></div>', unsafe_allow_html=True)
        st.text_area("📋 Copy Rewritten SOP", rewritten, height=200, key="sop_copy")

        c1,c2 = st.columns(2)
        with c1:
            st.markdown("**🔄 Changes Made:**")
            for ch in r.get("changes",[]): st.markdown(f"✅ {ch}")
        with c2:
            st.markdown("**💡 Further Suggestions:**")
            for sg in r.get("suggestions",[]): st.markdown(f"→ {sg}")

        dm = get_dm()
        pdf = dm.export_to_pdf("SOP Improvement Report",[
            {"heading":"Impact Scores","body":f"Before: {bef}/100\nAfter: {aft}/100\nImprovement: +{imp} points"},
            {"heading":"Rewritten SOP","body":rewritten},
            {"heading":"Changes","body":"\n".join(r.get("changes",[]))},
            {"heading":"Suggestions","body":"\n".join(r.get("suggestions",[]))},
        ])
        st.download_button("📥 Export SOP Report", pdf,"sop_report.pdf","application/pdf",key="sop_pdf")

# ── PAGE: ROADMAP ────────────────────────────────────────
def page_roadmap():
    H("🗺️ Full Scholarship Roadmap")
    ai = engine()

    c1,c2,c3 = st.columns(3)
    with c1: cur_yr = st.selectbox("Current Year", ["1st Year","2nd Year","3rd Year","4th Year","Graduate","Working Professional"], key="rm_yr")
    with c2: tgt_deg = st.selectbox("Target Degree", ["Masters","PhD","Postdoctoral","MBA","LLM"], key="rm_deg")
    with c3: tgt_yr = st.selectbox("Target Start", ["2026","2027","2028"], key="rm_tyr")
    fld = st.session_state.profile.get("field","") or st.text_input("Field of Study", placeholder="e.g. Computer Science", key="rm_fld")

    if st.button("🗺️ Generate My Personalized Roadmap", use_container_width=True, key="rm_btn"):
        with st.spinner("🤖 Generating your personalized roadmap..."):
            rm = ai.generate_roadmap(cur_yr, fld, tgt_deg, tgt_yr, st.session_state.profile)
            st.session_state.roadmap_text = rm
        st.rerun()

    if st.session_state.roadmap_text:
        st.markdown(f'<div class="g-card" style="border-left:4px solid var(--acc);"><div style="white-space:pre-wrap;font-size:0.9rem;line-height:1.8;color:var(--tx1);">{st.session_state.roadmap_text}</div></div>', unsafe_allow_html=True)
        dm = get_dm()
        pdf = dm.export_to_pdf("Scholarship Roadmap",[{"heading":"Your Personalized 12-Month Roadmap","body":st.session_state.roadmap_text}])
        st.download_button("📥 Download Roadmap PDF", pdf,"roadmap.pdf","application/pdf",key="rm_pdf")

# ── PAGE: REJECTION SIM ──────────────────────────────────
def page_rejection():
    H("⚠️ Rejection Reason Simulator")
    ai = engine()

    card("""<h4 style='color:#ef4444;margin:0 0 8px;'>🚨 AI Rejection Risk Analysis</h4>
<p style='color:var(--tx2);font-size:0.88rem;margin:0;'>AI analyzes your profile against real scholarship selection criteria to predict WHY you might get rejected — so you can fix issues BEFORE submitting.</p>""")

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

    if st.button("🔍 Analyze My Rejection Risk", use_container_width=True, key="rj_btn"):
        profile = {"cgpa":cgpa,"ielts":ielts,"research":research,"leadership":leadership,"target_scholarship":target_sc,"field":st.session_state.profile.get("field","General")}
        with st.spinner("🔬 AI analyzing your risks..."):
            result = ai.simulate_rejection(profile)
            st.session_state.rejection_result = result
        st.rerun()

    r = st.session_state.rejection_result
    if r:
        prob = r.get("success_probability",0)
        verdict = r.get("verdict","Unknown")
        vc = "#ef4444" if "High" in verdict else "#f59e0b" if "Medium" in verdict else "#10b981"

        c1,c2,c3 = st.columns(3)
        with c1: st.markdown(f'<div class="metric"><div class="metric-val" style="color:{vc};">{prob}%</div><div class="metric-label">Success Probability</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="metric"><div class="metric-val" style="font-size:1rem;color:{vc};">{verdict}</div><div class="metric-label">Risk Level</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="metric"><div class="metric-val" style="font-size:0.85rem;">{r.get("estimated_timeline","N/A")}</div><div class="metric-label">Timeline to Competitive</div></div>', unsafe_allow_html=True)
        st.progress(prob/100)

        H("🚨 Risk Factors Identified")
        for i, risk in enumerate(r.get("risks",[])):
            sev = risk.get("severity","Medium")
            sc = "#ef4444" if sev=="High" else "#f59e0b" if sev=="Medium" else "#10b981"
            bc = "red" if sev=="High" else "orange" if sev=="Medium" else "green"
            st.markdown(f"""
            <div class="g-card" style="border-left:4px solid {sc};">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                    <div style="font-weight:700;font-size:0.95rem;">{i+1}. {risk.get('factor','')}</div>
                    <span class="badge-{bc}">{sev} Risk</span>
                </div>
                <div style="color:var(--tx2);font-size:0.84rem;margin-bottom:8px;">{risk.get('detail','')}</div>
                <div style="color:#10b981;font-size:0.84rem;font-weight:500;">✅ Fix: {risk.get('fix','')}</div>
            </div>
            """, unsafe_allow_html=True)

        top = r.get("top_recommendation","")
        if top:
            st.markdown(f'<div class="g-card" style="border:1px solid #10b98133;background:rgba(16,185,129,0.05);"><div style="font-weight:700;margin-bottom:6px;">🎯 Top Priority Action:</div><div style="color:#10b981;">{top}</div></div>', unsafe_allow_html=True)

# ── PAGE: IELTS ──────────────────────────────────────────
def page_ielts():
    H("🎤 IELTS / TOEFL Prep Module")
    ai = engine()

    tab1, tab2, tab3 = st.tabs(["🎤 Speaking Mock", "📝 Study Tips", "📊 Score Calculator"])

    with tab1:
        card("""<h4 style='color:var(--acc);margin:0 0 8px;'>Speaking Mock Generator</h4>
<p style='color:var(--tx2);font-size:0.88rem;margin:0;'>Generate realistic IELTS Speaking prompts with band scoring guidance and vocabulary tips.</p>""")
        c1,c2 = st.columns(2)
        with c1: part = st.selectbox("Speaking Part", ["Part 2 (Long Turn - 2 min)","Part 1 (Introduction)","Part 3 (Discussion)"], key="ielts_part")
        with c2: topic = st.selectbox("Topic Area", ["Random","Education","Technology","Environment","Culture","Work & Career","Health","Society","Family","Travel"], key="ielts_topic")

        if st.button("🎲 Generate Mock Prompt", use_container_width=True, key="ielts_gen"):
            with st.spinner("Generating prompt..."):
                prompt = ai.generate_ielts_prompt(part, topic)
                st.session_state.ielts_prompt = prompt
            st.rerun()

        if st.session_state.ielts_prompt:
            st.markdown(f'<div class="g-card" style="border-left:4px solid var(--acc);"><div style="white-space:pre-wrap;font-size:0.9rem;line-height:1.75;color:var(--tx1);">{st.session_state.ielts_prompt}</div></div>', unsafe_allow_html=True)
            ans = st.text_area("📝 Practice Answer:", height=140, placeholder="Write your practice response here...", key="ielts_ans")
            if ans and st.button("📊 Evaluate Answer", key="ielts_eval"):
                with st.spinner("Evaluating..."):
                    ev = ai.evaluate_answer(st.session_state.ielts_prompt[:200], ans)
                total = ev.get("total",0)
                ec = "#10b981" if total>75 else "#f59e0b" if total>60 else "#ef4444"
                st.markdown(f'<div class="metric" style="text-align:center;"><div class="metric-val" style="color:{ec};">{total}/100</div><div class="metric-label">Band Score: {ev.get("grade","N/A")}</div></div>', unsafe_allow_html=True)
                c1,c2 = st.columns(2)
                with c1:
                    for s in ev.get("strengths",[]): st.markdown(f"✅ {s}")
                with c2:
                    for i in ev.get("improvements",[]): st.markdown(f"→ {i}")
                st.info(f"💡 {ev.get('model_answer_tip','')}")

    with tab2:
        tips_data = {
            "📖 Reading": ["Skim first for main ideas, then scan for specific answers","True/False/Not Given: 'Not Given' = info not in text (not 'false')","Read questions BEFORE the passage to know what to look for","Manage time: max 20 minutes per section","Watch qualifying words: always, never, most, some, usually"],
            "✍️ Writing Task 1": ["Always write an overview paragraph — most candidates skip this and lose marks","Compare specific data points, not just describe everything","Paraphrase the question for your introduction — never copy","Target 170-190 words (not 150 minimum)","Use variety: increased dramatically, fell sharply, remained stable"],
            "✍️ Writing Task 2": ["State your position clearly in the INTRODUCTION — not the conclusion","Each body paragraph: topic sentence + 2 supporting points + specific example","Use connectors: Furthermore, In contrast, Consequently, Notably","Target 270-290 words","Common question types: Agree/Disagree, Both Views, Problem-Solution, Advantages-Disadvantages"],
            "👂 Listening": ["Read questions during 30-second preview time — predict answer types","Answers appear in ORDER in the audio — don't fall behind","Signpost language: 'However', 'Moving on to', 'In conclusion'","Spelling errors cost marks — write carefully during transfer","Watch for distractors: answer often comes after correction"],
        }
        for section, tips in tips_data.items():
            with st.expander(f"**{section}**"):
                for t in tips: st.markdown(f"• {t}")

    with tab3:
        H("📊 Band Score Estimator")
        c1,c2,c3,c4 = st.columns(4)
        with c1: r_s = st.slider("Reading", 1.0, 9.0, 6.5, 0.5, key="ielts_r")
        with c2: w_s = st.slider("Writing", 1.0, 9.0, 6.0, 0.5, key="ielts_w")
        with c3: l_s = st.slider("Listening", 1.0, 9.0, 7.0, 0.5, key="ielts_l")
        with c4: sp_s = st.slider("Speaking", 1.0, 9.0, 6.5, 0.5, key="ielts_sp")
        overall = round((r_s+w_s+l_s+sp_s)/4*2)/2
        oc = "#ef4444" if overall<6.5 else "#f59e0b" if overall<7.0 else "#10b981"
        verdict = "✅ Meets most scholarship requirements" if overall>=7.0 else "⚠️ Meets minimum (6.5 required)" if overall>=6.5 else "❌ Below scholarship requirements — retake needed"
        st.markdown(f'<div class="g-card" style="text-align:center;border:2px solid {oc}44;"><div style="font-size:0.8rem;color:var(--tx2);text-transform:uppercase;letter-spacing:0.1em;font-family:Orbitron,monospace;margin-bottom:8px;">Overall Band Score</div><div style="font-size:4rem;font-weight:900;color:{oc};font-family:Orbitron,monospace;">{overall}</div><div style="color:var(--tx2);margin-top:8px;font-size:0.9rem;">{verdict}</div></div>', unsafe_allow_html=True)

# ── PAGE: INTERVIEW ──────────────────────────────────────
def page_interview():
    H("🎯 Interview Prep Mode")
    ai = engine()

    IQS = [
        "Tell me about yourself and your academic journey.",
        "Why did you choose this specific scholarship?",
        "What is your most significant academic or research achievement?",
        "Where do you see yourself in 10 years?",
        "How will you contribute to Pakistan after completing your studies?",
        "Describe a time you faced a significant challenge and how you overcame it.",
        "What makes you a stronger candidate than other applicants?",
        "How does this program align with your long-term career goals?",
        "Describe your leadership experience and its community impact.",
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
        <div class="g-card" style="border-left:4px solid var(--acc2);">
            <div style="font-size:0.75rem;color:var(--tx2);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:8px;font-family:'Orbitron',monospace;">Interview Question — {sc_type}</div>
            <div style="font-size:1.1rem;font-weight:600;color:var(--tx1);line-height:1.5;">"{st.session_state.interview_q}"</div>
        </div>
        """, unsafe_allow_html=True)

        answer = st.text_area("✍️ Your Answer (aim for 200-280 words = ~90-120 sec speaking):", height=150, key="iv_ans")

        c1,c2 = st.columns(2)
        with c1:
            if st.button("📊 Evaluate Answer", use_container_width=True, key="iv_eval") and answer:
                with st.spinner("🤖 Evaluating..."):
                    ev = ai.evaluate_answer(st.session_state.interview_q, answer)
                c1s,c2s,c3s,c4s = st.columns(4)
                for col, (lbl, sc_k) in zip([c1s,c2s,c3s,c4s],[("Clarity","clarity"),("Relevance","relevance"),("Evidence","evidence"),("Communication","communication")]):
                    sc_v = ev.get(sc_k,0)
                    ec = "#10b981" if sc_v>=20 else "#f59e0b" if sc_v>=15 else "#ef4444"
                    with col: st.markdown(f'<div class="metric"><div class="metric-val" style="font-size:1.5rem;color:{ec};">{sc_v}/25</div><div class="metric-label">{lbl}</div></div>', unsafe_allow_html=True)
                total = ev.get("total",0)
                tc = "#10b981" if total>75 else "#f59e0b" if total>60 else "#ef4444"
                st.markdown(f'<div class="g-card" style="text-align:center;"><span style="font-size:2rem;font-weight:900;color:{tc};font-family:Orbitron,monospace;">{total}/100</span><span style="font-size:1.1rem;color:var(--tx2);margin-left:12px;">Grade: {ev.get("grade","N/A")}</span></div>', unsafe_allow_html=True)
                c1a,c2a = st.columns(2)
                with c1a:
                    st.markdown("**💪 Strengths:**")
                    for s in ev.get("strengths",[]): st.markdown(f"✅ {s}")
                with c2a:
                    st.markdown("**📈 Improvements:**")
                    for i in ev.get("improvements",[]): st.markdown(f"→ {i}")
                tip = ev.get("model_answer_tip","")
                if tip: st.info(f"💡 **Pro Tip:** {tip}")
        with c2:
            if st.button("🔄 Next Question", use_container_width=True, key="iv_next"):
                st.session_state.interview_q = random.choice(IQS)
                st.rerun()

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
            st.markdown(f'<div class="g-card" style="border-left:4px solid var(--acc2);"><div style="font-size:0.75rem;color:var(--tx2);text-transform:uppercase;letter-spacing:0.08em;font-family:Orbitron,monospace;margin-bottom:6px;">Q{idx+1}</div><div style="font-size:1.05rem;font-weight:600;">"{qs[idx]}"</div></div>', unsafe_allow_html=True)
            ans = st.text_area("Your answer:", height=120, key=f"mock_a_{idx}")
            if st.button("Next →", use_container_width=True, key=f"mock_n_{idx}") and ans:
                st.session_state.mock_ans.append({"q":qs[idx],"a":ans})
                st.session_state.mock_idx += 1
                st.rerun()
        else:
            st.success("🎉 Mock interview complete!")
            for i, qa in enumerate(st.session_state.mock_ans):
                with st.expander(f"Q{i+1}: {qa['q'][:60]}..."):
                    st.markdown(f"**Your Answer:** {qa['a']}")
            if st.button("🔄 Restart Interview"):
                del st.session_state.mock_qs, st.session_state.mock_idx, st.session_state.mock_ans
                st.rerun()

# ── PAGE: COMPARE ────────────────────────────────────────
def page_compare():
    H("📊 Compare Scholarships")
    dm = get_dm()
    ai = engine()
    names = dm.get_all_names()
    if len(names) < 2:
        st.warning("Not enough scholarships in database.")
        return
    c1,c2 = st.columns(2)
    with c1: s1 = st.selectbox("Scholarship A", names, key="cmp_s1")
    with c2: s2_opts = [n for n in names if n!=s1]; s2 = st.selectbox("Scholarship B", s2_opts, key="cmp_s2")

    if st.button("⚡ Compare Now", use_container_width=True, key="cmp_btn"):
        cmp = dm.compare_scholarships(s1, s2)
        if not cmp:
            st.error("Could not load comparison data.")
            return

        st.markdown(f'<div class="cmp-grid"><div class="cmp-lbl">Criteria</div><div class="cmp-hdr">{s1[:30]}</div><div class="cmp-hdr">{s2[:30]}</div></div>', unsafe_allow_html=True)
        for key, data in cmp.items():
            lbl = data.get("label", key).replace("_"," ").title()
            v1 = str(data.get(s1,"N/A")); v2 = str(data.get(s2,"N/A"))
            st.markdown(f'<div class="cmp-grid"><div class="cmp-lbl">{lbl}</div><div class="cmp-val">{v1}</div><div class="cmp-val">{v2}</div></div>', unsafe_allow_html=True)

        st.markdown("---")
        prof = st.session_state.profile
        with st.spinner("🤖 AI analyzing best fit for your profile..."):
            ap = f"""Compare {s1} vs {s2} for a student with:
CGPA: {prof.get('cgpa',3.0)}, IELTS: {prof.get('ielts',6.5)}, Field: {prof.get('field','General')}

Give specific recommendation: which is better match, which is more accessible, and final verdict."""
            analysis = ai.chat_response(ap, prof, [])
        st.markdown(f'<div class="g-card" style="border-left:4px solid var(--acc3);"><h4 style="color:var(--acc);margin:0 0 10px;">🤖 AI Recommendation for Your Profile</h4><div style="white-space:pre-wrap;font-size:0.9rem;line-height:1.7;color:var(--tx1);">{analysis}</div></div>', unsafe_allow_html=True)

# ── PAGE: BOOKMARKS ──────────────────────────────────────
def page_bookmarks():
    H("🔖 Saved Scholarships")
    bm = st.session_state.bookmarks
    dm = get_dm()

    if not bm:
        st.markdown('<div class="g-card" style="text-align:center;padding:60px;"><div style="font-size:3rem;margin-bottom:12px;">🔖</div><div style="font-weight:600;font-size:1.1rem;margin-bottom:8px;color:var(--acc);">No Saved Scholarships</div><div style="color:var(--tx2);">Go to Scholarships and click 🔖 Save on programs you are interested in.</div></div>', unsafe_allow_html=True)
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
                    <div style="font-size:1.05rem;font-weight:700;">{nm}</div>
                    <div style="font-size:0.78rem;color:var(--tx2);">🌍 {row.get('country','N/A')} &nbsp;|&nbsp; 💰 {row.get('amount','N/A')} &nbsp;|&nbsp; 📊 GPA {row.get('gpa required','N/A')}+</div>
                </div>
                <span class="badge-{badge_color}">{badge_text}</span>
            </div>
            <div style="margin-top:8px;font-size:0.82rem;color:var(--tx2);">{str(row.get('description',''))[:200]}...</div>
        </div>
        """, unsafe_allow_html=True)
        c1,c2 = st.columns([4,1])
        with c1: st.markdown(f"🔗 [Official Website]({row.get('url','#')})")
        with c2:
            if st.button("❌ Remove", key=f"rm_bm_{nm}", use_container_width=True):
                st.session_state.bookmarks.remove(nm); st.rerun()

    if st.button("📥 Export All Bookmarks PDF", use_container_width=True, key="bm_pdf_btn"):
        secs = []
        for nm in bm:
            row_df = dm.df[dm.df['name'].str.lower()==nm.lower()]
            if not row_df.empty:
                r = row_df.iloc[0]
                secs.append({"heading":nm,"body":f"Country: {r.get('country','N/A')}\nAmount: {r.get('amount','N/A')}\nGPA: {r.get('gpa required','N/A')}+\nLanguage: {r.get('language requirement','N/A')}\nURL: {r.get('url','N/A')}"})
        pdf = dm.export_to_pdf("My Bookmarked Scholarships", secs)
        st.download_button("⬇️ Download PDF", pdf,"bookmarks.pdf","application/pdf",key="bm_dl")

# ── PAGE: SETTINGS ───────────────────────────────────────
def page_settings():
    H("⚙️ Settings")
    tab1, tab2, tab3 = st.tabs(["🔑 API Keys", "👤 Profile", "ℹ️ About"])

    with tab1:
        card("""<h4 style='color:var(--acc);margin:0 0 8px;'>🤖 AI Model Configuration</h4>
<p style='color:var(--tx2);font-size:0.88rem;margin:0;'>Add your API keys to enable full AI capabilities. Without keys, ScholarAI uses intelligent fallback logic that still works well.</p>""")

        # Show if secret key is detected
        ai = engine()
        if ai.groq_key:
            st.success("✅ Groq API key detected and active!")
        else:
            st.warning("⚠️ No Groq key found. Add below for full AI features.")

        gk = st.text_input("🟢 Groq API Key (Free - Recommended)", value=st.session_state.api_keys.get("groq",""), type="password", help="Get free key at console.groq.com")
        st.caption("🔗 Get free key: https://console.groq.com — Powers: Chat, CV Analysis, SOP, Interview, Roadmap")

        mk = st.text_input("🔵 Gemini 1.5 Pro API Key (Optional)", value=st.session_state.api_keys.get("gemini",""), type="password")
        st.caption("🔗 Get key: https://makersuite.google.com/app/apikey — Powers: PDF Vision, better CV analysis")

        if st.button("💾 Save API Keys", use_container_width=True, key="save_keys"):
            st.session_state.api_keys["groq"] = gk
            st.session_state.api_keys["gemini"] = mk
            get_engine.clear()
            st.success("✅ API keys saved! AI models reloaded.")

        H("📊 Model Status")
        c1,c2,c3 = st.columns(3)
        ak = ai.groq_key
        mk2 = ai.gemini_key
        with c1: st.markdown(f'<div class="metric"><div style="font-size:1.5rem;">🟢</div><div class="metric-val" style="font-size:1rem;color:{"#10b981" if ak else "#f59e0b"};">{"Active" if ak else "Fallback"}</div><div class="metric-label">Groq Llama3</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="metric"><div style="font-size:1.5rem;">🔵</div><div class="metric-val" style="font-size:1rem;color:{"#10b981" if mk2 else "#6b7280"};">{"Active" if mk2 else "Not Set"}</div><div class="metric-label">Gemini 1.5 Pro</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="metric"><div style="font-size:1.5rem;">🤖</div><div class="metric-val" style="font-size:1rem;color:#10b981;">Always On</div><div class="metric-label">Local Fallback</div></div>', unsafe_allow_html=True)

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
        r2 = st.selectbox("Research", ["none","minimal","coursework projects","conference paper","published paper","multiple publications"], key="st_res")
        l2 = st.selectbox("Leadership", ["none","minimal","club member","club officer","founded organization","professional role"], key="st_lead")

        if st.button("💾 Update Profile", use_container_width=True, key="st_save"):
            st.session_state.profile.update({"name":nm,"cgpa":cgpa,"field":fld,"year":year,"ielts":ielts,"country":country,"research":r2,"leadership":l2})
            st.success("✅ Profile updated!")
            st.rerun()

    with tab3:
        st.markdown(f"""
        <div class="g-card">
            <div style="font-family:'Orbitron',monospace;font-size:1.3rem;font-weight:900;background:linear-gradient(135deg,var(--acc),var(--acc2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:12px;">ScholarAI Elite v3.0</div>
            <p style="color:var(--tx2);">Enterprise-grade AI scholarship intelligence platform for international aspirants from Pakistan and developing countries.</p>
            <h4 style="color:var(--acc);font-family:'Orbitron',monospace;font-size:0.9rem;">🤖 AI MODELS:</h4>
            <ul style="color:var(--tx2);font-size:0.88rem;">
                <li><b>Groq Llama3-70B</b> — Chat, SOP, Interview, Rejection Analysis, Roadmap</li>
                <li><b>Google Gemini 1.5 Pro</b> — PDF processing, Vision, complex reasoning</li>
                <li><b>Intelligent Local Fallback</b> — Profile-based logic when APIs unavailable</li>
            </ul>
            <h4 style="color:var(--acc);font-family:'Orbitron',monospace;font-size:0.9rem;">📦 INSTALL:</h4>
            <div style="font-family:'Share Tech Mono',monospace;background:rgba(0,0,0,0.3);padding:12px;border-radius:8px;font-size:0.82rem;color:var(--acc);border:1px solid var(--gborder);">
            pip install streamlit groq google-generativeai pandas fpdf2 pdfplumber
            </div>
            <h4 style="color:var(--acc);font-family:'Orbitron',monospace;font-size:0.9rem;margin-top:12px;">🚀 RUN:</h4>
            <div style="font-family:'Share Tech Mono',monospace;background:rgba(0,0,0,0.3);padding:12px;border-radius:8px;font-size:0.82rem;color:#10b981;border:1px solid var(--gborder);">
            streamlit run app.py
            </div>
            <p style="color:var(--tx2);font-size:0.78rem;margin-top:16px;">16 verified 2026 scholarships | Full AI features with Groq key | Built for Pakistani students</p>
        </div>
        """, unsafe_allow_html=True)

# ── MAIN ─────────────────────────────────────────────────
def main():
    init_ss()
    apply_css(st.session_state.dark_mode)

    if not st.session_state.logged_in:
        page_login()
        return

    render_sidebar()

    pg = st.session_state.page
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
    pages.get(pg, page_dashboard)()

if __name__ == "__main__":
    main()
