import streamlit as st

from components.header import render_header
from components.uploader import render_uploader

render_header(
    "📤 Upload Documents",
    "Upload financial reports for AI-powered analysis."
)

uploaded_file = render_uploader()

st.markdown("---")

if uploaded_file:

    if st.button("🚀 Analyze Document"):

        st.success("Analysis will be connected with the backend soon.")

else:

    st.info("Upload a document to continue.")