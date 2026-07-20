import streamlit as st

st.set_page_config(
    page_title="OmniBrain",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 OmniBrain")

st.subheader("Agentic Multi-Modal RAG Orchestrator")

st.write(
    """
Welcome to OmniBrain.

This application is designed to process financial reports using
Agentic RAG, OCR, Vision Language Models and FastAPI.

The frontend is currently under active development.
"""
)

st.markdown("---")

st.sidebar.title("Navigation")

st.sidebar.info(
    """
Use the sidebar to access:

🏠 Home

📤 Upload

📊 Analysis

📑 Results
"""
)

st.success("Frontend project structure initialized successfully.")

st.info(
    "Backend integration will begin after API endpoints are finalized."
)
