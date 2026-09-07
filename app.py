import streamlit as st
from answer import answer_query

#setup the main dashboard header and
st.title("Local RAG Assistant")
st.caption("Offline Q&A powdered by Microsoft's Foundry Local")

#initialize the chat history in streamlit session state if it doesnt exist
if "messages" not in st.session_state:
    st.session_state.messages = []

#render all previous messages from history on rerender
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

#captures user input from the input box 
if question := st.chat_input("Ask a question"):
    #append and display the user question in the UI
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("User"):
        st.write(question)

    #generate answer while showing a spinnr and rendering assistant's response
    with st.chat_message("Assistant"):
        with st.spinner("Thinking... Please wait..."):
            answer = answer_query(question)
        st.write(answer)
    #save the asstistants response to the chat history
    st.session_state.messages.append({"role": "assistant", "content": answer})