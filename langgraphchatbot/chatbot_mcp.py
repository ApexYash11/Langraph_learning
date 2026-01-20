from langgraph.graph import StateGraph, START
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import TypedDict, Annotated, Any, cast
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
import os

load_dotenv()

llm = ChatGoogleGenerativeAI(
	model="gemini-2.5-flash",
	api_key=os.getenv("GOOGLE_API_KEY"),
)

# Configure MCP client to use only the expense service (env var overrides default)
expense_url = os.getenv("MCP_EXPENSE_URL", "https://required-tomato-monkey.fastmcp.app/mcp")
client_config = {
	"expense": {
		"transport": "streamable_http",
		"url": expense_url,
	}
}

client = MultiServerMCPClient(cast(Any, client_config))


class ChatState(TypedDict):
	messages: Annotated[list[BaseMessage], add_messages]


async def build_graph():
	try:
		tools = await client.get_tools()
	except Exception as e:
		# Print detailed info for nested ExceptionGroup/httpx errors
		print("Failed to load MCP tools:", repr(e))
		try:
			# Python 3.11 ExceptionGroup has .exceptions
			for sub in getattr(e, "exceptions", []):
				try:
					print("Sub-exception:", type(sub), repr(sub))
					resp = getattr(sub, "response", None)
					if resp is not None:
						try:
							text = resp.text
						except Exception:
							text = "<could not read response text>"
						print("Response status:", getattr(resp, "status_code", None))
						print("Response text (first 1000 chars):", (text[:1000] if isinstance(text, str) else str(text)))
				except Exception:
					pass
		except Exception:
			pass
		print("Falling back to local tools only.")
		tools = []

	# Normalize tools into dicts expected by the Google GenAI adapter
	normalized_tools = []
	for t in tools:
		try:
			if isinstance(t, dict):
				normalized_tools.append(t)
				continue
			name = getattr(t, "name", None) or getattr(t, "tool_name", None)
			desc = getattr(t, "description", None)
			args_schema = getattr(t, "args_schema", None) or getattr(t, "parameters", None)
			if name and args_schema is not None:
				params = dict(args_schema) if isinstance(args_schema, dict) else {}
				props = params.get("properties")
				if isinstance(props, dict):
					new_props = {}
					for pk, pv in props.items():
						if isinstance(pv, dict):
							pv = dict(pv)
							pv.setdefault("type", "string")
						new_props[pk] = pv
					params["properties"] = new_props

				normalized_tools.append({
					"name": name,
					"description": desc or "",
					"parameters": params,
				})
			else:
				normalized_tools.append(t)
		except Exception:
			normalized_tools.append(t)

	llm_with_tools = llm.bind_tools(normalized_tools)

	async def chat_node(state: ChatState):
		messages = state["messages"]
		response = await llm_with_tools.ainvoke(messages)
		return {"messages": [response]}

	# ToolNode expects the original tool objects (StructuredTool instances)
	tool_node = ToolNode(tools)

	graph = StateGraph(ChatState)
	graph.add_node("chat_node", chat_node)
	graph.add_node("tools", tool_node)
	graph.add_edge(START, "chat_node")
	graph.add_conditional_edges("chat_node", tools_condition)
	graph.add_edge("tools", "chat_node")

	return graph.compile()


async def main():
	chatbot = await build_graph()
	result = await chatbot.ainvoke({
		"messages": [HumanMessage(content="Give me all my expenses for the month of Nov from 1 Nov to 30 Nov")]
	})
	print(result["messages"][-1].content)


if __name__ == "__main__":
	asyncio.run(main())

