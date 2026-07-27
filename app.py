import streamlit as st
import requests, os, json
import faiss
import requests
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
# PREMIUM CSS
# =====================================================
st.markdown("""
<style>
#MainMenu, footer, header[data-testid="stHeader"] {visibility: hidden;}

.stApp {
    background: radial-gradient(circle at top, #0a0e1a, #05070d);
    color: #e5e7eb;
    font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
}

h1, h2, h3, .app-title, .section-title {
    font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
    letter-spacing: -0.01em;
}

.block-container {
    padding-top: 2.2rem;
    padding-bottom: 3rem;
    max-width: 1200px;
}

/* Typography helpers */
.app-title {
    font-size: 30px;
    font-weight: 800;
    color: #e5e7eb;
    margin-bottom: 2px;
}
.section-title {
    font-size: 22px;
    font-weight: 800;
    margin: 4px 0 14px 0;
    color: #e5e7eb;
}
.muted { color: #94a3b8; }
.eyebrow {
    text-transform: uppercase;
    font-size: 11.5px;
    font-weight: 700;
    letter-spacing: 0.12em;
    color: #3b82f6;
    margin-bottom: 6px;
}

/* Card */
.card {
    background: linear-gradient(145deg, #0d1220, #10162a);
    border: 1px solid #1e293b;
    border-radius: 18px;
    padding: 24px 26px;
    margin-bottom: 20px;
    box-shadow: 0 10px 24px rgba(0,0,0,0.35);
}
.card-flat {
    background: rgba(255,255,255,0.03);
    border: 1px solid #1e293b;
    border-radius: 12px;
    padding: 16px 18px;
}

/* Badges / chips */
.badge {
    display: inline-block;
    font-size: 12px;
    font-weight: 700;
    padding: 4px 12px;
    border-radius: 999px;
    background: rgba(34, 197, 94, 0.15);
    color: #22c55e;
    border: 1px solid rgba(34, 197, 94, 0.3);
}
.chip {
    display: inline-block;
    padding: 3px 11px;
    border-radius: 999px;
    background: rgba(59,130,246,0.15);
    border: 1px solid rgba(59,130,246,0.3);
    color: #93c5fd;
    font-size: 12px;
    font-weight: 600;
    margin-right: 6px;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(90deg, #2563eb, #1d4ed8);
    color: white;
    border-radius: 14px;
    padding: 10px 24px;
    font-weight: 700;
    border: none;
    transition: 0.2s;
}
.stButton > button:hover {
    transform: scale(1.02);
}

.stDownloadButton > button {
    background: linear-gradient(90deg, #16a34a, #22c55e);
    color: white;
    border-radius: 14px;
    font-weight: 700;
    border: none;
    padding: 10px 24px;
}

/* Inputs */
input, textarea {
    background-color: #0d1220 !important;
    color: #e5e7eb !important;
    border-radius: 12px !important;
}

/* progress bar */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #3b82f6, #a855f7);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #050810, #05070d);
    border-right: 1px solid #1e293b;
}
section[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    border-radius: 12px;
    background: transparent;
    color: #94a3b8;
    border: 1px solid transparent;
    padding: 10px;
    text-align: left;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(59, 130, 246, 0.15);
    border: 1px solid #3b82f6;
    color: #e5e7eb;
}
section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: rgba(59, 130, 246, 0.25);
    border: 1px solid #3b82f6;
    color: #e5e7eb;
}
section[data-testid="stSidebar"]::-webkit-scrollbar { width: 6px; }
section[data-testid="stSidebar"]::-webkit-scrollbar-thumb {
    background: #1e293b;
    border-radius: 10px;
}

.brand-title {
    font-weight: 800;
    font-size: 21px;
    color: #93c5fd;
    text-align: center;
}

.user-card {
    background: #0d1220;
    border: 1px solid #1e293b;
    border-radius: 12px;
    padding: 12px 14px;
}
.user-avatar {
    display: inline-block;
    width: 34px; height: 34px; border-radius: 50%;
    background: linear-gradient(135deg, #3b82f6, #a855f7);
    text-align: center; line-height: 34px;
    font-weight: 800; font-size: 14px; color: white;
}

/* KPI card */
.kpi-card {
    background: linear-gradient(145deg, #0d1220, #10162a);
    border: 1px solid #1e293b;
    border-radius: 18px;
    padding: 20px 22px;
}

/* AI chat bubble */
.ai-bubble {
    background: rgba(59,130,246,0.08);
    border: 1px solid rgba(59,130,246,0.3);
    border-radius: 16px;
    padding: 18px 20px;
    max-width: 640px;
    margin-bottom: 6px;
}
.ai-bubble-label {
    font-size: 12px; font-weight: 800; letter-spacing:0.06em;
    text-transform: uppercase; color: #93c5fd; margin-bottom: 6px;
}

/* Step indicator */
.stepper { display:flex; align-items:center; margin: 6px 0 22px 0; }
.step-item { display:flex; align-items:center; flex:1; }
.step-circle {
    width: 30px; height: 30px; border-radius: 50%;
    display:flex; align-items:center; justify-content:center;
    font-size: 13px; font-weight: 800; flex-shrink:0;
    border: 2px solid #1e293b;
    color: #94a3b8;
    background: #0d1220;
}
.step-circle.done {
    background: linear-gradient(135deg, #3b82f6, #a855f7);
    border-color: transparent; color: white;
}
.step-circle.active {
    border-color: #3b82f6;
    color: #3b82f6;
}
.step-label {
    margin-left: 9px; font-size: 13px; font-weight: 700; color: #94a3b8;
    white-space: nowrap;
}
.step-label.active-label { color: #e5e7eb; }
.step-line {
    flex:1; height: 2px; background: #1e293b; margin: 0 10px;
}
.step-line.done { background: linear-gradient(90deg, #3b82f6, #a855f7); }

/* Hero */
.hero {
    text-align:center;
    padding: 60px 30px;
    border-radius: 24px;
    background: linear-gradient(145deg, #0d1220, #10162a);
    border: 1px solid #1e293b;
    margin-bottom: 26px;
}
.hero-title {
    font-size: 42px;
    font-weight: 800;
    color: #e5e7eb;
    margin-bottom: 4px;
}
.hero-sub { font-size: 18px; color: #94a3b8; margin-top: 8px; }
.hero-desc {
    max-width: 680px;
    margin: 18px auto 0 auto;
    color: #94a3b8;
    line-height: 1.6;
}

.feat-num {
    width:34px; height:34px; border-radius:10px;
    background: rgba(59,130,246,0.15); border:1px solid rgba(59,130,246,0.3);
    text-align: center; line-height: 34px;
    font-weight:800; color:#93c5fd; font-size:14px; margin-bottom:10px;
}

.hiw-item { display:flex; gap:14px; align-items:flex-start; padding: 10px 0; }
.hiw-badge {
    width:28px; height:28px; border-radius:50%;
    background: linear-gradient(135deg, #3b82f6, #a855f7);
    color:white; font-weight:800; font-size:13px;
    text-align: center; line-height: 28px; flex-shrink:0;
}

.empty-state { text-align:center; padding: 34px 10px; color: #94a3b8; }

.disclaimer {
    border-left: 3px solid #f59e0b;
    background: rgba(245,158,11,0.08);
}

.activity-row {
    padding:10px 2px; border-bottom:1px solid #1e293b;
}
</style>
""", unsafe_allow_html=True)

if "page" not in st.session_state:
    st.session_state.page = "landing"

if "user" not in st.session_state:
    st.session_state.user = "Guest User"

if "step" not in st.session_state:
    st.session_state.step = 1

# ===== USER HISTORY INIT =====
if "history" not in st.session_state:
    st.session_state.history = []

# =====================================================
# API CONFIG
# =====================================================
API_KEY = st.secrets.get("API_KEY", "")
API_URL = "https://openrouter.ai/api/v1/chat/completions"
if not API_KEY:
    st.error("⚠️ API_KEY not set. Add it under Settings → Secrets as `API_KEY = \"your-key\"`.")
    st.stop()

# =====================================================
# SESSION STATE
# =====================================================
defaults = {
    "step": 1,
    "questions": [],
    "answers": {},
    "final_doc": "",
    "extra": ""
}
for k, v in defaults.items():
    st.session_state.setdefault(k, v)

# =====================================================
# LOAD PREBUILT RAG (FAST)
# =====================================================
@st.cache_resource
def load_rag():
    index = faiss.read_index("faiss.index")
    with open("clauses.json", "r", encoding="utf-8") as f:
        clauses = json.load(f)
    embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return index, clauses, embedder

try:
    faiss_index, rag_clauses, embedder = load_rag()
except Exception as e:
    st.error(f"⚠️ Could not load the legal knowledge base (faiss.index / clauses.json). Make sure both files sit next to app.py.\n\nDetails: {e}")
    st.stop()

def retrieve_clauses(query, k=3):
    q_emb = embedder.encode([query])
    _, idx = faiss_index.search(q_emb, k)
    return "\n".join(rag_clauses[i] for i in idx[0] if i != -1)

# =====================================================
# LLM CALL (SINGLE, FAST)
# =====================================================
def call_llm(prompt, temp=0.25, tokens=1400):
    try:
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
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"]
    except requests.exceptions.Timeout:
        st.error("⏱️ The AI took too long to respond. Please try again.")
        st.stop()
    except requests.exceptions.RequestException as e:
        st.error(f"⚠️ Could not reach the AI service. Details: {e}")
        st.stop()
    except (KeyError, IndexError, json.JSONDecodeError):
        st.error("⚠️ The AI returned an unexpected response. Please try again.")
        st.stop()


# =====================================================
# SIDEBAR
# =====================================================
def sidebar():
    with st.sidebar:

        # ================= COLLAPSE TOGGLE =================
        if "collapsed" not in st.session_state:
            st.session_state.collapsed = False

        toggle = "➡️" if st.session_state.collapsed else "⬅️  Collapse"
        if st.button(toggle, use_container_width=True):
            st.session_state.collapsed = not st.session_state.collapsed
            st.rerun()

        # ================= BRAND =================
        if not st.session_state.collapsed:
            st.markdown("""
            <div class="brand-wrap">
                <div class="brand-title">⚖️ LegalDoc AI</div>
                <div class='muted' style="font-size:12.5px; margin-top:2px;">AI Legal Workspace</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("<div style='text-align:center; font-size:22px; margin-bottom:10px;'>⚖️</div>", unsafe_allow_html=True)

        # ================= NAV BUTTON FUNCTION =================
        def nav_item(icon, label, page):
            active = st.session_state.page == page
            text = f"{icon}  {label}" if not st.session_state.collapsed else icon
            if st.button(text, use_container_width=True,
                         type="primary" if active else "secondary",
                         key=f"nav_{page}"):
                st.session_state.page = page
                st.rerun()

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

        # ================= NAVIGATION =================
        nav_item("🏠", "Dashboard", "dashboard")
        nav_item("📄", "New Document", "document")
        nav_item("📜", "History", "history")

        st.markdown("<br>", unsafe_allow_html=True)

        # ================= USER CARD =================
        if not st.session_state.collapsed:
            initials = "".join([p[0] for p in st.session_state.user.split()[:2]]).upper()
            st.markdown(f"""
            <div class='user-card'>
                <div class='user-avatar'>{initials}</div>
                <div>
                    <div style="font-weight:700; font-size:14px;">{st.session_state.user}</div>
                    <div class='muted' style="font-size:12px;">Active session</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

            # ================= QUICK STATS =================
            st.markdown(f"""
            <div class='card-flat'>
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span class='muted' style="font-size:13px;">📄 Documents drafted</span>
                    <b>{len(st.session_state.history)}</b>
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-top:8px;">
                    <span class='muted' style="font-size:13px;">⚡ Engine status</span>
                    <span class="badge"><span class="badge-dot"></span>Live</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ================= FOOTER =================
        if not st.session_state.collapsed:
            st.markdown("""
            <div style="text-align:center; margin-top:20px;" class='muted'>
                <span style="font-size:12px;">LegalDoc AI • v2.0</span>
            </div>
            """, unsafe_allow_html=True)

# =====================================================
# STEP INDICATOR COMPONENT
# =====================================================
def render_stepper(current_step):
    labels = ["Select", "Questions", "Review", "Generate"]
    html = "<div class='stepper'>"
    for i, label in enumerate(labels, start=1):
        if i < current_step:
            circle_class, content = "done", "✓"
        elif i == current_step:
            circle_class, content = "active", str(i)
        else:
            circle_class, content = "", str(i)
        label_class = "active-label" if i == current_step else ""
        html += f"""
        <div class="step-item">
            <div class="step-circle {circle_class}">{content}</div>
            <div class="step-label {label_class}">{label}</div>
        </div>
        """
        if i != len(labels):
            line_class = "done" if i < current_step else ""
            html += f"<div class='step-line {line_class}'></div>"
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

# =====================================================
# DASHBOARD
# =====================================================
def dashboard_ui():
    st.markdown("<div class='app-title'>📊 Dashboard</div>", unsafe_allow_html=True)
    st.markdown("<div class='muted'>Your AI-powered legal document workspace, at a glance.</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ================= KPI CARDS =================
    def kpi(title, value, icon, color):
        return f"""
        <div class='kpi-card'>
            <div>
                <div class='muted' style="font-size:13px;">{title}</div>
                <h1 style="margin:2px 0 0 0; font-size:28px; color:{color};">{value}</h1>
            </div>
            <div class='kpi-icon' style="background:{color}22; border:1px solid {color}44;">{icon}</div>
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

    st.markdown("<br>", unsafe_allow_html=True)

    # ================= MAIN GRID =================
    left, right = st.columns([2.5, 1.5])

    with left:
        st.markdown("""
        <div class='card'>
            <div class="eyebrow">Get Started</div>
            <h2 style="margin:0 0 6px 0;">📝 Create a Legal Document</h2>
            <p class='muted' style="margin:0;">
                Generate Indian legal documents using AI + verified clauses,
                in a guided step-by-step flow.
            </p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("➕  Start New Document", use_container_width=True):
            st.session_state.page = "document"
            st.session_state.step = 1
            st.session_state.questions = []
            st.session_state.answers = {}
            st.session_state.q_index = 0
            st.session_state.saved = False
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # ===== DOCUMENT TYPE ANALYTICS =====
        doc_types = {}
        for item in st.session_state.history:
            doc_types[item["document"]] = doc_types.get(item["document"], 0) + 1

        st.markdown("<div class='section-title' style='font-size:18px;'>📊 Document Insights</div>", unsafe_allow_html=True)
        if doc_types:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.bar_chart(doc_types, color="#3b82f6")
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='card empty-state'>
                <div class='icon'>🚀</div>
                <div>No analytics yet. Create your first document to see insights here.</div>
            </div>
            """, unsafe_allow_html=True)

    with right:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin-top:0;'>📜 Recent Activity</h3>", unsafe_allow_html=True)

        if not st.session_state.history:
            st.markdown("""
            <div class='empty-state'>
                <div class='icon'>🗂️</div>
                <div style="font-size:13.5px;">No activity yet</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for item in st.session_state.history[-5:][::-1]:
                st.markdown(f"""
                <div class="activity-row">
                    <div>
                        <b style="font-size:14px;">{item['document']}</b><br>
                        <span class='muted' style="font-size:12.5px;">{item['subtype']}</span>
                    </div>
                    <span class="chip">Done</span>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div class='card'>
            <h3 style="margin-top:0;">⚡ Quick Actions</h3>
        </div>
        """, unsafe_allow_html=True)

        if st.button("📄  New Document", use_container_width=True):
            st.session_state.page = "document"
            st.rerun()

        if st.button("📜  View History", use_container_width=True):
            st.session_state.page = "history"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ================= FOOTER INFO =================
    st.markdown("""
    <div class='card disclaimer'>
        ⚠️ <b>Disclaimer:</b> AI-generated documents must be reviewed by a legal professional before official use.
    </div>
    """, unsafe_allow_html=True)


def landing_ui():

    # ================= HERO SECTION =================
    st.markdown(
        """
        <div class="hero">
            <div class="hero-title">⚖️ LegalDoc AI</div>
            <p class="hero-sub">AI-Powered Indian Legal Document Generator</p>
            <p class="hero-desc">
                Create legally structured Indian documents using AI-guided workflows,
                verified legal clauses, and a fast, secure drafting experience.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        if st.button("🚀  Get Started", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)

    # ================= FEATURES =================
    st.markdown("<div class='section-title'>Why LegalDoc AI?</div>", unsafe_allow_html=True)

    f1, f2, f3, f4 = st.columns(4)
    features = [
        ("⚖️", "Legal Accuracy", "Clause-based drafting using verified Indian legal formats."),
        ("🤖", "AI Guided", "Chat-style questions to capture all legal requirements."),
        ("🔐", "Secure Access", "Backend-based authentication with hashed passwords."),
        ("⚡", "Fast & Optimized", "Single optimized AI call with RAG support."),
    ]
    for col, (icon, title, desc) in zip([f1, f2, f3, f4], features):
        with col:
            st.markdown(f"""
            <div class="card" style="min-height:170px;">
                <div class="feat-num">{icon}</div>
                <h3 style="margin:0 0 6px 0; font-size:16px;">{title}</h3>
                <p class="muted" style="margin:0; font-size:13.5px; line-height:1.5;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ================= HOW IT WORKS =================
    st.markdown("<div class='section-title'>How it works</div>", unsafe_allow_html=True)

    steps = [
        "Select document type & variant",
        "Answer AI-guided legal questions",
        "Review and customize clauses",
        "Download ready-to-use legal document",
    ]
    rows = "".join(
        f"""<div class="hiw-item">
                <div class="hiw-badge">{i}</div>
                <div class="muted" style="padding-top:3px;">{s}</div>
            </div>"""
        for i, s in enumerate(steps, start=1)
    )
    st.markdown(f"<div class='card'>{rows}</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ================= TRUST / DISCLAIMER =================
    st.markdown(
        """
        <div class="card disclaimer">
            ⚠️ <b>Disclaimer:</b>
            AI-generated documents should be reviewed by a qualified legal
            professional before official or legal use.
        </div>
        """,
        unsafe_allow_html=True
    )


# =====================================================
# DOCUMENT CREATION (STEPPER)
# =====================================================
def document_ui():

    render_stepper(st.session_state.step)
    st.markdown("<div class='app-title'>📄 Create Legal Document</div>", unsafe_allow_html=True)
    st.markdown("<div class='muted'>Follow the guided steps below to generate your document.</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # ================= STEP 1 =================
    if st.session_state.step == 1:
        st.markdown("""
        <div class='card'>
            <div class="eyebrow">Step 1</div>
            <h3 style="margin:0;">Select Document</h3>
        </div>
        """, unsafe_allow_html=True)

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

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Next →", use_container_width=True):
            st.session_state.document = document
            st.session_state.subtype = subtype
            st.session_state.step = 2
            st.session_state.q_index = 0
            st.rerun()

    # ================= STEP 2 (CHAT-STYLE QUESTIONS) =================
    elif st.session_state.step == 2:
        st.markdown("""
        <div class='card'>
            <div class="eyebrow">Step 2</div>
            <h3 style="margin:0;">AI is asking questions</h3>
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

        if q_index < len(questions):
            current_question = questions[q_index]
            progress_pct = q_index / max(len(questions), 1)
            st.progress(progress_pct)
            st.caption(f"Question {q_index + 1} of {len(questions)}")

            st.markdown(
                f"""
                <div class='ai-bubble'>
                    <div class="ai-bubble-label"><span class="ai-avatar">🤖</span> AI Assistant</div>
                    {current_question}
                </div>
                """,
                unsafe_allow_html=True
            )

            answer = st.text_input("Your answer", key=f"answer_{q_index}")

            if st.button("Next Question →", use_container_width=True):
                st.session_state.answers[current_question] = answer
                st.session_state.q_index += 1
                st.rerun()

        else:
            st.markdown("""
            <div class="badge" style="margin-bottom:14px;">
                <span class="badge-dot"></span> All questions completed
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<h4 style='margin-bottom:6px;'>Additional Instructions (Optional)</h4>", unsafe_allow_html=True)
            st.session_state.extra = st.text_area(
                "Add special clauses",
                placeholder="Example: No subletting, parking included",
                label_visibility="collapsed"
            )

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Continue → Review", use_container_width=True):
                st.session_state.step = 3
                st.rerun()

    # ================= STEP 3 (REVIEW) =================
    elif st.session_state.step == 3:
        st.markdown("""
        <div class='card'>
            <div class="eyebrow">Step 3</div>
            <h3 style="margin:0;">Review Your Details</h3>
        </div>
        """, unsafe_allow_html=True)

        for q, a in st.session_state.answers.items():
            st.markdown(f"""
            <div class='card-flat' style="margin-bottom:10px;">
                <div class="muted" style="font-size:12.5px; margin-bottom:4px;">{q}</div>
                <div style="font-weight:600;">{a if a else '—'}</div>
            </div>
            """, unsafe_allow_html=True)

        if st.session_state.extra:
            st.markdown(f"""
            <div class='card-flat' style="margin-bottom:10px; border-color: rgba(168,85,247,0.3);">
                <div class="muted" style="font-size:12.5px; margin-bottom:4px;">✨ Extra Instructions</div>
                <div style="font-weight:600;">{st.session_state.extra}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Generate Final Document →", use_container_width=True):
            st.session_state.step = 4
            st.rerun()

    # ================= STEP 4 (FINAL OUTPUT) =================
    elif st.session_state.step == 4:
        st.markdown("""
        <div class='card'>
            <div class="eyebrow">Step 4</div>
            <h3 style="margin:0;">Final Document</h3>
        </div>
        """, unsafe_allow_html=True)

        if not st.session_state.final_doc:
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

        # ===== SAVE TO HISTORY (ONLY ONCE) =====
        if not st.session_state.get("saved", False):
            st.session_state.history.append({
                "document": st.session_state.document,
                "subtype": st.session_state.subtype,
                "content": st.session_state.final_doc
            })
            st.session_state.saved = True

        st.markdown(f"""
        <div style="margin-bottom:10px;">
            <span class="chip">{st.session_state.document}</span>
            <span class="chip">{st.session_state.subtype}</span>
            <span class="badge"><span class="badge-dot"></span>Ready</span>
        </div>
        """, unsafe_allow_html=True)

        st.text_area("Final Document", st.session_state.final_doc, height=450, label_visibility="collapsed")

        docx_path = create_docx(st.session_state.final_doc)

        col1, col2 = st.columns([1, 1])
        with col1:
            with open(docx_path, "rb") as f:
                st.download_button(
                    label="⬇  Download as DOCX",
                    data=f,
                    file_name="Legal_Document.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
        with col2:
            if st.button("➕  Create New Document", use_container_width=True):
                st.session_state.step = 1
                st.session_state.questions = []
                st.session_state.answers = {}
                st.session_state.final_doc = ""
                st.session_state.extra = ""
                st.session_state.q_index = 0
                st.session_state.saved = False
                st.rerun()

        st.markdown("""
        <div class='card disclaimer' style="margin-top:20px;">
            ⚠️ <b>Disclaimer:</b> Please have this document reviewed by a qualified legal professional before use.
        </div>
        """, unsafe_allow_html=True)


def history_ui():
    st.markdown("<div class='app-title'>📜 Your Generated Documents</div>", unsafe_allow_html=True)
    st.markdown("<div class='muted'>All documents you've drafted in this session.</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    if not st.session_state.history:
        st.markdown("""
        <div class='card empty-state'>
            <div class='icon'>🗂️</div>
            <div>No documents generated yet.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    for i, item in enumerate(st.session_state.history):
        with st.expander(f"📄  {item['document']}  ·  {item['subtype']}"):
            st.text_area(
                "Document Content",
                item["content"],
                height=300,
                label_visibility="collapsed",
                key=f"hist_{i}"
            )

# =====================================================
# ROUTER
# =====================================================
if st.session_state.page != "landing":
    sidebar()

# ===== PAGE ROUTER =====
if st.session_state.page == "landing":
    landing_ui()

elif st.session_state.page == "dashboard":
    dashboard_ui()

elif st.session_state.page == "document":
    document_ui()

elif st.session_state.page == "history":
    history_ui()
