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
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# SESSION STATE (must exist before CSS reads theme)
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

defaults = {
    "step": 1,
    "questions": [],
    "answers": {},
    "final_doc": "",
    "extra": ""
}
for k, v in defaults.items():
    st.session_state.setdefault(k, v)

IS_DARK = st.session_state.theme == "dark"

# =====================================================
# THEME COLORS
# =====================================================
if IS_DARK:
    BG = "#020617"
    BG_SOFT = "#0b1220"
    CARD_BG = "linear-gradient(145deg, #0b1220, #0a0f1c)"
    BORDER = "#1e293b"
    TEXT = "#e5e7eb"
    MUTED = "#94a3b8"
else:
    BG = "#f1f5f9"
    BG_SOFT = "#ffffff"
    CARD_BG = "linear-gradient(145deg, #ffffff, #f8fafc)"
    BORDER = "#e2e8f0"
    TEXT = "#0f172a"
    MUTED = "#64748b"

ACCENT = "#3b82f6"
ACCENT_2 = "#2563eb"

# =====================================================
# PREMIUM CSS
# =====================================================
st.markdown(f"""
<style>
#MainMenu, footer {{visibility: hidden;}}

.stApp {{
    background: radial-gradient(circle at top, {BG}, {BG});
    color: {TEXT};
    font-family: 'Inter', sans-serif;
}}

/* Card */
.card {{
    background: {CARD_BG};
    border: 1px solid {BORDER};
    border-radius: 20px;
    padding: 26px;
    margin-bottom: 22px;
    box-shadow: 0 4px 18px rgba(0,0,0,0.15);
}}

.section-title {{
    font-size: 26px;
    font-weight: 800;
    margin-bottom: 8px;
    color: {TEXT};
}}

.muted {{ color: {MUTED}; }}

/* Buttons */
.stButton > button {{
    background: linear-gradient(90deg, {ACCENT}, {ACCENT_2});
    color: white;
    border-radius: 14px;
    padding: 10px 24px;
    font-weight: 700;
    border: none;
    transition: 0.2s;
}}
.stButton > button:hover {{ transform: scale(1.02); }}

/* Inputs */
input, textarea {{
    background-color: {BG_SOFT} !important;
    color: {TEXT} !important;
    border-radius: 12px !important;
    border: 1px solid {BORDER} !important;
}}

div[data-baseweb="select"] > div {{
    background-color: {BG_SOFT} !important;
    border-radius: 12px !important;
    border: 1px solid {BORDER} !important;
    color: {TEXT} !important;
}}

/* SIDEBAR */
section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {BG}, {BG});
    border-right: 1px solid {BORDER};
}}
section[data-testid="stSidebar"] .stButton > button {{
    width: 100%;
    text-align: left;
    border-radius: 12px;
    background: transparent;
    color: {TEXT};
    border: 1px solid transparent;
    padding: 10px 14px;
    font-weight: 600;
    box-shadow: none;
}}
section[data-testid="stSidebar"] .stButton > button:hover {{
    background: rgba(59, 130, 246, 0.15);
    border: 1px solid {ACCENT};
    transform: translateX(3px);
}}

/* KPI icon chip */
.kpi-icon {{
    width: 44px; height: 44px;
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px;
}}

/* Hero banner */
.hero-banner {{
    position: relative;
    border-radius: 20px;
    overflow: hidden;
    height: 220px;
    margin-bottom: 22px;
    background-size: cover;
    background-position: center;
    border: 1px solid {BORDER};
}}
.hero-overlay {{
    position: absolute; inset: 0;
    background: linear-gradient(90deg, rgba(2,6,23,0.92) 30%, rgba(2,6,23,0.55) 75%, rgba(2,6,23,0.2) 100%);
    display: flex; flex-direction: column; justify-content: center;
    padding: 0 34px;
}}
.hero-overlay h2 {{ color: white; margin: 0 0 6px 0; font-size: 26px; }}
.hero-overlay p {{ color: #cbd5e1; margin: 0; max-width: 420px; }}

/* Toggle pill (visual) */
.toggle-pill {{
    display: inline-flex; align-items: center; gap: 8px;
    background: {BG_SOFT}; border: 1px solid {BORDER};
    border-radius: 999px; padding: 6px 14px; font-size: 13px; color: {MUTED};
}}

/* Activity row */
.activity-row {{
    display: flex; justify-content: space-between; align-items: center;
    padding: 12px 4px; border-bottom: 1px solid {BORDER};
}}

/* Disclaimer box */
.disclaimer-box {{
    background: rgba(245, 158, 11, 0.1);
    border: 1px solid rgba(245, 158, 11, 0.35);
    border-radius: 16px;
    padding: 18px 20px;
    color: #f59e0b;
}}

/* Top bar */
.topbar {{
    display: flex; justify-content: space-between; align-items: flex-start;
    margin-bottom: 26px;
}}
</style>
""", unsafe_allow_html=True)

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
        if "collapsed" not in st.session_state:
            st.session_state.collapsed = False

        toggle = "➡️" if st.session_state.collapsed else "⬅️"
        if st.button(toggle, use_container_width=True):
            st.session_state.collapsed = not st.session_state.collapsed
            st.rerun()

        if not st.session_state.collapsed:
            st.markdown("""
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:24px;">
                <div style="width:42px;height:42px;border-radius:12px;background:linear-gradient(135deg,#3b82f6,#2563eb);
                display:flex;align-items:center;justify-content:center;font-size:20px;">⚖️</div>
                <div>
                    <div style="font-weight:800; font-size:16px;">LegalDoc AI</div>
                    <div class='muted' style="font-size:12px;">AI Legal Workspace</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        def nav_item(icon, label, page):
            text = f"{icon}  {label}" if not st.session_state.collapsed else icon
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
                    <div style="width:36px;height:36px;border-radius:50%;background:{ACCENT};
                    display:flex;align-items:center;justify-content:center;">👤</div>
                    <div>
                        <b>{st.session_state.user}</b><br>
                        <span class='muted' style="font-size:12px;">Docs: {len(st.session_state.history)} &nbsp;•&nbsp; <span style="color:#22c55e;">Live</span></span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div style="text-align:center; margin-top:10px;" class='muted'>
                LegalDoc AI • v2.0
            </div>
            """, unsafe_allow_html=True)

# =====================================================
# TOP BAR (title + theme toggle + New Document)
# =====================================================
def top_bar(title, subtitle, icon="📊"):
    left, right = st.columns([3, 2])
    with left:
        st.markdown(f"""
        <div>
            <div style="font-size:28px; font-weight:800;">{icon} {title}</div>
            <div class='muted'>{subtitle}</div>
        </div>
        """, unsafe_allow_html=True)
    with right:
        c1, c2 = st.columns([1.4, 1])
        with c1:
            mode_label = "🌙 Dark" if IS_DARK else "☀️ Light"
            other_label = "☀️ Light" if IS_DARK else "🌙 Dark"
            if st.button(f"{mode_label}  |  switch to {other_label}", key="theme_toggle"):
                st.session_state.theme = "light" if IS_DARK else "dark"
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
    st.markdown("<br>", unsafe_allow_html=True)

# =====================================================
# DASHBOARD
# =====================================================
def dashboard_ui():
    top_bar("Dashboard", "AI-powered legal document workspace")

    # ================= KPI CARDS =================
    def kpi(title, value, icon, color):
        return f"""
        <div class='card'>
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <div class='muted'>{title}</div>
                    <h1 style="margin:0; color:{color};">{value}</h1>
                </div>
                <div class="kpi-icon" style="background:{color}22;">{icon}</div>
            </div>
        </div>
        """

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(kpi("Total Docs", len(st.session_state.history), "📄", "#3b82f6"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi("Draft Mode", "RAG", "⚖️", "#22c55e"), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi("AI Engine", "LLM", "🤖", "#a855f7"), unsafe_allow_html=True)
    with c4:
        st.markdown(kpi("Status", "Live", "⚡", "#f59e0b"), unsafe_allow_html=True)

    left, right = st.columns([2.5, 1.5])

    with left:
        # ===== HERO BANNER =====
        st.markdown("""
        <div class="hero-banner" style="background-image:url('https://images.unsplash.com/photo-1521791136064-7986c2920216?q=80&w=1200&auto=format&fit=crop');">
            <div class="hero-overlay">
                <h2>Create Legal Document</h2>
                <p>Generate Indian legal documents using AI + verified clauses.</p>
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

        # ===== DOCUMENT INSIGHTS =====
        doc_types = {}
        for item in st.session_state.history:
            doc_types[item["document"]] = doc_types.get(item["document"], 0) + 1

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        ic1, ic2 = st.columns([3, 1])
        with ic1:
            st.markdown("<h3 style='margin:0;'>📊 Document Insights</h3>", unsafe_allow_html=True)
        with ic2:
            st.markdown("<div style='text-align:right;' class='toggle-pill'>RAG 🔵</div>", unsafe_allow_html=True)

        if doc_types:
            st.bar_chart(doc_types)
        else:
            st.info("No analytics yet. Create your first document 🚀")
        st.markdown("</div>", unsafe_allow_html=True)

        # ===== MY DOCUMENTS TASK BAR =====
        st.markdown("<div class='card'><h3 style='margin-top:0;'>📝 My Documents</h3>", unsafe_allow_html=True)
        tc1, tc2 = st.columns([5, 1])
        with tc1:
            new_task = st.text_input("Add a document task...", key="doc_task_input", label_visibility="collapsed", placeholder="Add a document task...")
        with tc2:
            if st.button("➕", key="add_doc_task", use_container_width=True):
                if new_task:
                    st.session_state.doc_tasks.append(new_task)
                    st.rerun()
        if st.session_state.doc_tasks:
            for t in st.session_state.doc_tasks[::-1]:
                st.markdown(f"<div style='padding:8px 0; border-bottom:1px solid {BORDER};'>• {t}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        # ===== RECENT ACTIVITY =====
        st.markdown("<div class='card'><h3 style='margin-top:0;'>🕐 Recent Activity</h3>", unsafe_allow_html=True)

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
                    <div style="color:#f59e0b;">{star}</div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # ===== QUICK SETUP =====
        st.markdown("<div class='card'><h3 style='margin-top:0;'>🔀 Quick Setup</h3>", unsafe_allow_html=True)
        st.markdown("<div class='muted' style='font-size:13px;'>Document Type</div>", unsafe_allow_html=True)
        st.session_state.quick_doc_type = st.selectbox(
            "Document Type", ["Rent Agreement", "Affidavit", "Power of Attorney"],
            index=["Rent Agreement", "Affidavit", "Power of Attorney"].index(st.session_state.quick_doc_type),
            label_visibility="collapsed", key="quick_doc_select"
        )
        st.markdown("<br>", unsafe_allow_html=True)
        qc1, qc2 = st.columns([3, 1])
        with qc1:
            st.markdown("<b>Auto-add clauses</b><br><span class='muted' style='font-size:12px;'>Verified legal formats</span>", unsafe_allow_html=True)
        with qc2:
            st.session_state.auto_add_clauses = st.toggle(
                "Auto-add clauses", value=st.session_state.auto_add_clauses,
                label_visibility="collapsed", key="auto_clause_toggle"
            )
        st.markdown("</div>", unsafe_allow_html=True)

        # ===== DISCLAIMER =====
        st.markdown("""
        <div class="disclaimer-box">
            ⚠️ <b>Disclaimer:</b> AI-generated documents must be reviewed by a legal professional.
        </div>
        """, unsafe_allow_html=True)


def landing_ui():
    st.markdown(
        """
        <div class="card" style="text-align:center; padding:50px 30px;">
            <h1 style="font-size:42px;">⚖️ LegalDoc AI</h1>
            <p class="muted" style="font-size:18px; margin-top:10px;">
                AI-Powered Indian Legal Document Generator
            </p>
            <p class="muted" style="max-width:700px; margin:20px auto;">
                Create legally structured Indian documents using AI-guided workflows,
                verified legal clauses, and secure authentication.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        if st.button("🚀 Get Started"):
            st.session_state.page = "dashboard"
            st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>Why LegalDoc AI?</div>", unsafe_allow_html=True)

    f1, f2, f3, f4 = st.columns(4)
    with f1:
        st.markdown("""
            <div class="card">
                <h3>⚖️ Legal Accuracy</h3>
                <p class="muted">Clause-based drafting using verified Indian legal formats.</p>
            </div>
            """, unsafe_allow_html=True)
    with f2:
        st.markdown("""
            <div class="card">
                <h3>🤖 AI Guided</h3>
                <p class="muted">Chat-style questions to capture all legal requirements.</p>
            </div>
            """, unsafe_allow_html=True)
    with f3:
        st.markdown("""
            <div class="card">
                <h3>🔐 Secure Access</h3>
                <p class="muted">Backend-based authentication with hashed passwords.</p>
            </div>
            """, unsafe_allow_html=True)
    with f4:
        st.markdown("""
            <div class="card">
                <h3>⚡ Fast & Optimized</h3>
                <p class="muted">Single optimized AI call with RAG support.</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>How it works</div>", unsafe_allow_html=True)
    st.markdown("""
        <div class="card">
            <ol class="muted">
                <li>Select document type & variant</li>
                <li>Answer AI-guided legal questions</li>
                <li>Review and customize clauses</li>
                <li>Download ready-to-use legal document</li>
            </ol>
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
# DOCUMENT CREATION (STEPPER)
# =====================================================
def document_ui():
    top_bar("Create Legal Document", "Follow the guided steps to draft your document", icon="📄")

    progress_map = {1: 0.25, 2: 0.50, 3: 0.75, 4: 1.0}
    st.progress(progress_map.get(st.session_state.step, 0.25))
    st.caption(f"Step {st.session_state.step} of 4")

    if st.session_state.step == 1:
        st.markdown("<div class='card'><b>Step 1: Select Document</b></div>", unsafe_allow_html=True)

        document = st.selectbox(
            "Document Type",
            ["Rent Agreement", "Affidavit", "Power of Attorney"]
        )

        subtype_map = {
            "Rent Agreement": ["Residential", "Commercial", "Leave & License"],
            "Affidavit": ["Name Change", "Address Proof", "Income Proof"],
            "Power of Attorney": ["General POA", "Special POA"]
        }
        subtype = st.selectbox("Document Variant", subtype_map[document])

        if st.button("Next →"):
            st.session_state.document = document
            st.session_state.subtype = subtype
            st.session_state.step = 2
            st.session_state.q_index = 0
            st.rerun()

    elif st.session_state.step == 2:
        st.markdown("<div class='card'><b>Step 2: AI is asking questions</b></div>", unsafe_allow_html=True)

        if not st.session_state.questions:
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

        if q_index < len(questions):
            current_question = questions[q_index]
            st.markdown(
                f"<div class='card'>🤖 <b>AI:</b><br>{current_question}</div>",
                unsafe_allow_html=True
            )
            answer = st.text_input("Your answer")

            if st.button("Next Question"):
                st.session_state.answers[current_question] = answer
                st.session_state.q_index += 1
                st.rerun()
        else:
            st.success("All questions completed ✅")
            st.subheader("Additional Instructions (Optional)")
            st.session_state.extra = st.text_area(
                "Add special clauses",
                placeholder="Example: No subletting, parking included"
            )
            if st.button("Continue → Review"):
                st.session_state.step = 3
                st.rerun()

    elif st.session_state.step == 3:
        st.markdown("<div class='card'><b>Step 3: Review Your Details</b></div>", unsafe_allow_html=True)

        for q, a in st.session_state.answers.items():
            st.markdown(f"<div class='card'><b>{q}</b><br>{a}</div>", unsafe_allow_html=True)

        if st.session_state.extra:
            st.markdown(f"<div class='card'><b>Extra</b><br>{st.session_state.extra}</div>", unsafe_allow_html=True)

        if st.button("Generate Final Document"):
            st.session_state.step = 4
            st.rerun()

    elif st.session_state.step == 4:
        st.markdown("<div class='card'><b>Step 4: Final Document</b></div>", unsafe_allow_html=True)

        with st.spinner("Drafting using legal knowledge base..."):
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
            st.session_state.final_doc = call_llm(prompt)

        if not st.session_state.get("saved", False):
            st.session_state.history.append({
                "document": st.session_state.document,
                "subtype": st.session_state.subtype,
                "content": st.session_state.final_doc
            })
            st.session_state.saved = True

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
    top_bar("History", "All your generated documents", icon="📜")

    if not st.session_state.history:
        st.info("No documents generated yet.")
        return

    for i, item in enumerate(st.session_state.history):
        with st.expander(f"{i+1}. {item['document']} ({item['subtype']})"):
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
