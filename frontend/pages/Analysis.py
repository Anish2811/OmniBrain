import streamlit as st

st.title("Financial Analysis")

st.write(
    "Analyze the uploaded financial document and view the extracted "
    "financial information."
)

st.markdown("---")

st.subheader("Document Status")

if "uploaded_file" not in st.session_state:
    st.info("No document selected for analysis.")
else:
    st.success("Document is ready for analysis.")

st.markdown("---")

st.subheader("Analysis")

analysis_type = st.selectbox(
    "Select analysis type",
    [
        "Financial Summary",
        "Ratio Analysis",
        "Tables and Charts",
    ]
)

if st.button("Start Analysis"):
    if "uploaded_file" not in st.session_state:
        st.warning("Please upload a document first.")
    else:
        st.info(f"Starting {analysis_type}...")

st.markdown("---")

st.caption("Analysis results will be displayed after processing.")