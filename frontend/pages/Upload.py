import streamlit as st

st.title("📤 Upload Financial Reports")

st.write(
    """
Upload annual reports, balance sheets, quarterly reports,
or any financial document for AI-powered analysis.
"""
)

st.markdown("---")

st.subheader("📁 Upload Document")

uploaded_file = st.file_uploader(
    "Choose a financial report",
    type=["pdf", "docx", "txt"]
)

if uploaded_file:
    st.success(f"Selected File: {uploaded_file.name}")

st.markdown("---")

st.subheader("📌 Supported File Types")

col1, col2 = st.columns(2)

with col1:
    st.info("📄 PDF Reports")
    st.info("📝 DOCX Documents")

with col2:
    st.info("📃 TXT Files")
    st.info("📊 Financial Statements")

st.markdown("---")

st.subheader("⚙ AI Processing Pipeline")

st.write("""
1. 📤 Upload document

2. 🔍 OCR & Text Extraction

3. 📊 Chart & Table Detection

4. 🤖 AI Financial Analysis

5. 📄 Generate Final Report
""")

st.markdown("---")

st.warning("Actual backend upload functionality will be connected after API integration.")

st.info("Maximum upload size and supported formats can be updated later.")