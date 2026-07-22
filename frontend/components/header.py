import streamlit as st


def render_header(title, subtitle):
    """
    Reusable header for all frontend pages.
    """

    st.title(title)

    st.caption(subtitle)

    st.markdown("---")