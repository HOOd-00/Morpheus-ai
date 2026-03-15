import streamlit as st
from src.chatbot import get_agent_rag

st.set_page_config(
    page_title="Morpheus AI", 
    page_icon="🎬", 
    layout="centered"
)

st.title("🎬 Morpheus AI")
st.caption("Your personal film and VFX assistant (Powered by Agentic RAG)")

# Load Agent and store at session state
if "agent" not in st.session_state:
    with st.spinner("Loading AI Agent..."):
        st.session_state.agent = get_agent_rag()

# Initialize storage for chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! What kind of movies would you like me to recommend, or what VFX techniques would you like to know? Feel free to ask!"}
    ]

# Loop display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input box
if prompt := st.chat_input("I would like to ask about.."):
    # Display user prompt
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # AI process
    with st.chat_message("assistant"):
        with st.spinner("Morpheus is thinking..."):
            try:
                # Send user prompt attach with chat history
                chat_history = []
                
                for msg in st.session_state.messages[1:]: # ignore welcome msg
                    chat_history.append({"role": msg["role"], "content": msg["content"]})
                
                result = st.session_state.agent.invoke({
                    "messages": chat_history
                })
                
                # Response
                raw_content = result["messages"][-1].content
                if isinstance(raw_content, list):
                    text_blocks = [block['text'] for block in raw_content if isinstance(block, dict) and block.get('type') == 'text']
                    final_answer = "\n".join(text_blocks)
                else:
                    final_answer = raw_content
                
                # Display response
                st.markdown(final_answer)
                
                # Save response to history
                st.session_state.messages.append({"role": "assistant", "content": final_answer})
                
            except Exception as e:
                st.error(f"Error: {e}")