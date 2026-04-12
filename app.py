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
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# PREMIUM CSS (THIS IS WHY UI DOESN'T LOOK BASIC)
# =====================================================
st.markdown("""
<style>
#MainMenu, footer {visibility: hidden;}

.stApp {
    background: radial-gradient(circle at top, #020617, #020617);
    color: #e5e7eb;
    font-family: 'Inter', sans-serif;
}

/* Card */
.card {
    background: linear-gradient(145deg, #020617, #020617);
    border: 1px solid #1e293b;
    border-radius: 20px;
    padding: 26px;
    margin-bottom: 22px;
    box-shadow: 0 0 0 rgba(0,0,0,0);
}

/* Section title */
.section-title {
    font-size: 26px;
    font-weight: 800;
    margin-bottom: 8px;
}

/* Muted text */
.muted {
    color: #94a3b8;
}

/* Button */
.stButton > button {
    background: linear-gradient(90deg, #2563eb, #1d4ed8);
    color: white;
    border-radius: 14px;
    padding: 10px 24px;
    font-weight: 700;
    border: none;
}

/* Inputs */
input, textarea {
    background-color: #020617 !important;
    color: #e5e7eb !important;
    border-radius: 12px !important;
}
/* SIDEBAR BASE */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #020617, #020617);
    border-right: 1px solid #1e293b;
    transition: all 0.3s ease;
}

/* BUTTONS */
section[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    border-radius: 12px;
    background: transparent;
    border: 1px solid transparent;
    padding: 10px;
    transition: all 0.2s ease;
}

/* HOVER EFFECT */
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(59, 130, 246, 0.15);
    border: 1px solid #3b82f6;
    transform: translateX(3px);
}

/* ACTIVE BUTTON */
section[data-testid="stSidebar"] .stButton > button:focus {
    background: rgba(59, 130, 246, 0.25);
    border: 1px solid #3b82f6;
}

/* SCROLLBAR CLEAN */
section[data-testid="stSidebar"]::-webkit-scrollbar {
    width: 6px;
}
section[data-testid="stSidebar"]::-webkit-scrollbar-thumb {
    background: #1e293b;
    border-radius: 10px;
}
/* ===== LOGIN CARD ===== */
.login-card {
    background: rgba(15, 23, 42, 0.6);
    backdrop-filter: blur(14px);
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 20px;
    padding: 40px 30px;
    margin-top: 80px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.4);
}

/* Center inputs */
.login-card input {
    margin-bottom: 10px;
}

/* Button animation */
.stButton > button {
    transition: 0.2s;
}

.stButton > button:hover {
    transform: scale(1.02);
}
</style>
""", unsafe_allow_html=True)

if "page" not in st.session_state:
    st.session_state.page = "landing"

if "user" not in st.session_state:
    st.session_state.user = None

if "step" not in st.session_state:
    st.session_state.step = 1

# ===== USER HISTORY INIT =====
if "history" not in st.session_state:
    st.session_state.history = []



# =====================================================
# API CONFIG
# =====================================================
API_KEY = "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"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
if not API_KEY:
    st.error("OPENROUTER_API_KEY not set")
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

faiss_index, rag_clauses, embedder = load_rag()

def retrieve_clauses(query, k=3):
    q_emb = embedder.encode([query])
    _, idx = faiss_index.search(q_emb, k)
    return "\n".join(rag_clauses[i] for i in idx[0] if i != -1)

# =====================================================
# LLM CALL (SINGLE, FAST)
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

        # ================= COLLAPSE TOGGLE =================
        if "collapsed" not in st.session_state:
            st.session_state.collapsed = False

        toggle = "➡️" if st.session_state.collapsed else "⬅️"
        if st.button(toggle, use_container_width=True):
            st.session_state.collapsed = not st.session_state.collapsed
            st.rerun()

        # ================= BRAND =================
        if not st.session_state.collapsed:
            st.markdown("""
            <div style="text-align:center; margin-bottom:20px;">
                <h2>⚖️ LegalDoc AI</h2>
                <div class='muted'>AI Legal Workspace</div>
            </div>
            """, unsafe_allow_html=True)

        # ================= NAV BUTTON FUNCTION =================
        def nav_item(icon, label, page):
            active = st.session_state.page == page

            text = f"{icon} {label}" if not st.session_state.collapsed else icon

            style = "background:#1e293b; border:1px solid #3b82f6;" if active else ""

            if st.button(text, use_container_width=True):
                st.session_state.page = page

        st.markdown("<hr>", unsafe_allow_html=True)

        # ================= NAVIGATION =================
        nav_item("🏠", "Dashboard", "dashboard")
        nav_item("📄", "New Document", "document")
        nav_item("📜", "History", "history")

        st.markdown("<br>", unsafe_allow_html=True)

        # ================= USER CARD =================
        if not st.session_state.collapsed:
            st.markdown(f"""
            <div class='card'>
                👤 <b>{st.session_state.user}</b><br>
                <span class='muted'>Active User</span>
            </div>
            """, unsafe_allow_html=True)

        # ================= QUICK STATS =================
        if not st.session_state.collapsed:
            st.markdown(f"""
            <div class='card'>
                📄 Docs: <b>{len(st.session_state.history)}</b><br>
                ⚡ Status: <span style="color:#22c55e;">Live</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ================= FOOTER =================
        if not st.session_state.collapsed:
            st.markdown("""
            <div style="text-align:center; margin-top:30px;" class='muted'>
                LegalDoc AI • v2.0
            </div>
            """, unsafe_allow_html=True)

# =====================================================
# DASHBOARD
# =====================================================
def dashboard_ui():
    st.markdown("<div class='app-title'>📊 Dashboard</div>", unsafe_allow_html=True)
    st.markdown("<div class='muted'>AI-powered legal document workspace</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ================= KPI CARDS =================
    def kpi(title, value, icon, color):
        return f"""
        <div class='card'>
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <div class='muted'>{title}</div>
                    <h1 style="margin:0; color:{color};">{value}</h1>
                </div>
                <div style="font-size:28px;">{icon}</div>
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

    st.markdown("<br>", unsafe_allow_html=True)

    # ================= MAIN GRID =================
    left, right = st.columns([2.5, 1.5])

    # =========================================================
    # LEFT SIDE (MAIN CONTENT)
    # =========================================================
    with left:

        # ===== ACTION CARD =====
        st.markdown("""
        <div class='card'>
            <h2>📝 Create Legal Document</h2>
            <p class='muted'>
                Generate Indian legal documents using AI + verified clauses.
            </p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("➕ Start New Document", use_container_width=True):
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

        if doc_types:
            st.markdown("<div class='card'><h3>📊 Document Insights</h3></div>", unsafe_allow_html=True)
            st.bar_chart(doc_types)
        else:
            st.info("No analytics yet. Create your first document 🚀")

    # =========================================================
    # RIGHT SIDE (SIDEBAR STYLE PANEL)
    # =========================================================
    with right:

        # ===== RECENT ACTIVITY =====
        st.markdown("<div class='card'><h3>📜 Recent Activity</h3>", unsafe_allow_html=True)

        if not st.session_state.history:
            st.markdown("<div class='muted'>No activity yet</div>", unsafe_allow_html=True)
        else:
            for item in st.session_state.history[-5:][::-1]:
                st.markdown(f"""
                <div style="padding:10px; border-bottom:1px solid #1e293b;">
                    <b>{item['document']}</b><br>
                    <span class='muted'>{item['subtype']}</span>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # ===== QUICK ACTIONS =====
        st.markdown("""
        <div class='card'>
            <h3>⚡ Quick Actions</h3>
        </div>
        """, unsafe_allow_html=True)

        if st.button("📄 New Document", use_container_width=True):
            st.session_state.page = "document"
            st.rerun()

        if st.button("📜 View History", use_container_width=True):
            st.session_state.page = "history"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ================= FOOTER INFO =================
    st.markdown("""
    <div class='card'>
        ⚠️ <b>Disclaimer:</b> AI-generated documents must be reviewed by a legal professional.
    </div>
    """, unsafe_allow_html=True)



def landing_ui():

    # ================= HERO SECTION =================
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

    # ================= CTA =================
    c1, c2, c3 = st.columns([1,1,1])
    with c2:
        if st.button("🚀 Get Started"):
            st.session_state.page = "dashboard"
            st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)

    # ================= FEATURES =================
    st.markdown(
        "<div class='section-title'>Why LegalDoc AI?</div>",
        unsafe_allow_html=True
    )

    f1, f2, f3, f4 = st.columns(4)

    with f1:
        st.markdown(
            """
            <div class="card">
                <h3>⚖️ Legal Accuracy</h3>
                <p class="muted">
                    Clause-based drafting using verified Indian legal formats.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with f2:
        st.markdown(
            """
            <div class="card">
                <h3>🤖 AI Guided</h3>
                <p class="muted">
                    Chat-style questions to capture all legal requirements.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with f3:
        st.markdown(
            """
            <div class="card">
                <h3>🔐 Secure Access</h3>
                <p class="muted">
                    Backend-based authentication with hashed passwords.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with f4:
        st.markdown(
            """
            <div class="card">
                <h3>⚡ Fast & Optimized</h3>
                <p class="muted">
                    Single optimized AI call with RAG support.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ================= HOW IT WORKS =================
    st.markdown(
        "<div class='section-title'>How it works</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="card">
            <ol class="muted">
                <li>Select document type & variant</li>
                <li>Answer AI-guided legal questions</li>
                <li>Review and customize clauses</li>
                <li>Download ready-to-use legal document</li>
            </ol>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ================= TRUST / DISCLAIMER =================
    st.markdown(
        """
        <div class="card">
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

    # ===== PROGRESS BAR =====
    progress_map = {1: 0.25, 2: 0.50, 3: 0.75, 4: 1.0}
    st.progress(progress_map.get(st.session_state.step, 0.25))
    st.caption(f"Step {st.session_state.step} of 4")

    st.markdown("<div class='app-title'>Create Legal Document</div>", unsafe_allow_html=True)

    # ================= STEP 1 =================
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
            st.session_state.q_index = 0   # 🔥 IMPORTANT
            st.rerun()

    # ================= STEP 2 (CHAT-STYLE QUESTIONS) =================
    elif st.session_state.step == 2:
        st.markdown("<div class='card'><b>Step 2: AI is asking questions</b></div>", unsafe_allow_html=True)

        # Generate questions once
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

            # AI bubble
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

    # ================= STEP 3 (REVIEW) =================
    elif st.session_state.step == 3:
        st.markdown("<div class='card'><b>Step 3: Review Your Details</b></div>", unsafe_allow_html=True)

        for q, a in st.session_state.answers.items():
            st.markdown(f"<div class='card'><b>{q}</b><br>{a}</div>", unsafe_allow_html=True)

        if st.session_state.extra:
            st.markdown(f"<div class='card'><b>Extra</b><br>{st.session_state.extra}</div>", unsafe_allow_html=True)

        if st.button("Generate Final Document"):
            st.session_state.step = 4
            st.rerun()

    # ================= STEP 4 (FINAL OUTPUT) =================
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

    # ===== SAVE TO HISTORY (ONLY ONCE) =====
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
    st.markdown("<div class='app-title'>📜 Your Generated Documents</div>", unsafe_allow_html=True)

    if not st.session_state.history:
        st.info("No documents generated yet.")
        return

    for i, item in enumerate(st.session_state.history):
        with st.expander(f"{i+1}. {item['document']} ({item['subtype']})"):
            st.text_area(
                "Document Content",
                item["content"],
                height=300
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

