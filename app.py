"""
ScholarAI Elite — Enterprise Scholarship Intelligence Platform
Author: ScholarAI Team | Version: 2.0
Full-stack Streamlit app with multi-model AI orchestration
"""

import os
import sys
import json
import time
import random
import datetime
from typing import Dict, List, Optional, Any

import streamlit as st
import pandas as pd

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils.ai_engine import AIEngine
from utils.data_manager import DataManager, extract_text_from_pdf

# ─────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ScholarAI Elite",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────
# GLOBAL CSS — GLASSMORPHISM + DARK/LIGHT MODE
# ─────────────────────────────────────────────────────────
def apply_custom_css(dark_mode: bool = True):
    if dark_mode:
        bg_primary = "#0A0E1A"
        bg_secondary = "#111827"
        glass_bg = "rgba(255,255,255,0.04)"
        glass_border = "rgba(255,255,255,0.10)"
        text_primary = "#F1F5F9"
        text_secondary = "#94A3B8"
        accent = "#3B82F6"
        accent2 = "#8B5CF6"
        accent3 = "#06B6D4"
        card_shadow = "rgba(0,0,0,0.5)"
        gradient_from = "#1E3A5F"
        gradient_to = "#0A0E1A"
    else:
        bg_primary = "#F0F4FF"
        bg_secondary = "#FFFFFF"
        glass_bg = "rgba(255,255,255,0.7)"
        glass_border = "rgba(59,130,246,0.20)"
        text_primary = "#1E293B"
        text_secondary = "#64748B"
        accent = "#2563EB"
        accent2 = "#7C3AED"
        accent3 = "#0891B2"
        card_shadow = "rgba(59,130,246,0.15)"
        gradient_from = "#DBEAFE"
        gradient_to = "#F0F4FF"

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Fira+Code:wght@400;500&display=swap');

    /* ── Base ── */
    html, body, .stApp {{
        background: linear-gradient(135deg, {gradient_from} 0%, {bg_primary} 60%, {gradient_to} 100%);
        font-family: 'Outfit', sans-serif;
        color: {text_primary};
    }}
    .stApp {{ background: linear-gradient(135deg, {gradient_from} 0%, {bg_primary} 60%, {gradient_to} 100%); }}

    /* ── Hide default streamlit chrome ── */
    #MainMenu, footer, header {{ visibility: hidden; }}
    .stDeployButton {{ display: none; }}

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {{
        background: {bg_secondary} !important;
        border-right: 1px solid {glass_border};
        backdrop-filter: blur(20px);
    }}
    [data-testid="stSidebar"] * {{ color: {text_primary} !important; }}

    /* ── Glass Cards ── */
    .glass-card {{
        background: {glass_bg};
        border: 1px solid {glass_border};
        border-radius: 16px;
        padding: 24px;
        margin: 12px 0;
        backdrop-filter: blur(12px);
        box-shadow: 0 8px 32px {card_shadow};
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    .glass-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 12px 40px {card_shadow};
    }}

    /* ── Scholarship Card ── */
    .scholar-card {{
        background: {glass_bg};
        border: 1px solid {glass_border};
        border-radius: 20px;
        padding: 20px 24px;
        margin: 10px 0;
        backdrop-filter: blur(16px);
        box-shadow: 0 4px 24px {card_shadow};
        transition: all 0.25s ease;
        position: relative;
        overflow: hidden;
    }}
    .scholar-card::before {{
        content: '';
        position: absolute;
        top: 0; left: 0;
        width: 4px; height: 100%;
        background: linear-gradient(180deg, {accent}, {accent2});
        border-radius: 20px 0 0 20px;
    }}
    .scholar-card:hover {{
        transform: translateX(4px);
        border-color: {accent};
        box-shadow: 0 8px 32px {card_shadow}, 0 0 0 1px {accent}33;
    }}

    /* ── Hero Header ── */
    .hero-header {{
        background: linear-gradient(135deg, {accent}22, {accent2}22);
        border: 1px solid {accent}33;
        border-radius: 24px;
        padding: 40px;
        text-align: center;
        margin-bottom: 24px;
        backdrop-filter: blur(20px);
        position: relative;
        overflow: hidden;
    }}
    .hero-header::after {{
        content: '';
        position: absolute;
        top: -50%; right: -50%;
        width: 200%; height: 200%;
        background: radial-gradient(circle, {accent}11 0%, transparent 60%);
        pointer-events: none;
    }}
    .hero-title {{
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, {accent}, {accent2}, {accent3});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        line-height: 1.1;
    }}
    .hero-subtitle {{
        color: {text_secondary};
        font-size: 1.1rem;
        font-weight: 400;
        margin-top: 8px;
    }}

    /* ── Metric Cards ── */
    .metric-card {{
        background: {glass_bg};
        border: 1px solid {glass_border};
        border-radius: 14px;
        padding: 18px 20px;
        text-align: center;
        backdrop-filter: blur(10px);
    }}
    .metric-value {{
        font-size: 2.2rem;
        font-weight: 700;
        color: {accent};
        line-height: 1;
    }}
    .metric-label {{
        font-size: 0.8rem;
        color: {text_secondary};
        margin-top: 4px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }}

    /* ── Deadline Badges ── */
    .badge-red {{
        display: inline-block;
        background: linear-gradient(135deg, #EF4444, #DC2626);
        color: white;
        font-size: 0.7rem;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 20px;
        letter-spacing: 0.05em;
    }}
    .badge-orange {{
        display: inline-block;
        background: linear-gradient(135deg, #F59E0B, #D97706);
        color: white;
        font-size: 0.7rem;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 20px;
        letter-spacing: 0.05em;
    }}
    .badge-green {{
        display: inline-block;
        background: linear-gradient(135deg, #10B981, #059669);
        color: white;
        font-size: 0.7rem;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 20px;
        letter-spacing: 0.05em;
    }}
    .badge-gray {{
        display: inline-block;
        background: #6B7280;
        color: white;
        font-size: 0.7rem;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 20px;
        letter-spacing: 0.05em;
    }}

    /* ── Progress Bar Override ── */
    .stProgress > div > div > div > div {{
        background: linear-gradient(90deg, {accent}, {accent2}) !important;
        border-radius: 10px;
    }}

    /* ── Stepper ── */
    .stepper-item {{
        display: flex;
        align-items: flex-start;
        margin: 8px 0;
        padding: 14px 18px;
        background: {glass_bg};
        border: 1px solid {glass_border};
        border-radius: 12px;
        position: relative;
    }}
    .step-number {{
        width: 32px; height: 32px;
        background: linear-gradient(135deg, {accent}, {accent2});
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-weight: 700; font-size: 0.85rem;
        color: white;
        flex-shrink: 0;
        margin-right: 14px;
        margin-top: 2px;
    }}
    .step-content {{ flex: 1; }}
    .step-title {{ font-weight: 600; font-size: 0.95rem; color: {text_primary}; }}
    .step-detail {{ font-size: 0.82rem; color: {text_secondary}; margin-top: 3px; }}

    /* ── Chat Messages ── */
    .chat-msg-user {{
        background: linear-gradient(135deg, {accent}22, {accent}11);
        border: 1px solid {accent}33;
        border-radius: 16px 16px 4px 16px;
        padding: 14px 18px;
        margin: 8px 0;
        margin-left: 40px;
        font-size: 0.95rem;
    }}
    .chat-msg-ai {{
        background: {glass_bg};
        border: 1px solid {glass_border};
        border-radius: 16px 16px 16px 4px;
        padding: 14px 18px;
        margin: 8px 0;
        margin-right: 40px;
        font-size: 0.95rem;
    }}

    /* ── Section Headers ── */
    .section-header {{
        font-size: 1.6rem;
        font-weight: 700;
        color: {text_primary};
        margin: 20px 0 16px 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }}
    .section-header::after {{
        content: '';
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, {accent}66, transparent);
        margin-left: 12px;
    }}

    /* ── Input Overrides ── */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {{
        background: {glass_bg} !important;
        border-color: {glass_border} !important;
        color: {text_primary} !important;
        border-radius: 10px !important;
        font-family: 'Outfit', sans-serif !important;
    }}
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {{
        border-color: {accent} !important;
        box-shadow: 0 0 0 3px {accent}22 !important;
    }}

    /* ── Buttons ── */
    .stButton > button {{
        background: linear-gradient(135deg, {accent}, {accent2}) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
        padding: 8px 20px !important;
        transition: all 0.2s ease !important;
    }}
    .stButton > button:hover {{
        opacity: 0.92 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 16px {accent}44 !important;
    }}

    /* ── Score Ring ── */
    .score-ring {{
        width: 120px; height: 120px;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        margin: 0 auto;
        font-size: 2rem;
        font-weight: 800;
    }}

    /* ── Comparison Table ── */
    .compare-header {{
        background: linear-gradient(135deg, {accent}22, {accent2}22);
        padding: 10px 16px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 0.95rem;
        margin-bottom: 4px;
    }}
    .compare-row {{
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 8px;
        margin: 6px 0;
        align-items: start;
    }}
    .compare-label {{ font-weight: 600; font-size: 0.82rem; color: {text_secondary}; text-transform: uppercase; letter-spacing: 0.05em; padding: 8px; }}
    .compare-val {{ font-size: 0.9rem; color: {text_primary}; padding: 8px; background: {glass_bg}; border-radius: 8px; border: 1px solid {glass_border}; }}

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {{
        background: {glass_bg};
        border-radius: 12px;
        padding: 4px;
        border: 1px solid {glass_border};
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 8px;
        color: {text_secondary};
        font-family: 'Outfit', sans-serif;
        font-weight: 500;
    }}
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, {accent}, {accent2}) !important;
        color: white !important;
    }}

    /* ── Animations ── */
    @keyframes fadeInUp {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    .fade-in {{ animation: fadeInUp 0.5s ease forwards; }}

    @keyframes pulse-glow {{
        0%, 100% {{ box-shadow: 0 0 8px {accent}44; }}
        50% {{ box-shadow: 0 0 20px {accent}88; }}
    }}
    .pulse {{ animation: pulse-glow 2s infinite; }}

    /* ── Scrollbar ── */
    ::-webkit-scrollbar {{ width: 6px; }}
    ::-webkit-scrollbar-track {{ background: {bg_primary}; }}
    ::-webkit-scrollbar-thumb {{ background: {accent}66; border-radius: 3px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: {accent}; }}
    </style>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────────────────
def init_session_state():
    defaults = {
        "dark_mode": True,
        "page": "🏠 Dashboard",
        "chat_history": [],
        "bookmarks": [],
        "user_profile": {
            "name": "", "cgpa": 3.0, "field": "", "year": "3rd Year",
            "country": "", "ielts": 6.5, "research": "none", "leadership": "none", "sop_ready": False
        },
        "api_keys": {"gemini": "", "groq": ""},
        "cv_analysis": None,
        "sop_result": None,
        "interview_question": None,
        "interview_history": [],
        "roadmap_generated": False,
        "rejection_result": None,
        "checklist": {
            "Transcripts Ordered": False, "IELTS Registered": False,
            "3 Referees Contacted": False, "SOP First Draft": False,
            "CV Updated": False, "Personal Statement Edited": False,
            "Financial Documents Ready": False, "Research Proposal Done": False
        },
        "ai_engine": None,
        "data_manager": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ─────────────────────────────────────────────────────────
# ENGINE FACTORY
# ─────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def get_engine(gemini_key: str, groq_key: str) -> AIEngine:
    return AIEngine(gemini_key=gemini_key, groq_key=groq_key)

@st.cache_resource(show_spinner=False)
def get_data_manager() -> DataManager:
    base = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base, "data", "scholarships.csv")
    return DataManager(csv_path=csv_path)


# ─────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        # Logo
        st.markdown("""
        <div style="text-align:center; padding: 10px 0 20px;">
            <div style="font-size: 2.5rem;">🎓</div>
            <div style="font-size: 1.3rem; font-weight: 800; background: linear-gradient(135deg, #3B82F6, #8B5CF6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">ScholarAI Elite</div>
            <div style="font-size: 0.72rem; color: #64748B; margin-top: 2px; letter-spacing: 0.1em;">AI SCHOLARSHIP INTELLIGENCE</div>
        </div>
        """, unsafe_allow_html=True)

        # Dark/Light Mode Toggle
        col1, col2 = st.columns([3, 2])
        with col1:
            st.caption("Theme")
        with col2:
            dark = st.toggle("🌙", value=st.session_state.dark_mode, key="theme_toggle")
            st.session_state.dark_mode = dark

        st.divider()

        # Navigation
        nav_items = [
            ("🏠", "Dashboard"),
            ("🔍", "Scholarships"),
            ("🤖", "AI Chat"),
            ("📄", "CV Analyzer"),
            ("✍️", "SOP Improve"),
            ("🗺️", "Roadmap"),
            ("⚠️", "Rejection Sim"),
            ("🎤", "IELTS Prep"),
            ("🎯", "Interview Prep"),
            ("📊", "Compare"),
            ("🔖", "Bookmarks"),
            ("⚙️", "Settings"),
        ]

        current = st.session_state.get("page", "🏠 Dashboard")

        for icon, label in nav_items:
            full = f"{icon} {label}"
            selected = current == full
            btn_style = "primary" if selected else "secondary"
            if st.button(f"  {icon}  {label}", key=f"nav_{label}", use_container_width=True,
                        type="primary" if selected else "secondary"):
                st.session_state.page = full
                st.rerun()

        st.divider()

        # Profile Strength
        dm = get_data_manager()
        ps = dm.calculate_profile_strength(st.session_state.user_profile)
        score = ps.get('score', 0)
        strength = ps.get('strength', '🔴 Weak')

        st.markdown(f"**Profile Strength:** {strength}")
        st.progress(score / 100)
        st.caption(f"{score}% Complete — {len(ps.get('missing', []))} areas to improve")

        if ps.get('missing'):
            with st.expander("📌 Missing Items", expanded=False):
                for m in ps.get('missing', []):
                    st.caption(f"• {m}")

        st.divider()
        st.caption(f"📌 {len(st.session_state.bookmarks)} Bookmarked")
        st.caption(f"💬 {len(st.session_state.chat_history)} Messages")


# ─────────────────────────────────────────────────────────
# PAGE: DASHBOARD
# ─────────────────────────────────────────────────────────
def page_dashboard():
    st.markdown("""
    <div class="hero-header fade-in">
        <h1 class="hero-title">ScholarAI Elite</h1>
        <p class="hero-subtitle">🤖 AI-Powered International Scholarship Intelligence Platform</p>
        <p style="color: #64748B; font-size: 0.85rem; margin-top: 8px;">
            Powered by Gemini 1.5 Pro • Groq Llama3 • Advanced Analytics
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Quick Profile Setup
    with st.expander("⚡ Quick Profile Setup", expanded=not st.session_state.user_profile.get('name')):
        c1, c2, c3 = st.columns(3)
        with c1:
            name = st.text_input("Your Name", value=st.session_state.user_profile.get('name', ''), placeholder="Enter your name")
            cgpa = st.number_input("CGPA (out of 4.0)", 0.0, 4.0, float(st.session_state.user_profile.get('cgpa', 3.0)), 0.1)
        with c2:
            field = st.selectbox("Field of Study", ["", "Computer Science", "Engineering", "Business", "Biology", "Medicine", "Arts", "Economics", "Law", "Education"])
            year = st.selectbox("Current Year", ["1st Year", "2nd Year", "3rd Year", "4th Year", "Graduate", "Working Professional"])
        with c3:
            ielts = st.number_input("IELTS Score", 0.0, 9.0, float(st.session_state.user_profile.get('ielts', 6.5)), 0.5)
            target_country = st.selectbox("Target Country", ["", "USA", "UK", "Germany", "Australia", "Canada", "Japan", "Sweden", "Netherlands"])

        col_a, col_b = st.columns(2)
        with col_a:
            research = st.selectbox("Research Experience", ["none", "minimal", "coursework projects", "published paper", "multiple publications"])
        with col_b:
            leadership = st.selectbox("Leadership Experience", ["none", "minimal", "club member", "club officer", "founded organization"])

        if st.button("💾 Save Profile", use_container_width=True):
            st.session_state.user_profile.update({
                "name": name, "cgpa": cgpa, "field": field, "year": year,
                "ielts": ielts, "country": target_country,
                "research": research, "leadership": leadership
            })
            st.success("✅ Profile saved! Your AI recommendations are now personalized.")
            st.rerun()

    # Metrics Row
    dm = get_data_manager()
    scholarships_df = dm.df
    total = len(scholarships_df)
    bookmarked = len(st.session_state.bookmarks)

    # Count upcoming deadlines
    now = pd.Timestamp.now()
    upcoming = 0
    try:
        if 'deadline' in scholarships_df.columns:
            upcoming = int((scholarships_df['deadline'] > now).sum())
    except Exception:
        upcoming = total

    ps = dm.calculate_profile_strength(st.session_state.user_profile)

    cols = st.columns(4)
    metrics = [
        (str(total), "Scholarships Available", "🏆"),
        (str(upcoming), "Open Deadlines", "📅"),
        (str(bookmarked), "Bookmarked", "🔖"),
        (f"{ps.get('score', 0)}%", "Profile Strength", "💪"),
    ]
    for i, (val, label, icon) in enumerate(metrics):
        with cols[i]:
            st.markdown(f"""
            <div class="metric-card fade-in">
                <div style="font-size:1.5rem; margin-bottom:4px;">{icon}</div>
                <div class="metric-value">{val}</div>
                <div class="metric-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Feature Grid
    st.markdown('<div class="section-header">🚀 Quick Access</div>', unsafe_allow_html=True)

    features = [
        ("🤖 AI Chat", "Context-aware scholarship advisor", "AI Chat"),
        ("📄 CV Analyzer", "ATS scoring + 5 improvement tips", "CV Analyzer"),
        ("✍️ SOP Improve", "Rewrite SOP with high-impact tone", "SOP Improve"),
        ("🗺️ Roadmap", "12-month personalized plan", "Roadmap"),
        ("⚠️ Rejection Sim", "Find your rejection risk factors", "Rejection Sim"),
        ("🎤 IELTS Prep", "Mock prompts + band scoring tips", "IELTS Prep"),
        ("🎯 Interview Prep", "Simulated Q&A with AI scoring", "Interview Prep"),
        ("📊 Compare", "Side-by-side scholarship comparison", "Compare"),
    ]

    for row_start in range(0, len(features), 4):
        cols = st.columns(4)
        for i, (icon_label, desc, page_key) in enumerate(features[row_start:row_start+4]):
            with cols[i]:
                st.markdown(f"""
                <div class="glass-card" style="min-height:100px; cursor:pointer;">
                    <div style="font-size:1.3rem; font-weight:700; margin-bottom:6px;">{icon_label}</div>
                    <div style="font-size:0.82rem; color:#94A3B8;">{desc}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Open", key=f"quick_{page_key}", use_container_width=True):
                    icon = icon_label.split()[0]
                    st.session_state.page = f"{icon} {page_key}"
                    st.rerun()

    # Application Checklist
    st.markdown('<div class="section-header">✅ Application Checklist</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    items = list(st.session_state.checklist.items())
    for i, (item, done) in enumerate(items):
        col = c1 if i < len(items)//2 else c2
        with col:
            new_val = st.checkbox(item, value=done, key=f"check_{item}")
            st.session_state.checklist[item] = new_val

    done_count = sum(1 for v in st.session_state.checklist.values() if v)
    total_checks = len(st.session_state.checklist)
    st.progress(done_count / total_checks)
    st.caption(f"📋 {done_count}/{total_checks} tasks completed")

    # Scholarship Timeline Visual
    st.markdown('<div class="section-header">📅 Scholarship Success Timeline</div>', unsafe_allow_html=True)
    timeline_steps = [
        ("Research Phase", "Identify 5-8 target scholarships aligned with your profile and goals", "Month 1-2"),
        ("Profile Building", "Strengthen CGPA, get IELTS 7+, build research portfolio", "Month 3-5"),
        ("Document Prep", "SOP, CV, transcripts, recommendation letters from strong referees", "Month 6-7"),
        ("Application Submission", "Submit applications before deadlines with proofreaded documents", "Month 8-10"),
        ("Interview Preparation", "Practice common questions, research committee members", "Month 10-11"),
        ("Decision & Acceptance", "Receive offers, negotiate terms, prepare for relocation", "Month 12"),
    ]

    for i, (title, detail, timing) in enumerate(timeline_steps):
        done_pct = i / len(timeline_steps)
        color = "#10B981" if done_pct < 0.3 else ("#F59E0B" if done_pct < 0.7 else "#3B82F6")
        st.markdown(f"""
        <div class="stepper-item fade-in">
            <div class="step-number" style="background: {color};">{i+1}</div>
            <div class="step-content">
                <div class="step-title">{title} <span style="font-size:0.75rem; color:#64748B; font-weight:400; margin-left:8px;">📅 {timing}</span></div>
                <div class="step-detail">{detail}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
# PAGE: SCHOLARSHIPS DATABASE
# ─────────────────────────────────────────────────────────
def page_scholarships():
    st.markdown('<div class="section-header">🔍 Scholarship Database</div>', unsafe_allow_html=True)

    dm = get_data_manager()

    # Filters
    with st.expander("🔧 Advanced Filters", expanded=True):
        f1, f2, f3, f4, f5 = st.columns(5)
        with f1:
            country_filter = st.selectbox("Country", dm.get_countries(), key="filter_country")
        with f2:
            field_filter = st.selectbox("Field", dm.get_fields(), key="filter_field")
        with f3:
            degree_filter = st.selectbox("Degree", dm.get_degrees(), key="filter_degree")
        with f4:
            gpa_filter = st.slider("My CGPA", 0.0, 4.0, float(st.session_state.user_profile.get('cgpa', 3.0)), 0.1, key="filter_gpa")
        with f5:
            search_q = st.text_input("🔍 Search", placeholder="e.g. STEM, Europe...", key="filter_search")

    filtered = dm.filter_scholarships(country_filter, field_filter, degree_filter, gpa_filter, search_q)

    st.markdown(f"**Found {len(filtered)} scholarships** matching your criteria")

    if filtered.empty:
        st.info("No scholarships match your current filters. Try broadening your search.")
        return

    for idx, row in filtered.iterrows():
        name = row.get('name', 'Unknown')
        country = row.get('country', 'N/A')
        field = row.get('field', 'N/A')
        amount = row.get('amount', 'N/A')
        deadline = row.get('deadline', None)
        gpa_req = row.get('gpa required', 'N/A')
        lang_req = row.get('language requirement', 'N/A')
        description = row.get('description', '')
        url = row.get('url', '#')
        success = row.get('success rate', 'N/A')
        degree = row.get('degree', 'N/A')

        badge_text, badge_color, days = dm.get_deadline_status(deadline)
        badge_class = f"badge-{badge_color}"

        is_bookmarked = name in st.session_state.bookmarks

        with st.container():
            st.markdown(f"""
            <div class="scholar-card fade-in">
                <div style="display:flex; align-items:flex-start; justify-content:space-between; flex-wrap:wrap; gap:8px;">
                    <div>
                        <div style="font-size:1.1rem; font-weight:700;">{name}</div>
                        <div style="font-size:0.82rem; color:#94A3B8; margin-top:2px;">
                            🌍 {country} &nbsp;|&nbsp; 📚 {field} &nbsp;|&nbsp; 🎓 {degree}
                        </div>
                    </div>
                    <span class="{badge_class}">{badge_text}</span>
                </div>
                <div style="margin-top:10px; font-size:0.85rem; color:#CBD5E1;">{description}</div>
                <div style="display:flex; gap:20px; margin-top:12px; flex-wrap:wrap;">
                    <span style="font-size:0.82rem;">💰 <b>{amount}</b></span>
                    <span style="font-size:0.82rem;">📊 GPA: <b>{gpa_req}+</b></span>
                    <span style="font-size:0.82rem;">🗣️ <b>{lang_req}</b></span>
                    <span style="font-size:0.82rem;">✅ Success: <b>{success}</b></span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            col_a, col_b, col_c = st.columns([2, 1, 1])
            with col_a:
                st.markdown(f"🔗 [Visit Official Website]({url})")
            with col_b:
                bm_label = "❤️ Bookmarked" if is_bookmarked else "🔖 Bookmark"
                if st.button(bm_label, key=f"bm_{idx}_{name}", use_container_width=True):
                    if is_bookmarked:
                        st.session_state.bookmarks.remove(name)
                    else:
                        st.session_state.bookmarks.append(name)
                    st.rerun()
            with col_c:
                if st.button("📤 Export", key=f"export_{idx}_{name}", use_container_width=True):
                    pdf_bytes = dm.export_to_pdf(
                        f"Scholarship: {name}",
                        [
                            {"heading": "Overview", "body": f"Country: {country}\nField: {field}\nDegree: {degree}\nAmount: {amount}"},
                            {"heading": "Requirements", "body": f"GPA Required: {gpa_req}+\nLanguage: {lang_req}\nSuccess Rate: {success}"},
                            {"heading": "Description", "body": description},
                            {"heading": "Apply", "body": f"Official URL: {url}"},
                        ]
                    )
                    st.download_button(
                        "⬇️ Download PDF",
                        pdf_bytes,
                        f"{name.replace(' ', '_')}_info.pdf",
                        "application/pdf",
                        key=f"dl_{idx}_{name}"
                    )


# ─────────────────────────────────────────────────────────
# PAGE: AI CHAT
# ─────────────────────────────────────────────────────────
def page_ai_chat():
    st.markdown('<div class="section-header">🤖 AI Scholar Assistant</div>', unsafe_allow_html=True)

    engine = get_engine(
        st.session_state.api_keys.get('gemini', ''),
        st.session_state.api_keys.get('groq', '')
    )

    # Career path quick buttons
    st.markdown("**💡 Quick Questions:**")
    q_cols = st.columns(4)
    quick_qs = [
        "What scholarships suit my CGPA?",
        "How do I write a winning SOP?",
        "Best countries for Computer Science?",
        "How to get strong reference letters?",
    ]
    for i, q in enumerate(quick_qs):
        with q_cols[i]:
            if st.button(q, key=f"quick_q_{i}", use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "content": q})
                with st.spinner("AI is thinking..."):
                    reply = engine.chat_response(q, st.session_state.user_profile, st.session_state.chat_history)
                st.session_state.chat_history.append({"role": "assistant", "content": reply})
                st.rerun()

    st.divider()

    # Chat display
    chat_container = st.container()
    with chat_container:
        if not st.session_state.chat_history:
            st.markdown("""
            <div class="glass-card" style="text-align:center; padding:40px;">
                <div style="font-size:3rem; margin-bottom:12px;">🤖</div>
                <div style="font-size:1.1rem; font-weight:600; margin-bottom:8px;">Hello! I'm ScholarAI Elite</div>
                <div style="color:#94A3B8; font-size:0.9rem;">Ask me anything about scholarships, career paths, SOPs, or your application strategy. I'm powered by Groq Llama3 + Gemini 1.5 Pro.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for msg in st.session_state.chat_history:
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                if role == "user":
                    st.markdown(f'<div class="chat-msg-user">👤 {content}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-msg-ai">🤖 {content}</div>', unsafe_allow_html=True)

    # Input
    with st.form("chat_form", clear_on_submit=True):
        c1, c2 = st.columns([6, 1])
        with c1:
            user_input = st.text_input("Message ScholarAI...", placeholder="e.g. What career paths suit Computer Science students targeting UK?", label_visibility="collapsed")
        with c2:
            submitted = st.form_submit_button("Send →", use_container_width=True)

    if submitted and user_input.strip():
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.spinner("🧠 ScholarAI is thinking..."):
            reply = engine.chat_response(user_input, st.session_state.user_profile, st.session_state.chat_history)
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.rerun()

    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()

        # Export chat
        dm = get_data_manager()
        sections = [{"heading": f"{m['role'].title()} ({i+1})", "body": m.get('content', '')}
                   for i, m in enumerate(st.session_state.chat_history)]
        pdf = dm.export_to_pdf("AI Chat History", sections)
        st.download_button("📥 Export Chat as PDF", pdf, "scholar_chat.pdf", "application/pdf", key="export_chat_pdf")


# ─────────────────────────────────────────────────────────
# PAGE: CV ANALYZER
# ─────────────────────────────────────────────────────────
def page_cv_analyzer():
    st.markdown('<div class="section-header">📄 CV Analyzer & ATS Scorer</div>', unsafe_allow_html=True)

    engine = get_engine(
        st.session_state.api_keys.get('gemini', ''),
        st.session_state.api_keys.get('groq', '')
    )

    tab1, tab2 = st.tabs(["📤 Upload & Analyze", "📊 Results"])

    with tab1:
        st.markdown("""
        <div class="glass-card">
            <h4>How it works</h4>
            <p style="color:#94A3B8; font-size:0.9rem;">Upload your CV/Resume as PDF or paste the text directly. Our AI will analyze it for ATS compatibility, identify 5 critical weaknesses, and suggest specific improvements to maximize your scholarship chances.</p>
        </div>
        """, unsafe_allow_html=True)

        upload_method = st.radio("Input Method", ["📁 Upload PDF", "📋 Paste Text"], horizontal=True)
        cv_text = ""

        if upload_method == "📁 Upload PDF":
            uploaded = st.file_uploader("Upload your CV/Resume (PDF)", type=["pdf"])
            if uploaded:
                with st.spinner("📖 Extracting text from PDF..."):
                    cv_text = extract_text_from_pdf(uploaded)
                if cv_text:
                    st.success("✅ Text extracted successfully!")
                    with st.expander("Preview Extracted Text"):
                        st.text(cv_text[:1500] + ("..." if len(cv_text) > 1500 else ""))
        else:
            cv_text = st.text_area(
                "Paste your CV text here",
                height=300,
                placeholder="Paste your full CV/Resume content here...\n\nInclude: Education, Experience, Skills, Publications, etc."
            )

        if cv_text and st.button("🔍 Analyze My CV", use_container_width=True):
            with st.spinner("🤖 AI is analyzing your CV... This may take 15-30 seconds."):
                result = engine.analyze_cv(cv_text)
                st.session_state.cv_analysis = result
            st.success("✅ Analysis complete! Check the Results tab.")
            st.rerun()

    with tab2:
        result = st.session_state.cv_analysis
        if not result:
            st.info("👈 Upload or paste your CV in the first tab to see results here.")
            return

        ats = result.get('ats_score', 0)
        grade = result.get('grade', 'N/A')
        assessment = result.get('assessment', '')

        # Score Display
        score_color = "#EF4444" if ats < 50 else ("#F59E0B" if ats < 70 else "#10B981")
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.markdown(f"""
            <div class="glass-card" style="text-align:center; border: 2px solid {score_color}44;">
                <div style="font-size:0.85rem; color:#94A3B8; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:8px;">ATS Compatibility Score</div>
                <div style="font-size:4rem; font-weight:800; color:{score_color}; line-height:1;">{ats}</div>
                <div style="font-size:1.5rem; font-weight:600; color:{score_color}; margin-top:4px;">Grade: {grade}</div>
                <div style="margin-top:12px; font-size:0.88rem; color:#CBD5E1;">{assessment}</div>
            </div>
            """, unsafe_allow_html=True)

        st.progress(ats / 100)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 🚨 5 Key Weaknesses")
            for i, w in enumerate(result.get('weaknesses', []), 1):
                st.markdown(f"""
                <div class="glass-card" style="border-left: 3px solid #EF4444; margin: 6px 0; padding: 12px 16px;">
                    <span style="color:#EF4444; font-weight:700;">{i}.</span> {w}
                </div>
                """, unsafe_allow_html=True)

        with c2:
            st.markdown("### ✅ Recommended Improvements")
            for i, imp in enumerate(result.get('improvements', []), 1):
                st.markdown(f"""
                <div class="glass-card" style="border-left: 3px solid #10B981; margin: 6px 0; padding: 12px 16px;">
                    <span style="color:#10B981; font-weight:700;">{i}.</span> {imp}
                </div>
                """, unsafe_allow_html=True)

        c3, c4 = st.columns(2)
        with c3:
            st.markdown("**✅ Sections Found:**")
            for s in result.get('sections_found', []):
                st.markdown(f"✅ {s}")
        with c4:
            st.markdown("**❌ Missing Sections:**")
            for s in result.get('sections_missing', []):
                st.markdown(f"❌ {s}")

        st.markdown("**🔑 Missing Keywords:**")
        kws = result.get('missing_keywords', [])
        st.markdown("  ".join([f'<code style="background:#3B82F622; padding:3px 8px; border-radius:4px; border:1px solid #3B82F644;">{k}</code>' for k in kws]), unsafe_allow_html=True)

        # Export
        dm = get_data_manager()
        sections = [
            {"heading": "ATS Score & Grade", "body": f"Score: {ats}/100\nGrade: {grade}\nAssessment: {assessment}"},
            {"heading": "Key Weaknesses", "body": "\n".join(f"{i}. {w}" for i, w in enumerate(result.get('weaknesses', []), 1))},
            {"heading": "Recommended Improvements", "body": "\n".join(f"{i}. {w}" for i, w in enumerate(result.get('improvements', []), 1))},
            {"heading": "Missing Keywords", "body": ", ".join(result.get('missing_keywords', []))},
        ]
        pdf = dm.export_to_pdf("CV Analysis Report", sections)
        st.download_button("📥 Export Analysis as PDF", pdf, "cv_analysis.pdf", "application/pdf", key="cv_pdf_export")


# ─────────────────────────────────────────────────────────
# PAGE: SOP IMPROVE
# ─────────────────────────────────────────────────────────
def page_sop_improve():
    st.markdown('<div class="section-header">✍️ SOP Improve AI</div>', unsafe_allow_html=True)

    engine = get_engine(
        st.session_state.api_keys.get('gemini', ''),
        st.session_state.api_keys.get('groq', '')
    )

    st.markdown("""
    <div class="glass-card">
        <h4>🚀 High-Impact SOP Rewriter</h4>
        <p style="color:#94A3B8; font-size:0.9rem;">Paste your Statement of Purpose and let AI transform it into a compelling, high-impact narrative that stands out to scholarship committees.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        target_scholarship = st.text_input("Target Scholarship (optional)", placeholder="e.g., Chevening Scholarship 2025")
    with c2:
        sop_focus = st.selectbox("Focus Area", ["Overall Quality", "Research Focus", "Leadership Emphasis", "Community Impact", "Career Vision"])

    original_sop = st.text_area(
        "📝 Your Original SOP",
        height=300,
        placeholder="Paste your current Statement of Purpose here...\n\nTip: Include your background, motivation, goals, and why you chose this program."
    )

    if original_sop and len(original_sop) > 100:
        if st.button("🚀 Rewrite for High Impact", use_container_width=True):
            with st.spinner("✍️ AI is rewriting your SOP with high-impact language..."):
                result = engine.rewrite_sop(original_sop, target_scholarship)
                st.session_state.sop_result = result
            st.rerun()
    elif original_sop:
        st.warning("Please paste a more complete SOP (at least 100 characters) for best results.")

    result = st.session_state.sop_result
    if result:
        st.markdown("---")
        # Score comparison
        before = result.get('score_before', 0)
        after = result.get('score_after', 0)
        improvement = after - before

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""<div class="metric-card"><div class="metric-value" style="color:#EF4444;">{before}</div><div class="metric-label">Impact Score Before</div></div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class="metric-card"><div class="metric-value" style="color:#10B981;">{after}</div><div class="metric-label">Impact Score After</div></div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""<div class="metric-card"><div class="metric-value" style="color:#3B82F6;">+{improvement}</div><div class="metric-label">Improvement</div></div>""", unsafe_allow_html=True)

        st.markdown("### ✨ AI-Rewritten High-Impact SOP")
        rewritten = result.get('rewritten_sop', '')
        st.markdown(f"""
        <div class="glass-card" style="border-left: 4px solid #10B981;">
            <div style="white-space: pre-wrap; font-size:0.95rem; line-height:1.7; color:#E2E8F0;">{rewritten}</div>
        </div>
        """, unsafe_allow_html=True)

        st.text_area("Copy Rewritten SOP", rewritten, height=250)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**🔄 Changes Made:**")
            for c in result.get('changes', []):
                st.markdown(f"✅ {c}")
        with c2:
            st.markdown("**💡 Further Suggestions:**")
            for s in result.get('suggestions', []):
                st.markdown(f"→ {s}")

        # Export
        dm = get_data_manager()
        pdf = dm.export_to_pdf("SOP Improvement Report", [
            {"heading": "Impact Score Analysis", "body": f"Before: {before}/100\nAfter: {after}/100\nImprovement: +{improvement} points"},
            {"heading": "Rewritten High-Impact SOP", "body": rewritten},
            {"heading": "Key Changes", "body": "\n".join(result.get('changes', []))},
            {"heading": "Further Suggestions", "body": "\n".join(result.get('suggestions', []))},
        ])
        st.download_button("📥 Export SOP Report", pdf, "sop_improvement.pdf", "application/pdf", key="sop_pdf")


# ─────────────────────────────────────────────────────────
# PAGE: ROADMAP
# ─────────────────────────────────────────────────────────
def page_roadmap():
    st.markdown('<div class="section-header">🗺️ Full Scholarship Roadmap</div>', unsafe_allow_html=True)

    engine = get_engine(
        st.session_state.api_keys.get('gemini', ''),
        st.session_state.api_keys.get('groq', '')
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        current_year = st.selectbox("Your Current Year", ["1st Year", "2nd Year", "3rd Year", "4th Year", "Graduate", "Working Professional"])
    with c2:
        target_degree = st.selectbox("Target Degree", ["Masters", "PhD", "Postdoctoral", "MBA", "LLM"])
    with c3:
        target_year = st.selectbox("Target Start Year", ["2025", "2026", "2027"])

    field = st.session_state.user_profile.get('field', '') or st.text_input("Field of Study", placeholder="e.g. Computer Science")

    if st.button("🗺️ Generate My Personalized Roadmap", use_container_width=True):
        prompt = f"""Create a detailed 12-month scholarship application roadmap for:
- Current Year: {current_year}
- Field: {field or 'General'}
- Target Degree: {target_degree}
- Target Start: {target_year}
- CGPA: {st.session_state.user_profile.get('cgpa', 3.0)}
- IELTS: {st.session_state.user_profile.get('ielts', 6.5)}

Create a month-by-month plan with specific, actionable tasks. Focus on scholarship applications, profile building, and documentation. Format as numbered monthly steps."""

        with st.spinner("🤖 Generating your personalized roadmap..."):
            roadmap_text = engine.groq_chat(prompt, max_tokens=1800)
            st.session_state.roadmap_text = roadmap_text
            st.session_state.roadmap_generated = True

    if st.session_state.get('roadmap_text'):
        roadmap = st.session_state.roadmap_text

        st.markdown(f"""
        <div class="glass-card" style="border-left: 4px solid #3B82F6;">
            <div style="white-space: pre-wrap; font-size:0.92rem; line-height:1.75; color:#E2E8F0;">{roadmap}</div>
        </div>
        """, unsafe_allow_html=True)

        dm = get_data_manager()
        pdf = dm.export_to_pdf(
            f"12-Month Scholarship Roadmap — {current_year} to {target_degree}",
            [{"heading": "Your Personalized Roadmap", "body": roadmap}]
        )
        st.download_button("📥 Download Roadmap PDF", pdf, "scholarship_roadmap.pdf", "application/pdf", key="roadmap_pdf")
    else:
        # Show default roadmap
        st.markdown("""
        <div class="section-header" style="font-size:1.1rem;">📋 Standard 12-Month Framework</div>
        """, unsafe_allow_html=True)

        months = [
            ("Jan-Feb", "Research & Target", "Identify 8-10 target scholarships, research requirements, create tracking spreadsheet"),
            ("Mar-Apr", "Profile Assessment", "Run CV analysis, IELTS preparation, identify research opportunities"),
            ("May-Jun", "Skill Building", "Take IELTS/TOEFL, attend workshops, join research projects, build portfolio"),
            ("Jul-Aug", "Document Creation", "Write SOP first draft, update CV, contact potential referees"),
            ("Sep-Oct", "Review & Refine", "Get SOP reviewed, refine CV with mentor feedback, prepare reference letter briefs"),
            ("Nov-Dec", "Application Submission", "Submit applications before deadlines, prepare interview responses"),
        ]

        for i, (period, phase, tasks) in enumerate(months):
            colors = ["#3B82F6", "#8B5CF6", "#06B6D4", "#10B981", "#F59E0B", "#EF4444"]
            color = colors[i]
            st.markdown(f"""
            <div class="stepper-item fade-in">
                <div class="step-number" style="background:{color};">{i+1}</div>
                <div class="step-content">
                    <div class="step-title">{period} — {phase}</div>
                    <div class="step-detail">{tasks}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
# PAGE: REJECTION SIMULATOR
# ─────────────────────────────────────────────────────────
def page_rejection_sim():
    st.markdown('<div class="section-header">⚠️ Rejection Reason Simulator</div>', unsafe_allow_html=True)

    engine = get_engine(
        st.session_state.api_keys.get('gemini', ''),
        st.session_state.api_keys.get('groq', '')
    )

    st.markdown("""
    <div class="glass-card" style="border: 1px solid #EF444433; background: rgba(239,68,68,0.05);">
        <h4>🚨 AI Rejection Risk Analysis</h4>
        <p style="color:#94A3B8; font-size:0.9rem;">Our AI analyzes your profile against real scholarship selection criteria to predict why you might get rejected — so you can fix issues BEFORE submitting.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        cgpa = st.number_input("Your CGPA", 0.0, 4.0, float(st.session_state.user_profile.get('cgpa', 3.0)), 0.1)
        ielts = st.number_input("IELTS Score", 0.0, 9.0, float(st.session_state.user_profile.get('ielts', 6.5)), 0.5)
    with c2:
        research = st.selectbox("Research Experience", ["none", "minimal", "coursework projects", "conference paper", "published paper", "multiple publications"])
        leadership = st.selectbox("Leadership", ["none", "minimal", "club member", "club officer", "founded organization"])
    with c3:
        target_scholarship = st.text_input("Target Scholarship", placeholder="e.g., Chevening, Fulbright")
        sop_written = st.selectbox("SOP Status", ["Not started", "First draft", "Reviewed draft", "Final version"])

    if st.button("🔍 Analyze My Rejection Risk", use_container_width=True):
        profile = {
            "cgpa": cgpa, "ielts": ielts, "research": research,
            "leadership": leadership, "target_scholarship": target_scholarship,
            "sop": sop_written
        }
        with st.spinner("🔬 AI is analyzing your rejection risks..."):
            result = engine.simulate_rejection(profile)
            st.session_state.rejection_result = result
        st.rerun()

    result = st.session_state.rejection_result
    if result:
        prob = result.get('success_probability', 0)
        verdict = result.get('verdict', 'Unknown')
        verdict_color = "#EF4444" if "High Risk" in verdict else ("#F59E0B" if "Medium" in verdict else "#10B981")

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""<div class="metric-card"><div class="metric-value" style="color:{verdict_color};">{prob}%</div><div class="metric-label">Success Probability</div></div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class="metric-card"><div class="metric-value" style="font-size:1.2rem; color:{verdict_color};">{verdict}</div><div class="metric-label">Risk Level</div></div>""", unsafe_allow_html=True)
        with c3:
            timeline = result.get('estimated_timeline', 'N/A')
            st.markdown(f"""<div class="metric-card"><div class="metric-value" style="font-size:1rem;">{timeline}</div><div class="metric-label">Est. Timeline to Competitive</div></div>""", unsafe_allow_html=True)

        st.progress(prob / 100)

        st.markdown("### 🚨 Identified Risk Factors")
        risks = result.get('risks', [])
        for i, risk in enumerate(risks):
            severity = risk.get('severity', 'Medium')
            sev_color = "#EF4444" if severity == "High" else ("#F59E0B" if severity == "Medium" else "#10B981")
            st.markdown(f"""
            <div class="glass-card" style="border-left: 4px solid {sev_color}; margin: 8px 0;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div style="font-weight:700; font-size:0.95rem;">{i+1}. {risk.get('factor', 'Unknown Risk')}</div>
                    <span class="badge-{'red' if severity == 'High' else ('orange' if severity == 'Medium' else 'green')}">{severity} Risk</span>
                </div>
                <div style="color:#94A3B8; font-size:0.85rem; margin-top:8px;">{risk.get('detail', '')}</div>
                <div style="color:#10B981; font-size:0.85rem; margin-top:8px; font-weight:500;">✅ Fix: {risk.get('fix', '')}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="glass-card" style="border: 1px solid #10B98133; background: rgba(16,185,129,0.05);">
            <div style="font-weight:700; margin-bottom:6px;">🎯 Top Priority Action:</div>
            <div style="color:#10B981; font-size:0.95rem;">{result.get('top_recommendation', '')}</div>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
# PAGE: IELTS PREP
# ─────────────────────────────────────────────────────────
def page_ielts_prep():
    st.markdown('<div class="section-header">🎤 IELTS / TOEFL Prep Module</div>', unsafe_allow_html=True)

    engine = get_engine(
        st.session_state.api_keys.get('gemini', ''),
        st.session_state.api_keys.get('groq', '')
    )

    tab1, tab2, tab3 = st.tabs(["🎤 Speaking Mock", "📝 Writing Tips", "📊 Score Calculator"])

    with tab1:
        st.markdown("""
        <div class="glass-card">
            <h4>Speaking Mock Prompt Generator</h4>
            <p style="color:#94A3B8; font-size:0.9rem;">Get AI-generated IELTS Speaking prompts for Parts 1, 2, and 3. Practice under timed conditions and get band scoring guidance.</p>
        </div>
        """, unsafe_allow_html=True)

        part = st.selectbox("IELTS Speaking Part", ["Part 2 (Long Turn)", "Part 1 (Introduction)", "Part 3 (Discussion)"])
        topic_area = st.selectbox("Topic Area", ["Random", "Education", "Technology", "Environment", "Culture", "Work & Career", "Health", "Society"])

        if st.button("🎲 Generate Mock Prompt", use_container_width=True):
            prompt_req = f"Generate an IELTS Speaking {part} mock prompt for topic: {topic_area}. Include the prompt, what to say, timing guidance, and Band 7+ tips."
            with st.spinner("Generating mock prompt..."):
                response = engine.groq_chat(prompt_req, max_tokens=800)
            st.session_state.ielts_prompt = response

        if st.session_state.get('ielts_prompt'):
            st.markdown(f"""
            <div class="glass-card" style="border-left: 4px solid #3B82F6;">
                <div style="white-space: pre-wrap; font-size:0.92rem; line-height:1.7; color:#E2E8F0;">{st.session_state.ielts_prompt}</div>
            </div>
            """, unsafe_allow_html=True)

            practice_answer = st.text_area("📝 Write/Record Your Answer:", height=150, placeholder="Type your practice response here...")
            if practice_answer and st.button("📊 Evaluate My Answer"):
                with st.spinner("Evaluating your answer..."):
                    eval_prompt = f"Evaluate this IELTS Speaking answer for band score. Be specific about strengths and weaknesses.\nPrompt: {st.session_state.ielts_prompt[:300]}\nAnswer: {practice_answer}\nProvide: estimated band score, 3 strengths, 3 improvements."
                    feedback = engine.groq_chat(eval_prompt, max_tokens=600)
                st.markdown(f"""<div class="glass-card">{feedback}</div>""", unsafe_allow_html=True)

    with tab2:
        tips = {
            "Reading": [
                "Skim for main ideas first, then scan for specific answers",
                "Pay attention to qualifying words: 'always', 'never', 'most', 'some'",
                "Practice True/False/Not Given questions — 'Not Given' means info isn't in the text",
                "Manage time: aim for 20 minutes per section",
                "Read questions before the passage to know what to look for"
            ],
            "Writing Task 1": [
                "Always write an overview paragraph summarizing main trends",
                "Use data comparisons: 'significantly higher than', 'a sharp increase'",
                "Avoid copying the question — paraphrase the introduction",
                "Aim for 160-180 words minimum; 200 is safe",
                "Use present tense for graphs showing current trends; past for historical data"
            ],
            "Writing Task 2": [
                "Structure: Introduction → 2 body paragraphs → Conclusion",
                "State your position clearly in the introduction",
                "Each body paragraph: topic sentence + 2 supporting points + example",
                "Use a variety of linking words: 'Furthermore', 'In contrast', 'Consequently'",
                "Aim for 260-290 words; 300+ shows strong command"
            ],
            "Listening": [
                "Read the questions during preview time — predict answer types",
                "Answers appear in order in the audio",
                "Watch for signpost language: 'However', 'Moving on to', 'In conclusion'",
                "Write exactly what you hear — don't change spellings",
                "Transfer answers carefully — spelling errors cost marks"
            ]
        }

        for section, tip_list in tips.items():
            with st.expander(f"📌 {section} Tips", expanded=False):
                for tip in tip_list:
                    st.markdown(f"• {tip}")

    with tab3:
        st.markdown("### 📊 Band Score Estimator")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            r = st.slider("Reading", 1.0, 9.0, 6.5, 0.5)
        with c2:
            w = st.slider("Writing", 1.0, 9.0, 6.0, 0.5)
        with c3:
            ls = st.slider("Listening", 1.0, 9.0, 7.0, 0.5)
        with c4:
            sp = st.slider("Speaking", 1.0, 9.0, 6.5, 0.5)

        overall = round((r + w + ls + sp) / 4 * 2) / 2
        color = "#EF4444" if overall < 6.5 else ("#F59E0B" if overall < 7.0 else "#10B981")

        st.markdown(f"""
        <div class="glass-card" style="text-align:center; border: 2px solid {color}44;">
            <div style="font-size:0.85rem; color:#94A3B8; text-transform:uppercase; letter-spacing:0.1em;">Overall Band Score</div>
            <div style="font-size:4rem; font-weight:800; color:{color}; line-height:1.2;">{overall}</div>
            <div style="font-size:0.9rem; color:#94A3B8; margin-top:8px;">
                {'✅ Meets most scholarship requirements (7.0+)' if overall >= 7.0 else ('⚠️ Meets minimum requirements (6.5)' if overall >= 6.5 else '❌ Below typical scholarship requirements')}
            </div>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
# PAGE: INTERVIEW PREP
# ─────────────────────────────────────────────────────────
def page_interview_prep():
    st.markdown('<div class="section-header">🎯 Interview Prep Mode</div>', unsafe_allow_html=True)

    engine = get_engine(
        st.session_state.api_keys.get('gemini', ''),
        st.session_state.api_keys.get('groq', '')
    )

    interview_questions = [
        "Tell me about yourself and your academic journey.",
        "Why did you choose this specific scholarship?",
        "What is your most significant academic or research achievement?",
        "Where do you see yourself in 10 years?",
        "How will you contribute to your home country after completing your studies?",
        "Describe a time you faced a significant challenge and how you overcame it.",
        "What makes you a better candidate than other applicants?",
        "How does this program align with your long-term career goals?",
        "Describe your research experience and its significance.",
        "What are your three greatest strengths as a scholar?",
    ]

    c1, c2 = st.columns(2)
    with c1:
        scholarship_type = st.selectbox("Interview Style", ["Chevening", "Fulbright", "Gates Cambridge", "Rhodes", "DAAD", "General"])
    with c2:
        mode = st.radio("Mode", ["Practice Individual Questions", "Full Mock Interview"], horizontal=True)

    if mode == "Practice Individual Questions":
        if not st.session_state.interview_question:
            st.session_state.interview_question = random.choice(interview_questions)

        q = st.session_state.interview_question
        st.markdown(f"""
        <div class="glass-card" style="border-left: 4px solid #8B5CF6; padding: 24px;">
            <div style="font-size:0.8rem; color:#94A3B8; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:8px;">Interview Question</div>
            <div style="font-size:1.15rem; font-weight:600; color:#E2E8F0; line-height:1.5;">"{q}"</div>
        </div>
        """, unsafe_allow_html=True)

        user_answer = st.text_area("✍️ Your Answer:", height=150, placeholder="Type your answer here. Aim for 90-120 seconds of spoken response (approximately 200-280 words)...")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("📊 Evaluate My Answer", use_container_width=True) and user_answer:
                with st.spinner("🤖 AI is evaluating your answer..."):
                    evaluation = engine.evaluate_answer(q, user_answer)

                c_a, c_b, c_c, c_d = st.columns(4)
                metrics = [
                    ("Clarity", evaluation.get('clarity', 0), 25),
                    ("Relevance", evaluation.get('relevance', 0), 25),
                    ("Evidence", evaluation.get('evidence', 0), 25),
                    ("Communication", evaluation.get('communication', 0), 25),
                ]
                for col, (label, score, max_s) in zip([c_a, c_b, c_c, c_d], metrics):
                    pct = score / max_s
                    color = "#EF4444" if pct < 0.6 else ("#F59E0B" if pct < 0.8 else "#10B981")
                    with col:
                        st.markdown(f"""<div class="metric-card"><div class="metric-value" style="color:{color};">{score}/{max_s}</div><div class="metric-label">{label}</div></div>""", unsafe_allow_html=True)

                total = evaluation.get('total', 0)
                grade = evaluation.get('grade', 'N/A')
                st.markdown(f"""
                <div class="glass-card" style="text-align:center;">
                    <span style="font-size:2rem; font-weight:800; color:#3B82F6;">{total}/100</span>
                    <span style="font-size:1.2rem; color:#94A3B8; margin-left:12px;">Grade: {grade}</span>
                </div>
                """, unsafe_allow_html=True)

                c_left, c_right = st.columns(2)
                with c_left:
                    st.markdown("**💪 Strengths:**")
                    for s in evaluation.get('strengths', []):
                        st.markdown(f"✅ {s}")
                with c_right:
                    st.markdown("**📈 Improvements:**")
                    for s in evaluation.get('improvements', []):
                        st.markdown(f"→ {s}")

                tip = evaluation.get('model_answer_tip', '')
                if tip:
                    st.info(f"💡 **Tip:** {tip}")

        with c2:
            if st.button("🔄 Next Question", use_container_width=True):
                st.session_state.interview_question = random.choice(interview_questions)
                st.rerun()

    else:  # Full Mock Interview
        if 'mock_interview_qs' not in st.session_state:
            st.session_state.mock_interview_qs = random.sample(interview_questions, 5)
            st.session_state.mock_current = 0
            st.session_state.mock_answers = []

        current_idx = st.session_state.mock_current
        qs = st.session_state.mock_interview_qs

        if current_idx < len(qs):
            progress = current_idx / len(qs)
            st.progress(progress)
            st.caption(f"Question {current_idx + 1} of {len(qs)}")

            q = qs[current_idx]
            st.markdown(f"""
            <div class="glass-card" style="border-left: 4px solid #8B5CF6;">
                <div style="font-size:0.8rem; color:#94A3B8; margin-bottom:8px;">Q{current_idx+1}</div>
                <div style="font-size:1.1rem; font-weight:600;">"{q}"</div>
            </div>
            """, unsafe_allow_html=True)

            answer = st.text_area("Your answer:", height=120, key=f"mock_answer_{current_idx}")

            if st.button("Next →", use_container_width=True) and answer:
                st.session_state.mock_answers.append({"question": q, "answer": answer})
                st.session_state.mock_current += 1
                st.rerun()
        else:
            st.success("🎉 Mock interview complete! Here's your summary:")
            for i, qa in enumerate(st.session_state.mock_answers):
                with st.expander(f"Q{i+1}: {qa['question'][:60]}..."):
                    st.markdown(f"**Your Answer:** {qa['answer']}")

            if st.button("🔄 Restart Interview"):
                st.session_state.mock_interview_qs = random.sample(interview_questions, 5)
                st.session_state.mock_current = 0
                st.session_state.mock_answers = []
                st.rerun()


# ─────────────────────────────────────────────────────────
# PAGE: COMPARE SCHOLARSHIPS
# ─────────────────────────────────────────────────────────
def page_compare():
    st.markdown('<div class="section-header">📊 Compare Scholarships</div>', unsafe_allow_html=True)

    dm = get_data_manager()
    all_names = dm.get_all_names()

    c1, c2 = st.columns(2)
    with c1:
        s1 = st.selectbox("Scholarship A", all_names, key="compare_s1")
    with c2:
        s2_options = [n for n in all_names if n != s1]
        s2 = st.selectbox("Scholarship B", s2_options, key="compare_s2")

    if st.button("⚡ Compare Now", use_container_width=True):
        comparison = dm.compare_scholarships(s1, s2)

        if not comparison:
            st.error("Could not load comparison data. Please try different scholarships.")
            return

        st.markdown(f"""
        <div class="compare-row">
            <div class="compare-label">Criteria</div>
            <div class="compare-header">{s1}</div>
            <div class="compare-header">{s2}</div>
        </div>
        """, unsafe_allow_html=True)

        for key, data in comparison.items():
            label = data.get('label', key)
            val1 = str(data.get(s1, 'N/A'))
            val2 = str(data.get(s2, 'N/A'))

            st.markdown(f"""
            <div class="compare-row">
                <div class="compare-label">{label}</div>
                <div class="compare-val">{val1}</div>
                <div class="compare-val">{val2}</div>
            </div>
            """, unsafe_allow_html=True)

        # Analysis
        st.markdown("---")
        engine = get_engine(
            st.session_state.api_keys.get('gemini', ''),
            st.session_state.api_keys.get('groq', '')
        )
        profile = st.session_state.user_profile
        cgpa = profile.get('cgpa', 3.0)
        ielts = profile.get('ielts', 6.5)
        field = profile.get('field', 'General')

        analysis_prompt = f"""Compare these two scholarships for a student with CGPA {cgpa}, IELTS {ielts}, studying {field}:
1. {s1}
2. {s2}
Give a 3-paragraph analysis covering: which is more competitive, which better matches the profile, and a clear recommendation."""

        with st.spinner("AI is analyzing the best fit for your profile..."):
            analysis = engine.groq_chat(analysis_prompt, max_tokens=600)

        st.markdown(f"""
        <div class="glass-card" style="border-left: 4px solid #06B6D4;">
            <h4>🤖 AI Recommendation for Your Profile</h4>
            <div style="white-space: pre-wrap; font-size:0.92rem; color:#E2E8F0; line-height:1.7;">{analysis}</div>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
# PAGE: BOOKMARKS
# ─────────────────────────────────────────────────────────
def page_bookmarks():
    st.markdown('<div class="section-header">🔖 Bookmarked Scholarships</div>', unsafe_allow_html=True)

    bm = st.session_state.bookmarks
    if not bm:
        st.markdown("""
        <div class="glass-card" style="text-align:center; padding:60px;">
            <div style="font-size:3rem; margin-bottom:12px;">🔖</div>
            <div style="font-size:1.1rem; font-weight:600; margin-bottom:8px;">No bookmarks yet</div>
            <div style="color:#94A3B8; font-size:0.9rem;">Visit the Scholarships page and bookmark programs you're interested in.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    dm = get_data_manager()
    df = dm.df

    for name in bm:
        matching = df[df['name'].str.lower() == name.lower()]
        if matching.empty:
            continue
        row = matching.iloc[0]

        deadline = row.get('deadline', None)
        badge_text, badge_color, days = dm.get_deadline_status(deadline)
        badge_class = f"badge-{badge_color}"

        st.markdown(f"""
        <div class="scholar-card fade-in">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                <div>
                    <div style="font-size:1.1rem; font-weight:700;">{name}</div>
                    <div style="font-size:0.82rem; color:#94A3B8;">🌍 {row.get('country','N/A')} &nbsp;|&nbsp; 💰 {row.get('amount','N/A')} &nbsp;|&nbsp; 📊 GPA {row.get('gpa required','N/A')}+</div>
                </div>
                <span class="{badge_class}">{badge_text}</span>
            </div>
            <div style="margin-top:10px; font-size:0.85rem; color:#CBD5E1;">{row.get('description','')}</div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns([4, 1])
        with c1:
            st.markdown(f"🔗 [Official Website]({row.get('url', '#')})")
        with c2:
            if st.button("❌ Remove", key=f"remove_bm_{name}", use_container_width=True):
                st.session_state.bookmarks.remove(name)
                st.rerun()

    if st.button("📥 Export Bookmarks PDF", use_container_width=True):
        sections = []
        for name in bm:
            matching = df[df['name'].str.lower() == name.lower()]
            if not matching.empty:
                row = matching.iloc[0]
                sections.append({
                    "heading": name,
                    "body": f"Country: {row.get('country','N/A')}\nAmount: {row.get('amount','N/A')}\nGPA Required: {row.get('gpa required','N/A')}+\nLanguage: {row.get('language requirement','N/A')}\nURL: {row.get('url','N/A')}"
                })
        pdf = dm.export_to_pdf("My Bookmarked Scholarships", sections)
        st.download_button("⬇️ Download PDF", pdf, "bookmarked_scholarships.pdf", "application/pdf", key="bm_pdf_dl")


# ─────────────────────────────────────────────────────────
# PAGE: SETTINGS
# ─────────────────────────────────────────────────────────
def page_settings():
    st.markdown('<div class="section-header">⚙️ Settings & API Configuration</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🔑 API Keys", "👤 Profile", "ℹ️ About"])

    with tab1:
        st.markdown("""
        <div class="glass-card">
            <h4>🤖 AI Model Configuration</h4>
            <p style="color:#94A3B8; font-size:0.9rem;">Configure your API keys to enable full AI capabilities. Without keys, ScholarAI Elite uses intelligent fallback logic.</p>
        </div>
        """, unsafe_allow_html=True)

        groq_key = st.text_input(
            "🟢 Groq API Key (Llama3 — Chat & Analysis)",
            value=st.session_state.api_keys.get('groq', ''),
            type="password",
            help="Get your free key at console.groq.com — Powers: Chat, SOP, Interview, Rejection Sim"
        )
        st.caption("🔗 Get free Groq key: https://console.groq.com")

        gemini_key = st.text_input(
            "🔵 Gemini API Key (1.5 Pro — Vision & PDF)",
            value=st.session_state.api_keys.get('gemini', ''),
            type="password",
            help="Get your key at makersuite.google.com — Powers: PDF CV extraction, Vision analysis"
        )
        st.caption("🔗 Get Gemini key: https://makersuite.google.com/app/apikey")

        if st.button("💾 Save API Keys", use_container_width=True):
            st.session_state.api_keys['groq'] = groq_key
            st.session_state.api_keys['gemini'] = gemini_key
            # Clear cached engine to force reinit
            get_engine.clear()
            st.success("✅ API keys saved! AI models are now active.")

        # Model status
        st.markdown("### 🤖 Model Status")
        c1, c2, c3 = st.columns(3)
        with c1:
            groq_status = "✅ Active" if groq_key else "⚠️ Fallback Mode"
            color = "#10B981" if groq_key else "#F59E0B"
            st.markdown(f"""<div class="metric-card"><div style="font-size:1.5rem;">🟢</div><div class="metric-value" style="font-size:1rem; color:{color};">{groq_status}</div><div class="metric-label">Groq Llama3</div></div>""", unsafe_allow_html=True)
        with c2:
            gem_status = "✅ Active" if gemini_key else "⚠️ Not configured"
            color2 = "#10B981" if gemini_key else "#F59E0B"
            st.markdown(f"""<div class="metric-card"><div style="font-size:1.5rem;">🔵</div><div class="metric-value" style="font-size:1rem; color:{color2};">{gem_status}</div><div class="metric-label">Gemini 1.5 Pro</div></div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""<div class="metric-card"><div style="font-size:1.5rem;">🤖</div><div class="metric-value" style="font-size:1rem; color:#10B981;">Always On</div><div class="metric-label">Fallback Logic</div></div>""", unsafe_allow_html=True)

    with tab2:
        st.markdown("### 👤 Your Profile")
        profile = st.session_state.user_profile

        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Full Name", value=profile.get('name', ''))
            cgpa = st.number_input("CGPA", 0.0, 4.0, float(profile.get('cgpa', 3.0)), 0.1)
            field = st.text_input("Field of Study", value=profile.get('field', ''))
            year = st.selectbox("Year", ["1st Year", "2nd Year", "3rd Year", "4th Year", "Graduate", "Working Professional"],
                               index=["1st Year", "2nd Year", "3rd Year", "4th Year", "Graduate", "Working Professional"].index(profile.get('year', '3rd Year')) if profile.get('year') in ["1st Year", "2nd Year", "3rd Year", "4th Year", "Graduate", "Working Professional"] else 2)
        with c2:
            country = st.text_input("Target Country", value=profile.get('country', ''))
            ielts = st.number_input("IELTS Score", 0.0, 9.0, float(profile.get('ielts', 6.5)), 0.5)
            research = st.selectbox("Research", ["none", "minimal", "coursework projects", "conference paper", "published paper", "multiple publications"],
                                   index=0 if not profile.get('research') else ["none", "minimal", "coursework projects", "conference paper", "published paper", "multiple publications"].index(profile.get('research', 'none')) if profile.get('research') in ["none", "minimal", "coursework projects", "conference paper", "published paper", "multiple publications"] else 0)
            leadership = st.selectbox("Leadership", ["none", "minimal", "club member", "club officer", "founded organization"],
                                     index=0 if not profile.get('leadership') else ["none", "minimal", "club member", "club officer", "founded organization"].index(profile.get('leadership', 'none')) if profile.get('leadership') in ["none", "minimal", "club member", "club officer", "founded organization"] else 0)

        sop_ready = st.checkbox("SOP Ready", value=profile.get('sop_ready', False))

        if st.button("💾 Update Profile", use_container_width=True):
            st.session_state.user_profile.update({
                'name': name, 'cgpa': cgpa, 'field': field, 'year': year,
                'country': country, 'ielts': ielts, 'research': research,
                'leadership': leadership, 'sop_ready': sop_ready
            })
            st.success("✅ Profile updated!")
            st.rerun()

    with tab3:
        st.markdown("""
        <div class="glass-card">
            <h2>🎓 ScholarAI Elite</h2>
            <p style="color:#94A3B8;">Enterprise-grade AI scholarship intelligence platform for international aspirants.</p>

            <h4>🤖 AI Models Used:</h4>
            <ul style="color:#94A3B8; font-size:0.9rem;">
                <li><b>Groq Llama3-70B</b> — Chat, SOP rewriting, interview evaluation, rejection analysis</li>
                <li><b>Google Gemini 1.5 Pro</b> — PDF processing, vision analysis, complex reasoning</li>
                <li><b>Intelligent Fallback</b> — Rule-based system when API keys are absent</li>
            </ul>

            <h4>📦 Required Libraries:</h4>
            <div style="font-family: 'Fira Code', monospace; background: rgba(0,0,0,0.3); padding: 12px; border-radius: 8px; font-size:0.82rem; color:#06B6D4;">
            streamlit>=1.28.0<br>
            pandas>=2.0.0<br>
            google-generativeai>=0.3.0<br>
            groq>=0.4.0<br>
            fpdf2>=2.7.0<br>
            pdfplumber>=0.9.0<br>
            streamlit-option-menu>=0.3.0<br>
            streamlit-lottie>=0.0.5<br>
            requests>=2.31.0
            </div>

            <h4 style="margin-top:16px;">🚀 Getting Started:</h4>
            <div style="font-family: 'Fira Code', monospace; background: rgba(0,0,0,0.3); padding: 12px; border-radius: 8px; font-size:0.82rem; color:#10B981;">
            pip install -r requirements.txt<br>
            streamlit run app.py
            </div>

            <p style="color:#64748B; font-size:0.8rem; margin-top:16px;">Version 2.0 | Built with ❤️ for scholarship aspirants worldwide</p>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
# MAIN APP ROUTER
# ─────────────────────────────────────────────────────────
def main():
    init_session_state()
    apply_custom_css(dark_mode=st.session_state.dark_mode)
    render_sidebar()

    page = st.session_state.page

    if "Dashboard" in page:
        page_dashboard()
    elif "Scholarships" in page:
        page_scholarships()
    elif "Chat" in page:
        page_ai_chat()
    elif "CV Analyzer" in page:
        page_cv_analyzer()
    elif "SOP" in page:
        page_sop_improve()
    elif "Roadmap" in page:
        page_roadmap()
    elif "Rejection" in page:
        page_rejection_sim()
    elif "IELTS" in page:
        page_ielts_prep()
    elif "Interview" in page:
        page_interview_prep()
    elif "Compare" in page:
        page_compare()
    elif "Bookmarks" in page:
        page_bookmarks()
    elif "Settings" in page:
        page_settings()
    else:
        page_dashboard()


if __name__ == "__main__":
    main()
