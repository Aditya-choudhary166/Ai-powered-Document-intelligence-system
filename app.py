import streamlit as st
import pandas as pd
from config.settings import PAGE_TITLE
from modules.pdf_processor import extract_pdf
from modules.rag_engine import DocumentStore
from modules.ai_engine import AIEngine
from modules.report_generator import build_pdf_report

st.set_page_config(page_title=PAGE_TITLE, page_icon="📄", layout="wide")
st.markdown("""
<style>
.block-container{padding-top:1.6rem;max-width:1400px}
[data-testid="stMetric"]{background:#f5f7fb;padding:16px;border-radius:12px;border:1px solid #e7eaf1}
section[data-testid="stSidebar"]{background:#f7f8fc}
h1,h2,h3{color:#172554}
</style>
""", unsafe_allow_html=True)

if "docs" not in st.session_state: st.session_state.docs = []
if "store" not in st.session_state: st.session_state.store = DocumentStore()
if "analysis" not in st.session_state: st.session_state.analysis = {}
if "messages" not in st.session_state: st.session_state.messages = []

engine = AIEngine()
st.title("📄 DocuMind AI")
st.caption("AI-powered document intelligence & business automation")

with st.sidebar:
    st.header("Workspace")
    page = st.radio("Navigate", ["Dashboard", "Document Analysis", "AI Chat", "Risk Intelligence", "Action Center", "Reports"])
    st.divider()
    api_ready = bool(engine.api_key)
    st.caption("Groq API: " + ("🟢 Configured" if api_ready else "🟠 Not configured"))
    st.caption("Add GROQ_API_KEY to your .env file.")

if page == "Dashboard":
    st.subheader("Workspace overview")
    risks = st.session_state.analysis.get("risks", [])
    high = sum(1 for r in risks if str(r.get("level","")).lower()=="high")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Documents", len(st.session_state.docs))
    c2.metric("Processed", sum(1 for d in st.session_state.docs if d.get("text")))
    c3.metric("Identified risks", len(risks))
    c4.metric("High risks", high)
    st.markdown("### Recent documents")
    if st.session_state.docs:
        st.dataframe(pd.DataFrame([{"Document":d["name"],"Pages":d["pages"],"Characters":len(d["text"])} for d in st.session_state.docs]), use_container_width=True, hide_index=True)
    else:
        st.info("Upload a PDF in Document Analysis to get started.")
    if risks:
        st.markdown("### Risk distribution")
        st.bar_chart(pd.Series([r.get("level","Unknown") for r in risks]).value_counts())

elif page == "Document Analysis":
    st.subheader("Upload and analyze documents")
    uploads = st.file_uploader("Choose PDF documents", type=["pdf"], accept_multiple_files=True)
    if st.button("Process uploaded PDFs", type="primary", disabled=not uploads):
        new_docs=[]
        with st.spinner("Extracting text and building searchable index..."):
            for up in uploads:
                try:
                    text, pages = extract_pdf(up.getvalue())
                    if not text.strip(): st.warning(f"No extractable text found in {up.name}. It may be scanned.")
                    else:
                        doc={"name":up.name,"text":text,"pages":pages}
                        new_docs.append(doc)
                except Exception as e:
                    st.error(f"{up.name}: {e}")
            if new_docs:
                st.session_state.docs = new_docs
                st.session_state.store.build(new_docs)
                st.session_state.analysis = {}
                st.success(f"Processed {len(new_docs)} document(s).")
    if st.session_state.docs:
        for d in st.session_state.docs:
            with st.expander(f"{d['name']} · {d['pages']} pages"):
                st.write(d["text"][:2500] + ("…" if len(d["text"])>2500 else ""))
        if st.button("Run full AI analysis", type="primary"):
            if not engine.api_key:
                st.error("Set GROQ_API_KEY in .env and restart the app.")
            else:
                with st.spinner("Analyzing documents with Groq..."):
                    try:
                        st.session_state.analysis = engine.analyze(st.session_state.docs)
                        st.success("Analysis complete.")
                    except Exception as e: st.error(str(e))
    else:
        st.info("Upload one or more text-based PDFs. A sample contract is included in sample_documents/.")

elif page == "AI Chat":
    st.subheader("Ask your documents")
    if not st.session_state.docs:
        st.info("Process PDFs first in Document Analysis.")
    else:
        for m in st.session_state.messages:
            with st.chat_message(m["role"]): st.markdown(m["content"])
        question = st.chat_input("Ask a question grounded in your uploaded documents...")
        if question:
            st.session_state.messages.append({"role":"user","content":question})
            with st.chat_message("user"): st.markdown(question)
            with st.chat_message("assistant"):
                if not engine.api_key:
                    answer="Configure GROQ_API_KEY in your .env file to enable AI answers."
                    st.warning(answer)
                else:
                    with st.spinner("Searching documents and generating answer..."):
                        try:
                            chunks=st.session_state.store.search(question, k=5)
                            answer=engine.answer(question, chunks)
                            st.markdown(answer)
                            with st.expander("Retrieved sources"):
                                for ch in chunks: st.caption(f"{ch['source']} · page {ch['page']}")
                        except Exception as e:
                            answer=f"Could not answer: {e}"
                            st.error(answer)
            st.session_state.messages.append({"role":"assistant","content":answer})

elif page == "Risk Intelligence":
    st.subheader("Potential contract risks")
    if not st.session_state.analysis:
        st.info("Run full AI analysis from Document Analysis first.")
    else:
        risks=st.session_state.analysis.get("risks",[])
        if risks:
            for r in risks:
                level=str(r.get("level","Medium")).upper()
                with st.expander(f"{'🔴' if level=='HIGH' else '🟠' if level=='MEDIUM' else '🟢'} {level}: {r.get('title','Potential risk')}"):
                    st.write(r.get("description",""))
                    st.caption(f"Evidence: {r.get('evidence','Not specified')} · Source: {r.get('source','Not specified')} · Page: {r.get('page','Not specified')}")
                    st.caption("AI-generated flag for human review; not legal advice.")
        else: st.success("No potential risks were returned by the model.")

elif page == "Action Center":
    st.subheader("Recommended actions")
    actions=st.session_state.analysis.get("actions",[])
    if not st.session_state.analysis: st.info("Run full AI analysis first.")
    elif actions:
        for i,a in enumerate(actions,1):
            st.checkbox(f"{i}. {a.get('task','Review item')}", key=f"action_{i}")
            st.caption(f"Owner: {a.get('owner','Unassigned')} · Deadline: {a.get('deadline','Not specified')} · Priority: {a.get('priority','Medium')}")
    else: st.info("No action items identified.")

elif page == "Reports":
    st.subheader("Download analysis report")
    if not st.session_state.docs: st.info("Upload and process a document first.")
    else:
        if not st.session_state.analysis: st.warning("Run full AI analysis to include AI findings. You can still download a basic report.")
        if st.button("Generate PDF report", type="primary"):
            try:
                pdf=build_pdf_report(st.session_state.docs, st.session_state.analysis)
                st.download_button("⬇️ Download PDF report", data=pdf, file_name="document_intelligence_report.pdf", mime="application/pdf")
            except Exception as e: st.error(f"Report generation failed: {e}")

st.divider()
st.caption("DocuMind AI · Evidence-grounded document analysis. AI outputs require human verification.")
