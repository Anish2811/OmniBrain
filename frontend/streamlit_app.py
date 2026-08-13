import streamlit as st

st.set_page_config(
    page_title="OmniBrain",
    page_icon="OmniBrain",
    layout="wide"
)

st.title("OmniBrain")

st.subheader("Agentic Multi-Modal Financial Report Analysis")

st.success("Welcome to the OmniBrain Dashboard")

st.write("""
OmniBrain is an AI-powered platform for analyzing financial reports.
It combines OCR, Vision Language Models, RAG, and AI agents to
extract information, understand charts and tables, and generate
meaningful financial insights.
""")

st.markdown("---")

st.subheader("Platform Features")

col1, col2 = st.columns(2)

with col1:
    st.info("Upload Financial Reports")
    st.info("AI-Powered Document Analysis")
    st.info("OCR & Text Extraction")

with col2:
    st.info("Chart & Table Extraction")
    st.info("Multi-Agent Processing")
    st.info("AI-Generated Reports")

st.markdown("---")

st.subheader("Workflow")

st.write("""
1. Upload a financial report

2. OCR extracts text

3. Charts & tables are detected

4. AI agents analyze the report

5. Final insights are generated
""")

st.markdown("---")

st.subheader("Current Development Status")

st.progress(20)

st.caption("Frontend UI is under active development.")

st.success("Frontend dashboard initialized successfully.")

st.info("Backend integration will be added after API completion.")