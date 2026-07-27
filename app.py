import streamlit as st
import requests, os, json
import faiss
from sentence_transformers import SentenceTransformer
from docx import Document

def create_docx(content: str):
    doc = Document()
    for line in content.split("\n"):
        doc.add_paragraph(line)
    file_path = "Legal_Document.docx"
    doc.save(file_path)
    return file_path

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="LegalDoc AI",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# SESSION STATE
# =====================================================
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "user" not in st.session_state:
    st.session_state.user = "Aditya Sharma"
if "step" not in st.session_state:
    st.session_state.step = 1
if "history" not in st.session_state:
    st.session_state.history = []
if "theme" not in st.session_state:
    st.session_state.theme = "dark"          # "dark" or "light"
if "auto_add_clauses" not in st.session_state:
    st.session_state.auto_add_clauses = True
if "quick_doc_type" not in st.session_state:
    st.session_state.quick_doc_type = "Rent Agreement"
if "doc_tasks" not in st.session_state:
    st.session_state.doc_tasks = []
if "collapsed" not in st.session_state:
    st.session_state.collapsed = False

defaults = {
    "step": 1,
    "questions": [],
    "answers": {},
    "final_doc": "",
    "extra": "",
    "q_index": 0,
    "saved": False,
    "document": "Rent Agreement",
    "subtype": "Residential",
}
for k, v in defaults.items():
    st.session_state.setdefault(k, v)

IS_DARK = st.session_state.theme == "dark"

# =====================================================
# DESIGN TOKENS — "The Chambers" (ink, parchment & brass)
#
# A document-drafting product lives or dies on the feeling of the
# paper itself, so the palette borrows from a barrister's chambers:
# deep pine-ink walls, brass fittings, a wax seal for authenticity —
# rather than the generic dark-SaaS blue gradient.
# =====================================================
if IS_DARK:
    INK = "#0F1710"          # deep pine-ink background
    INK_SOFT = "#161F17"
    PANEL = "linear-gradient(155deg, #182119, #121912)"
    BORDER = "#2B3A2C"
    TEXT = "#EDE7D9"          # warm parchment white
    MUTED = "#93A090"
else:
    INK = "#F4EEDD"          # parchment
    INK_SOFT = "#FFFFFF"
    PANEL = "linear-gradient(155deg, #FFFFFF, #FAF5E8)"
    BORDER = "#DCD2B4"
    TEXT = "#1E2A1D"
    MUTED = "#5B6B57"

BRASS = "#C9A227"
BRASS_LIGHT = "#E4C25E"
RUST = "#A6452D"
SAGE = "#7C8B6F"

# =====================================================
# GLOBAL CSS
# =====================================================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,600;0,6..72,700;1,6..72,500&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

#MainMenu, footer {{visibility: hidden;}}

html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}

.stApp {{
    background: {INK};
    color: {TEXT};
    transition: background-color .35s ease, color .35s ease;
}}

h1, h2, h3, .display {{
    font-family: 'Newsreader', serif;
    letter-spacing: -0.01em;
}}

.mono {{ font-family: 'JetBrains Mono', monospace; }}

/* Letterhead rule */
.letterhead-rule {{
    height: 2px;
    background: linear-gradient(90deg, {BRASS}, transparent);
    margin: 4px 0 26px 0;
    border-radius: 2px;
}}

/* Card / paper sheet */
.card {{
    background: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 16px;
    padding: 26px;
    margin-bottom: 20px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.18);
    transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
}}
.card.hoverable:hover {{
    transform: translateY(-4px);
    border-color: {BRASS}55;
    box-shadow: 0 12px 28px rgba(0,0,0,0.24);
}}

.section-title {{
    font-size: 25px;
    font-weight: 700;
    margin-bottom: 6px;
    color: {TEXT};
    font-family: 'Newsreader', serif;
}}

.muted {{ color: {MUTED}; }}
.brass-text {{ color: {BRASS_LIGHT if IS_DARK else BRASS}; }}

/* Wax seal */
.seal {{
    width: 46px; height: 46px;
    border-radius: 50%;
    background: radial-gradient(circle at 35% 30%, {BRASS_LIGHT}, {BRASS} 60%, #8a6c1c 100%);
    display: flex; align-items: center; justify-content: center;
    font-size: 20px;
    box-shadow: inset 0 0 0 3px rgba(0,0,0,0.18), 0 4px 10px rgba(0,0,0,0.35);
    flex-shrink: 0;
}}
.seal.small {{ width: 34px; height: 34px; font-size: 15px; }}
.seal.big {{ width: 84px; height: 84px; font-size: 34px; }}

@keyframes stampDown {{
    0%   {{ transform: scale(2.4) rotate(-18deg); opacity: 0; }}
    55%  {{ transform: scale(0.92) rotate(3deg); opacity: 1; }}
    75%  {{ transform: scale(1.06) rotate(-2deg); }}
    100% {{ transform: scale(1) rotate(-6deg); }}
}}
.stamp-wrap {{ text-align:center; margin: 6px 0 22px 0; }}
.stamp {{
    display: inline-flex; flex-direction: column; align-items:center; justify-content:center;
    width: 130px; height: 130px; border-radius: 50%;
    border: 3px solid {RUST};
    color: {RUST};
    font-family: 'Newsreader', serif; font-weight: 700; font-size: 15px;
    animation: stampDown .55s cubic-bezier(.2,.9,.3,1.2);
    transform: rotate(-6deg);
    background: {'rgba(166,69,45,0.08)' if IS_DARK else 'rgba(166,69,45,0.06)'};
}}
.stamp span.small {{ font-size: 10px; letter-spacing: 2px; margin-top: 4px; font-family:'Inter',sans-serif; }}

/* Buttons */
.stButton > button {{
    background: linear-gradient(90deg, {BRASS}, #B48A22);
    color: #1a1405;
    border-radius: 10px;
    padding: 9px 22px;
    font-weight: 700;
    border: none;
    transition: transform .15s ease, box-shadow .15s ease, filter .15s ease;
}}
.stButton > button:hover {{
    transform: translateY(-1px);
    filter: brightness(1.08);
    box-shadow: 0 6px 16px rgba(201,162,39,0.35);
}}
.stButton > button:active {{ transform: translateY(0px) scale(.98); }}

/* Secondary look for sidebar / ghost buttons handled below */

/* Inputs */
input, textarea, .stChatInput textarea {{
    background-color: {INK_SOFT} !important;
    color: {TEXT} !important;
    border-radius: 10px !important;
    border: 1px solid {BORDER} !important;
}}
div[data-baseweb="select"] > div {{
    background-color: {INK_SOFT} !important;
    border-radius: 10px !important;
    border: 1px solid {BORDER} !important;
    color: {TEXT} !important;
}}

/* Radio-as-pills (document type / variant / quick setup selectors) */
div[data-testid="stRadio"] > div {{
    gap: 10px;
}}
div[data-testid="stRadio"] label {{
    background: {INK_SOFT};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 10px 16px !important;
    margin: 0 !important;
    transition: border-color .15s ease, transform .12s ease, background .15s ease;
    cursor: pointer;
}}
div[data-testid="stRadio"] label:hover {{
    border-color: {BRASS};
    transform: translateY(-2px);
}}
div[data-testid="stRadio"] label[data-baseweb="radio"] > div:first-child {{
    display: none;
}}

/* Docket stepper */
.docket {{ display:flex; align-items:center; margin-bottom: 22px; }}
.docket-step {{ display:flex; flex-direction:column; align-items:center; flex:1; position:relative; }}
.docket-circle {{
    width: 34px; height: 34px; border-radius: 50%;
    display:flex; align-items:center; justify-content:center;
    font-family:'JetBrains Mono', monospace; font-weight:600; font-size:13px;
    border: 2px solid {BORDER}; color: {MUTED}; background:{INK_SOFT};
    transition: all .25s ease; z-index: 2;
}}
.docket-circle.done {{ background:{BRASS}; border-color:{BRASS}; color:#1a1405; }}
.docket-circle.active {{ border-color:{BRASS}; color:{BRASS if not IS_DARK else BRASS_LIGHT}; box-shadow: 0 0 0 4px {BRASS}22; }}
.docket-label {{ font-size:12px; margin-top:6px; color:{MUTED}; text-align:center; }}
.docket-line {{
    position:absolute; top:17px; left:-50%; width:100%; height:2px;
    background:{BORDER}; z-index:1;
}}
.docket-line.done {{ background:{BRASS}; }}
.docket-step:first-child .docket-line {{ display:none; }}

/* KPI icon chip */
.kpi-icon {{
    width: 44px; height: 44px; border-radius: 12px;
    display: flex; align-items: center; justify-content: center; font-size: 20px;
}}

/* Hero banner */
.hero-banner {{
    position: relative; border-radius: 18px; overflow: hidden; height: 230px;
    margin-bottom: 22px; background-size: cover; background-position: center;
    border: 1px solid {BORDER};
}}
.hero-overlay {{
    position: absolute; inset: 0;
    background: linear-gradient(90deg, {INK}ee 32%, {INK}99 70%, {INK}22 100%);
    display: flex; align-items:center; gap: 22px; padding: 0 34px;
}}
.hero-overlay h2 {{ color: {TEXT}; margin: 0 0 6px 0; font-size: 30px; font-family:'Newsreader',serif; font-weight:700; }}
.hero-overlay p {{ color: {MUTED}; margin: 0; max-width: 420px; }}

/* Toggle pill */
.toggle-pill {{
    display: inline-flex; align-items: center; gap: 8px;
    background: {INK_SOFT}; border: 1px solid {BORDER};
    border-radius: 999px; padding: 6px 14px; font-size: 12px; color: {MUTED};
}}

/* Activity row */
.activity-row {{
    display: flex; justify-content: space-between; align-items: center;
    padding: 12px 4px; border-bottom: 1px solid {BORDER};
    transition: padding-left .15s ease;
}}
.activity-row:hover {{ padding-left: 6px; }}

/* Disclaimer box */
.disclaimer-box {{
    background: {RUST}18;
    border: 1px solid {RUST}55;
    border-radius: 14px;
    padding: 16px 20px;
    color: {RUST if not IS_DARK else '#E8A28F'};
}}

.topbar {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px; }}

/* Sidebar */
section[data-testid="stSidebar"] {{
    background: {INK};
    border-right: 1px solid {BORDER};
    transition: width .25s ease;
}}
section[data-testid="stSidebar"] .stButton > button {{
    width: 100%; text-align: left; border-radius: 10px;
    background: transparent; color: {TEXT}; border: 1px solid transparent;
    padding: 10px 14px; font-weight: 600; box-shadow: none;
}}
section[data-testid="stSidebar"] .stButton > button:hover {{
    background: {BRASS}1c; border: 1px solid {BRASS}55;
    transform: translateX(3px); box-shadow:none; filter:none;
}}

/* Chat bubbles for the Q&A step */
div[data-testid="stChatMessage"] {{
    background: {INK_SOFT};
    border: 1px solid {BORDER};
    border-radius: 14px;
    padding: 4px 6px;
    margin-bottom: 8px;
}}
</style>
""", unsafe_allow_html=True)


def seal(size="", symbol="⚖"):
    cls = f"seal {size}".strip()
    return f"<div class='{cls}'>{symbol}</div>"


def toast(msg, icon="✅"):
    try:
        st.toast(msg, icon=icon)
    except Exception:
        pass

# =====================================================
# API CONFIG
# =====================================================
API_KEY = st.secrets.get("API_KEY", "")
API_URL = "https://openrouter.ai/api/v1/chat/completions"
if not API_KEY:
    st.error("OPENROUTER_API_KEY not set")
    st.stop()

# =====================================================
# LOAD PREBUILT RAG
# =====================================================
@st.cache_resource
def load_rag():
    index = faiss.read_index("faiss.index")
    with open("clauses.json", "r", encoding="utf-8") as f:
        clauses = json.load(f)
    embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return index, clauses, embedder

faiss_index, rag_clauses, embedder = load_rag()

def retrieve_clauses(query, k=3):
    q_emb = embedder.encode([query])
    _, idx = faiss_index.search(q_emb, k)
    return "\n".join(rag_clauses[i] for i in idx[0] if i != -1)

# =====================================================
# LLM CALL
# =====================================================
def call_llm(prompt, temp=0.25, tokens=1400):
    r = requests.post(
        API_URL,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "qwen/qwen-2.5-7b-instruct",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temp,
            "max_tokens": tokens
        },
        timeout=60
    )
    return r.json()["choices"][0]["message"]["content"]

# =====================================================
# SIDEBAR
# =====================================================
def sidebar():
    with st.sidebar:
        toggle = "➡️" if st.session_state.collapsed else "⬅️"
        if st.button(toggle, use_container_width=True):
            st.session_state.collapsed = not st.session_state.collapsed
            st.rerun()

        if not st.session_state.collapsed:
            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:24px;">
                {seal("small")}
                <div>
                    <div style="font-weight:700; font-size:16px; font-family:'Newsreader',serif;">LegalDoc AI</div>
                    <div class='muted' style="font-size:12px;">Chambers of AI Drafting</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        def nav_item(icon, label, page):
            text = f"{icon}  {label}" if not st.session_state.collapsed else icon
            active = st.session_state.page == page
            if st.button(text, use_container_width=True, key=f"nav_{page}"):
                st.session_state.page = page
                st.rerun()

        nav_item("🏠", "Dashboard", "dashboard")
        nav_item("📄", "New Document", "document")
        nav_item("📜", "History", "history")

        st.markdown("<br>", unsafe_allow_html=True)

        if not st.session_state.collapsed:
            st.markdown(f"""
            <div class='card' style="padding:16px;">
                <div style="display:flex; align-items:center; gap:10px;">
                    <div style="width:36px;height:36px;border-radius:50%;background:{BRASS};
                    display:flex;align-items:center;justify-content:center;">👤</div>
                    <div>
                        <b>{st.session_state.user}</b><br>
                        <span class='muted' style="font-size:12px;">Docs: {len(st.session_state.history)} &nbsp;•&nbsp; <span style="color:{SAGE};">Live</span></span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"<div style='text-align:center;' class='muted'>LegalDoc AI • v2.1</div>", unsafe_allow_html=True)

# =====================================================
# TOP BAR (letterhead)
# =====================================================
def top_bar(title, subtitle, icon="📊"):
    left, right = st.columns([3, 2])
    with left:
        st.markdown(f"""
        <div>
            <div style="font-size:28px; font-weight:700; font-family:'Newsreader',serif;">{icon} {title}</div>
            <div class='muted'>{subtitle}</div>
        </div>
        """, unsafe_allow_html=True)
    with right:
        c1, c2 = st.columns([1.4, 1])
        with c1:
            mode_label = "🌙 Dark" if IS_DARK else "☀️ Light"
            other_label = "☀️ Light" if IS_DARK else "🌙 Dark"
            if st.button(f"{mode_label}  →  {other_label}", key="theme_toggle"):
                st.session_state.theme = "light" if IS_DARK else "dark"
                toast(f"Switched to {other_label.split()[1]} mode", icon="🌗")
                st.rerun()
        with c2:
            if st.button("➕ New Document", key="topbar_new_doc", use_container_width=True):
                st.session_state.page = "document"
                st.session_state.step = 1
                st.session_state.questions = []
                st.session_state.answers = {}
                st.session_state.q_index = 0
                st.session_state.saved = False
                st.rerun()
    st.markdown("<div class='letterhead-rule'></div>", unsafe_allow_html=True)

# =====================================================
# DASHBOARD
# =====================================================
def dashboard_ui():
    top_bar("Dashboard", "Your AI-powered legal drafting workspace")

    def kpi(title, value, icon, color):
        return f"""
        <div class='card hoverable'>
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <div class='muted'>{title}</div>
                    <h1 style="margin:0; color:{color}; font-family:'Newsreader',serif;">{value}</h1>
                </div>
                <div class="kpi-icon" style="background:{color}22;">{icon}</div>
            </div>
        </div>
        """

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(kpi("Total Docs", len(st.session_state.history), "📄", BRASS), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi("Draft Mode", "RAG", "⚖️", SAGE), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi("AI Engine", "LLM", "🤖", "#8b6fd6"), unsafe_allow_html=True)
    with c4:
        st.markdown(kpi("Status", "Live", "⚡", RUST), unsafe_allow_html=True)

    left, right = st.columns([2.5, 1.5])

    with left:
        st.markdown(f"""
        <div class="hero-banner" style="background: linear-gradient(120deg, {INK_SOFT}, {INK});">
            <div class="hero-overlay">
                {seal("big")}
                <div>
                    <h2>Draft with confidence</h2>
                    <p>Generate Indian legal documents using AI, grounded in verified clauses.</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("➕ Start New Document", use_container_width=True, key="hero_start"):
            st.session_state.page = "document"
            st.session_state.step = 1
            st.session_state.questions = []
            st.session_state.answers = {}
            st.session_state.q_index = 0
            st.session_state.saved = False
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        doc_types = {}
        for item in st.session_state.history:
            doc_types[item["document"]] = doc_types.get(item["document"], 0) + 1

        st.markdown("<div class='card hoverable'>", unsafe_allow_html=True)
        ic1, ic2 = st.columns([3, 1])
        with ic1:
            st.markdown("<h3 style='margin:0;'>📊 Document Insights</h3>", unsafe_allow_html=True)
        with ic2:
            st.markdown("<div style='text-align:right;' class='toggle-pill'>RAG 🔵</div>", unsafe_allow_html=True)

        if doc_types:
            st.bar_chart(doc_types, color=BRASS)
        else:
            st.info("No analytics yet. Create your first document 🚀")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='card hoverable'><h3 style='margin-top:0;'>📝 My Documents</h3>", unsafe_allow_html=True)
        tc1, tc2 = st.columns([5, 1])
        with tc1:
            new_task = st.text_input("Add a document task...", key="doc_task_input", label_visibility="collapsed", placeholder="Add a document task...")
        with tc2:
            if st.button("➕", key="add_doc_task", use_container_width=True):
                if new_task:
                    st.session_state.doc_tasks.append(new_task)
                    toast("Task added", icon="📝")
                    st.rerun()
        if st.session_state.doc_tasks:
            for t in st.session_state.doc_tasks[::-1]:
                st.markdown(f"<div style='padding:8px 0; border-bottom:1px solid {BORDER};'>• {t}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div class='card hoverable'><h3 style='margin-top:0;'>🕐 Recent Activity</h3>", unsafe_allow_html=True)
        if not st.session_state.history:
            st.markdown("<div class='muted'>No activity yet</div>", unsafe_allow_html=True)
        else:
            icon_map = {"Rent Agreement": "📄", "Affidavit": "📗", "Power of Attorney": "🖋️"}
            for i, item in enumerate(st.session_state.history[-5:][::-1]):
                icon = icon_map.get(item["document"], "📄")
                star = "⭐" if i == 1 else "☆"
                st.markdown(f"""
                <div class="activity-row">
                    <div>
                        <div>{icon} <b>{item['document']}</b></div>
                        <span class='muted' style="font-size:12px;">{item['subtype']}</span>
                    </div>
                    <div style="color:{BRASS};">{star}</div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='card hoverable'><h3 style='margin-top:0;'>🔀 Quick Setup</h3>", unsafe_allow_html=True)
        st.markdown("<div class='muted' style='font-size:13px;'>Document Type</div>", unsafe_allow_html=True)
        options = ["Rent Agreement", "Affidavit", "Power of Attorney"]
        icons = {"Rent Agreement": "🏠", "Affidavit": "📗", "Power of Attorney": "🖋️"}
        st.session_state.quick_doc_type = st.radio(
            "Document Type", options,
            index=options.index(st.session_state.quick_doc_type),
            format_func=lambda o: f"{icons[o]} {o}",
            label_visibility="collapsed", key="quick_doc_select", horizontal=True
        )
        st.markdown("<br>", unsafe_allow_html=True)
        qc1, qc2 = st.columns([3, 1])
        with qc1:
            st.markdown("<b>Auto-add clauses</b><br><span class='muted' style='font-size:12px;'>Verified legal formats</span>", unsafe_allow_html=True)
        with qc2:
            new_val = st.toggle(
                "Auto-add clauses", value=st.session_state.auto_add_clauses,
                label_visibility="collapsed", key="auto_clause_toggle"
            )
            if new_val != st.session_state.auto_add_clauses:
                st.session_state.auto_add_clauses = new_val
                toast("Clause auto-add " + ("enabled" if new_val else "disabled"), icon="⚖️")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div class="disclaimer-box">
            ⚠️ <b>Disclaimer:</b> AI-generated documents must be reviewed by a legal professional.
        </div>
        """, unsafe_allow_html=True)


def landing_ui():
    st.markdown(
        f"""
        <div class="card" style="text-align:center; padding:56px 30px;">
            <div style="display:flex; justify-content:center; margin-bottom:18px;">{seal("big")}</div>
            <h1 style="font-size:42px; margin-bottom:4px;">LegalDoc AI</h1>
            <p class="muted" style="font-size:18px; margin-top:6px;">
                AI-Powered Indian Legal Document Generator
            </p>
            <p class="muted" style="max-width:680px; margin:20px auto;">
                Create legally structured Indian documents through a guided, conversational
                workflow — grounded in verified clauses, sealed and ready to download.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        if st.button("🚀 Get Started", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Why LegalDoc AI?</div>", unsafe_allow_html=True)

    features = [
        ("⚖️", "Legal Accuracy", "Clause-based drafting using verified Indian legal formats."),
        ("🤖", "AI Guided", "A chat-style dialogue captures every requirement, one question at a time."),
        ("🔐", "Secure Access", "Backend-based authentication with hashed passwords."),
        ("⚡", "Fast & Optimized", "A single optimized AI call, grounded with retrieval (RAG)."),
    ]
    cols = st.columns(4)
    for col, (icon, title, desc) in zip(cols, features):
        with col:
            st.markdown(f"""
                <div class="card hoverable">
                    <h3>{icon} {title}</h3>
                    <p class="muted">{desc}</p>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>How it works</div>", unsafe_allow_html=True)
    steps = [
        ("Select", "Choose the document type & variant"),
        ("Converse", "Answer AI-guided legal questions in a chat"),
        ("Review", "Check details and add special clauses"),
        ("Seal", "Download your ready-to-use legal document"),
    ]
    step_cols = st.columns(4)
    for i, (col, (label, desc)) in enumerate(zip(step_cols, steps)):
        with col:
            st.markdown(f"""
            <div class="card hoverable" style="text-align:center;">
                <div class="mono brass-text" style="font-size:22px; font-weight:700;">0{i+1}</div>
                <div style="font-weight:700; margin:6px 0 4px 0; font-family:'Newsreader',serif;">{label}</div>
                <div class="muted" style="font-size:13px;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
        <div class="disclaimer-box">
            ⚠️ <b>Disclaimer:</b> AI-generated documents should be reviewed by a qualified legal
            professional before official or legal use.
        </div>
        """, unsafe_allow_html=True)


# =====================================================
# DOCKET STEPPER
# =====================================================
def docket_stepper(current, labels):
    parts = ["<div class='docket'>"]
    for i, label in enumerate(labels, start=1):
        state = "done" if i < current else ("active" if i == current else "")
        line_state = "done" if i < current else ""
        parts.append(
            f'<div class="docket-step"><div class="docket-line {line_state}"></div>'
            f'<div class="docket-circle {state}">{i}</div>'
            f'<div class="docket-label">{label}</div></div>'
        )
    parts.append("</div>")
    # Joined with no leading whitespace on any line — Markdown treats
    # 4+ leading spaces as a code block, which was swallowing steps 2-4.
    st.markdown("".join(parts), unsafe_allow_html=True)


# =====================================================
# DOCUMENT CREATION (STEPPER)
# =====================================================
def document_ui():
    top_bar("Create Legal Document", "A guided conversation drafts your document", icon="📄")

    docket_stepper(st.session_state.step, ["Select", "Converse", "Review", "Seal"])

    if st.session_state.step == 1:
        st.markdown("<div class='card'><b>Step 1 · Select Document</b></div>", unsafe_allow_html=True)

        doc_options = ["Rent Agreement", "Affidavit", "Power of Attorney"]
        doc_icons = {"Rent Agreement": "🏠", "Affidavit": "📗", "Power of Attorney": "🖋️"}
        document = st.radio(
            "Document Type", doc_options,
            format_func=lambda o: f"{doc_icons[o]}  {o}",
            horizontal=True, key="step1_doc_type"
        )

        subtype_map = {
            "Rent Agreement": ["Residential", "Commercial", "Leave & License"],
            "Affidavit": ["Name Change", "Address Proof", "Income Proof"],
            "Power of Attorney": ["General POA", "Special POA"]
        }
        st.markdown("<div class='muted' style='margin-top:14px;'>Document Variant</div>", unsafe_allow_html=True)
        subtype = st.radio(
            "Document Variant", subtype_map[document],
            horizontal=True, key="step1_subtype", label_visibility="collapsed"
        )

        if st.button("Next →"):
            st.session_state.document = document
            st.session_state.subtype = subtype
            st.session_state.step = 2
            st.session_state.q_index = 0
            st.rerun()

    elif st.session_state.step == 2:
        st.markdown(f"""
        <div class='card' style="display:flex; align-items:center; gap:12px;">
            {seal("small")}
            <div>
                <b>Step 2 · A quick conversation</b><br>
                <span class='muted' style='font-size:13px;'>Answer each question — your document is built from these answers.</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if not st.session_state.questions:
            with st.spinner("Preparing questions..."):
                q_prompt = f"""
Ask essential questions to draft a {st.session_state.subtype} {st.session_state.document}.
Use simple language. Numbered list only.
"""
                q_text = call_llm(q_prompt, temp=0.0, tokens=400)
                st.session_state.questions = [
                    q.split(".", 1)[1].strip()
                    for q in q_text.split("\n") if "." in q
                ]

        q_index = st.session_state.q_index
        questions = st.session_state.questions

        # Transcript of everything answered so far
        for q, a in st.session_state.answers.items():
            with st.chat_message("assistant", avatar="🤖"):
                st.write(q)
            with st.chat_message("user", avatar="🧑"):
                st.write(a)

        if q_index < len(questions):
            current_question = questions[q_index]
            with st.chat_message("assistant", avatar="🤖"):
                st.write(current_question)

            answer = st.chat_input("Type your answer and press Enter…")
            if answer:
                st.session_state.answers[current_question] = answer
                st.session_state.q_index += 1
                st.rerun()
        else:
            st.success("All questions completed ✅")
            st.markdown("<div class='card'><b>Additional Instructions (Optional)</b></div>", unsafe_allow_html=True)
            st.session_state.extra = st.text_area(
                "Add special clauses",
                value=st.session_state.extra,
                placeholder="Example: No subletting, parking included",
                label_visibility="collapsed"
            )
            if st.button("Continue → Review"):
                st.session_state.step = 3
                st.rerun()

    elif st.session_state.step == 3:
        st.markdown("<div class='card'><b>Step 3 · Review Your Details</b></div>", unsafe_allow_html=True)

        for q, a in st.session_state.answers.items():
            st.markdown(f"""
            <div class='card hoverable' style="padding:16px 20px;">
                <span class='muted' style='font-size:12px;'>QUESTION</span><br>
                <b>{q}</b><br><br>
                <span class='muted' style='font-size:12px;'>ANSWER</span><br>
                {a}
            </div>""", unsafe_allow_html=True)

        if st.session_state.extra:
            st.markdown(f"<div class='card hoverable'><span class='muted' style='font-size:12px;'>EXTRA CLAUSES</span><br>{st.session_state.extra}</div>", unsafe_allow_html=True)

        b1, b2 = st.columns([1, 1])
        with b1:
            if st.button("← Back", use_container_width=True):
                st.session_state.step = 2
                st.rerun()
        with b2:
            if st.button("Generate Final Document ⚖️", use_container_width=True):
                st.session_state.step = 4
                st.rerun()

    elif st.session_state.step == 4:
        st.markdown("<div class='card'><b>Step 4 · Final Document</b></div>", unsafe_allow_html=True)

        with st.spinner("Drafting using the legal knowledge base…"):
            qa = "\n".join(f"{k}: {v}" for k, v in st.session_state.answers.items())
            rag_ctx = retrieve_clauses(f"{st.session_state.document} {st.session_state.subtype}")

            prompt = f"""
You are an expert Indian legal drafting AI.

Use the following reference clauses:
{rag_ctx}

Document:
{st.session_state.subtype} {st.session_state.document}

User Inputs:
{qa}

Additional Instructions:
{st.session_state.extra}

Rules:
- Follow Indian legal structure
- Formal legal language
- Output final document only
"""
            if not st.session_state.final_doc:
                st.session_state.final_doc = call_llm(prompt)

        if not st.session_state.get("saved", False):
            st.session_state.history.append({
                "document": st.session_state.document,
                "subtype": st.session_state.subtype,
                "content": st.session_state.final_doc
            })
            st.session_state.saved = True
            toast("Document saved to history", icon="📁")
            st.markdown(f"""
            <div class="stamp-wrap">
                <div class="stamp">SEALED<span class="small">DRAFT COMPLETE</span></div>
            </div>
            """, unsafe_allow_html=True)
            st.balloons()

        st.text_area("Final Document", st.session_state.final_doc, height=450)
        docx_path = create_docx(st.session_state.final_doc)

        with open(docx_path, "rb") as f:
            st.download_button(
                label="⬇ Download as DOCX",
                data=f,
                file_name="Legal_Document.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

        if st.button("➕ Create New Document"):
            st.session_state.step = 1
            st.session_state.questions = []
            st.session_state.answers = {}
            st.session_state.final_doc = ""
            st.session_state.extra = ""
            st.session_state.q_index = 0
            st.session_state.saved = False
            st.rerun()


def history_ui():
    top_bar("History", "Every document you've sealed", icon="📜")

    if not st.session_state.history:
        st.info("No documents generated yet.")
        return

    icon_map = {"Rent Agreement": "📄", "Affidavit": "📗", "Power of Attorney": "🖋️"}
    for i, item in enumerate(st.session_state.history):
        icon = icon_map.get(item["document"], "📄")
        with st.expander(f"{icon}  {i+1}. {item['document']} ({item['subtype']})"):
            st.text_area("Document Content", item["content"], height=300, key=f"hist_{i}")

# =====================================================
# ROUTER
# =====================================================
if st.session_state.page != "landing":
    sidebar()

if st.session_state.page == "landing":
    landing_ui()
elif st.session_state.page == "dashboard":
    dashboard_ui()
elif st.session_state.page == "document":
    document_ui()
elif st.session_state.page == "history":
    history_ui()
