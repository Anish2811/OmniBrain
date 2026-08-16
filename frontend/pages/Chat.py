import streamlit as st

from utils.api_client import request_analysis


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
        if not query.strip():
            st.warning("Please enter a question.")
        else:
            with st.spinner("Analyzing..."):
                response = request_analysis(query.strip())

            if response.get("success") is False:
                st.error(response.get("message", "Something went wrong."))
            elif "answer" in response:
                st.subheader("Answer")
                st.write(response["answer"])

                citations = response.get("citations", [])

                if citations:
                    st.subheader("Sources")

                    for i, citation in enumerate(citations, start=1):
                        document = citation.get("document")
                        page_number = citation.get("page_number")
                        snippet = citation.get("content_snippet", "")

                        source_name = document or "Unknown document"

                        if page_number is not None:
                            source_name += f" — Page {page_number}"

                        with st.expander(f"Source {i}: {source_name}"):
                            st.write(snippet)

                agent_trace = response.get("agent_trace", [])

                if agent_trace:
                    with st.expander("Agent Trace"):
                        st.write(" → ".join(agent_trace))
            else:
                st.error("Unexpected response received from the backend.")