import streamlit as st

from components.header import render_header
from components.home_sections import render_main_features

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

# Reusable Main Features Section
render_main_features()

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