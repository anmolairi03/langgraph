from langgraph.graph import StateGraph, START, END, add_messages
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import TypedDict, Annotated
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv

load_dotenv()

model = ChatGoogleGenerativeAI(model = 'gemini-2.5-flash')

class ChatState(TypedDict):
    
    messages: Annotated[list[BaseMessage], add_messages]

def chatbot(state: ChatState) -> ChatState:
    response = model.invoke(state['messages'])
    
    return {'messages': [response.content]}

checkpointer = MemorySaver()
graph = StateGraph(ChatState)

graph.add_node('Chatbot', chatbot)

graph.add_edge(START, 'Chatbot')
graph.add_edge('Chatbot', END)

bot = graph.compile(checkpointer= checkpointer)



