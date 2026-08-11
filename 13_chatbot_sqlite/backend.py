from langgraph.graph import StateGraph, START, END, add_messages
from langchain_core.messages import BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import TypedDict, Annotated
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash"
)


class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def chatbot(state: ChatState) -> ChatState:
    response = model.invoke(state["messages"])

    return {
        "messages": [response]
    }


conn = sqlite3.connect(
    database="chatbot.db",
    check_same_thread=False
)

checkpointer = SqliteSaver(conn=conn)

graph = StateGraph(ChatState)

graph.add_node("Chatbot", chatbot)

graph.add_edge(START, "Chatbot")
graph.add_edge("Chatbot", END)

bot = graph.compile(
    checkpointer=checkpointer
)


def retrieve_all_threads():
    all_threads = set()

    for checkpoint in checkpointer.list(None):
        thread_id = checkpoint.config["configurable"]["thread_id"]
        all_threads.add(thread_id)

    return all_threads

class ChatNameSchema(BaseModel):
    name: str = Field(description= 'Summarised name of the chat')
    
chat_name_llm = model.with_structured_output(ChatNameSchema)


