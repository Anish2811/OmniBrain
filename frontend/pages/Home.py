import streamlit as st

from components.header import render_header

render_header(
    "🏠 Home",
    "Welcome to the OmniBrain Dashboard"
)

st.write("""
Welcome to OmniBrain.

This dashboard serves as the central hub for the application.
From here, users will be able to upload financial reports,
analyze them using AI-powered pipelines, and view the generated results.
""")

st.markdown("---")

st.subheader("🚀 Planned Features")

st.markdown("""
- 📤 Upload financial reports
- 📊 AI-powered document analysis
- 📑 View processed results
- 📈 Extract charts and tables
- 🤖 Multi-agent workflow
""")

st.info("Dashboard UI is currently under development.")

st.success("Frontend Home page initialized successfully.")