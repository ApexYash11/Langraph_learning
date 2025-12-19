import streamlit as st
from databse_backend import chatbot
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
import uuid

#Utility function to generate unique thread IDs
def generate_thread_id():
    # Use string form for stable keys across serialization and UI use.
    thread_id = str(uuid.uuid4())
    return thread_id

def reset_chat():
    thread_id=generate_thread_id()
    st.session_state["thread_id"]=thread_id
    add_thread(st.session_state["thread_id"])
    st.session_state["message_history"]=[]

def add_thread(thread_id):
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)

def load_conversation(thread_id):
    state = chatbot.get_state(config={"configurable": {"thread_id": thread_id}})
    values = getattr(state, "values", None) or {}
    if isinstance(values, dict) and "messages" in values:
        return values["messages"]
    return []



# session setup 
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = []
add_thread(st.session_state["thread_id"])


# sidebar ui 
st.sidebar.title("LangGraph Chatbot")

if st.sidebar.button("New chat"):
    reset_chat()

st.sidebar.header("My Chats")

for thread in st.session_state["chat_threads"]:
    if st.sidebar.button(str(thread)):
        st.session_state["thread_id"]=thread
        messages=load_conversation(thread)

        temp_message_history=[]
        for msg in messages:
            if isinstance(msg, HumanMessage):
                role="user"
            else:
                role="assistant"
            temp_message_history.append({"role": role, "content": msg.content})
        st.session_state["message_history"] = temp_message_history

# loading the conversation history
for message in st.session_state['message_history']:
    with st.chat_message(message["role"]):
        st.text(message["content"])

user_input = st.chat_input("Type your message here...")

if user_input:
    st.session_state['message_history'].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.text(user_input)

    config: RunnableConfig = {"configurable": {"thread_id": (st.session_state["thread_id"])}}       

    response = chatbot.invoke({"messages": [HumanMessage(content=user_input)]}, config=config)
    ai_message = response['messages'][-1].content
    st.session_state['message_history'].append({"role": "assistant", "content": ai_message})
    with st.chat_message("assistant"):
        st.text(ai_message)
