import streamlit as st


st.title("Analysis Results")

st.write(
    "View the results generated from the uploaded financial report."
)

st.markdown("---")

# Check whether a document has been uploaded
uploaded_file = st.session_state.get("uploaded_file")

if uploaded_file is None:
    st.warning("No document has been uploaded yet.")
    st.info("Upload a financial report before viewing results.")

else:
    st.subheader("Document")

    st.write(f"File: {uploaded_file.name}")

    st.markdown("---")

    st.subheader("Analysis Summary")

    # These values will be updated when backend analysis is available
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Documents", "1")

    with col2:
        st.metric("Tables", "0")

    with col3:
        st.metric("Charts", "0")

    st.markdown("---")

    st.subheader("Summary")

    st.info("Analysis results are not available yet.")

    st.markdown("---")

    st.subheader("Extracted Content")

    tab1, tab2, tab3 = st.tabs(["Text", "Tables", "Charts"])

    with tab1:
        st.write("Extracted text will appear here.")

    with tab2:
        st.write("Detected tables will appear here.")

    with tab3:
        st.write("Detected charts will appear here.")