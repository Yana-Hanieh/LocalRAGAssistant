import streamlit as st
from answer import answer_query

st.title("Local RAG Assistant")
st.caption("Offline Q&A powdered by Microsoft's Foundry Local")

question = st.text_input("Ask a question:")

if question:
    answer_placeholder = st.empty()
    with st.spinner("Thinking... Please wait..."):
        answer = answer_query(question)
    st.write(answer)