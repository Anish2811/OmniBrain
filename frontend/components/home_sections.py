import streamlit as st


def render_main_features():
    """
    Reusable section displaying the main features
    of the OmniBrain platform.
    """

    st.subheader("Main Features")

    col1, col2 = st.columns(2)

    with col1:
        st.info("Upload Financial Reports")
        st.info("AI Document Analysis")

    with col2:
        st.info("Charts & Table Extraction")
        st.info("AI Generated Results")