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
