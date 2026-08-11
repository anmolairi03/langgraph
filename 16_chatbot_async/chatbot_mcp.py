from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio

load_dotenv()

llm = ChatGoogleGenerativeAI(model = 'gemini-2.5-flash')

client = MultiServerMCPClient(
    {
        'Calculator_Server':{
            'transport': 'stdio',
            'command': 'python',        
            'args': ["16_chatbot_async/server.py"]
            }
    }
)

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    
async def build_graph():
    
    tools = await client.get_tools()
    llm_with_tools = llm.bind_tools(tools)
    
    async def chat_node(state: ChatState):
        """LLM node that may answer or request a tool call."""
        messages = state["messages"]
        response = await llm_with_tools.ainvoke(messages)
        return {"messages": [response]}
    
    
    tool_node = ToolNode(tools)
    graph = StateGraph(ChatState)
    graph.add_node("chat_node", chat_node)
    graph.add_node("tools", tool_node)

    graph.add_edge(START, "chat_node")

    graph.add_conditional_edges("chat_node",tools_condition)
    graph.add_edge('tools', 'chat_node')

    chatbot = graph.compile()
    return chatbot
    
async def main():
    chatbot = await build_graph()
    response = await chatbot.ainvoke({'messages': [HumanMessage(content='what is the multiplication of 432 and 3652. also divide the product with 765')]})
    
    print(response['messages'][-1].content[0]['text'])
    
    await asyncio.sleep(0.1)


if __name__ == '__main__':
    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy()
    )
    asyncio.run(main())