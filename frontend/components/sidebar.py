import streamlit as st


def render_sidebar():
    """
    Reusable sidebar component.
    """

    with st.sidebar:

        st.title("🧠 OmniBrain")

        st.markdown("---")

        st.subheader("Navigation")

        st.write("🏠 Home")

        st.write("📤 Upload")

        st.write("📊 Analysis")

        st.write("📄 Results")

        st.markdown("---")

        st.caption("Version 0.1")

        st.success("Frontend Module")