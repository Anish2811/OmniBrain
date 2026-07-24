import streamlit as st

from components.header import render_header

render_header(
    "🧠 OmniBrain",
    "Multi-Modal AI Platform for Financial Document Analysis"
)

st.success("🚀 Welcome to the OmniBrain Dashboard")

st.write(
    """
    OmniBrain helps analyze financial reports using AI-powered document
    processing, OCR, table extraction and intelligent report generation.
    """
)

st.markdown("---")

st.subheader("✨ Main Features")

col1, col2 = st.columns(2)

with col1:
    st.info("📤 Upload Financial Reports")
    st.info("🤖 AI Document Analysis")

with col2:
    st.info("📊 Charts & Table Extraction")
    st.info("📄 AI Generated Results")

st.markdown("---")

st.subheader("⚙ Workflow")

st.write("""
1. 📤 Upload your financial report

2. 🔍 AI extracts text, tables and charts

3. 🤖 Multi-agent pipeline processes the document

4. 📄 View summarized results and insights
""")

st.markdown("---")

st.subheader("📌 Project Status")

st.progress(20)

st.caption("Frontend implementation is currently in progress.")