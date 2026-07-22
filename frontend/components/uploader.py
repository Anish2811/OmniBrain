import streamlit as st


def render_uploader():
    """
    Reusable uploader component.
    """

    st.subheader("📤 Upload Financial Report")

    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"]
    )

    if uploaded_file is not None:
        st.success(f"Uploaded: {uploaded_file.name}")

        st.write(f"File Size: {uploaded_file.size / 1024:.2f} KB")

        st.info("Ready for AI processing.")

    else:
        st.warning("Please upload a PDF document.")

    return uploaded_file