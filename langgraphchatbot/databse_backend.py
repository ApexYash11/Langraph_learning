from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated, Literal
from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from pydantic import SecretStr
from langgraph.graph.message import add_messages
import sqlite3

load_dotenv(dotenv_path="../.env")  # Load from parent directory

model_name = "gemini-2.5-flash"  # Valid model name
key = os.getenv("GOOGLE_API_KEY")
api_key = SecretStr(key) if key is not None else None
llm = ChatGoogleGenerativeAI(model=model_name, api_key=api_key)


class chatstate(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state: chatstate):
    message = state['messages']
    response = llm.invoke(message)
    return {"messages": [response]}

conn=sqlite3.connect(database="chatbot_state.db",check_same_thread=False)

# checkpointer using SQLite
checkpointer = SqliteSaver(conn=conn)

graph = StateGraph(chatstate)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)
