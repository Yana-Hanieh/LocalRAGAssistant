import streamlit as st
from answer import answer_query

st.title("Local RAG Assistant")
st.caption("Offline Q&A powdered by Microsoft's Foundry Local")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if question := st.chat_input("Ask a question"):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("User"):
        st.write(question)

    with st.chat_message("Assistant"):
        with st.spinner("Thinking... Please wait..."):
            answer = answer_query(question)
        st.write(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})