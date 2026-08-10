import streamlit as st

st.title("Chat")

st.write("Ask questions about the uploaded financial report.")

uploaded_file = st.session_state.get("uploaded_file")

if uploaded_file is None:
    st.warning("Please upload a financial report first.")
else:
    st.success(f"Document: {uploaded_file.name}")

    query = st.text_area(
        "Enter your question",
        placeholder="Ask something about the report..."
    )

    if st.button("Ask"):
        if query.strip():
            st.info("Response will appear here after backend integration.")
        else:
            st.warning("Please enter a question.")