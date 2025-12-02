import os
import json
import re
import asyncio
from typing import Dict, Any

from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END

from llm_new.state import AgentState
from llm_new.tools import TOOL_MAP

# --- System Prompt ---
# --- System Prompt ---
def get_system_prompt():
    prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "system_prompt.md")
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Error reading system prompt: {e}")
        return "You are a web automation agent. Please help the user."

SYSTEM_PROMPT = get_system_prompt()


# --- Nodes ---

async def planner_node(state: AgentState):
    messages = state['messages']
    
    llm = ChatOpenAI(
        model="MBZUAI-IFM/K2-Think",
        base_url=os.environ.get("K2_LLM_URI"),
        api_key=os.environ.get("K2_LLM_API_KEY"),
        temperature=0.1,
    )
    
    # Ensure system message is first
    full_history = [SystemMessage(content=SYSTEM_PROMPT)] + messages
    
    print("   [PLANNER] Invoking LLM...")
    response = await llm.ainvoke(full_history)
    content = response.content
    # print(content)
    # --- Parsing Logic ---
    try:
        # Remove thinking tags if present
        clean_content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
        start_index = clean_content.find('{')
        if start_index != -1:
            decoder = json.JSONDecoder()
            action_data, _ = decoder.raw_decode(clean_content[start_index:])
        else:
            # If no JSON found, assume it's a finish message or a raw response
            action_data = {"type": "finish", "content": clean_content}
    except Exception as e:
        print(f"   [PLANNER] JSON Parse Error: {e}")
        action_data = {"type": "finish", "content": f"Error parsing response: {content}"}
        
    return {
        "next_action": action_data,
        "messages": [AIMessage(content=content)]
    }


async def executor_node(state: AgentState):
    action = state['next_action']
    tool_name = action.get("name")
    args = action.get("args", {})
    
    print(f"   [EXECUTOR] Running {tool_name}...")
    
    # Run Tool
    if tool_name in TOOL_MAP:
        try:
            # Tools are async
            result = await TOOL_MAP[tool_name].ainvoke(args)
        except Exception as e:
            result = f"Error: {str(e)}"
    else:
        result = "Error: Unknown tool."
    
    # Create AgentResult dict
    # Map tool names to agent types expected by frontend
    agent_type_map = {
        "action_tool": "act",
        "edit_tool": "edit", 
        "clarify_tool": "clarify"
    }
    agent_result = {
        "session_id": args.get("session_id", state.get("session_id", "unknown")),
        "step_id": args.get("step_id", "unknown"),
        "intent": args.get("intent", "unknown"),
        "context": args.get("context", "unknown"),
        "result": result,
        "agent_type": agent_type_map.get(tool_name, tool_name.replace("_tool", "")),
        "execution_time_seconds": 0.0
    }
        
    # Return as HumanMessage to simulate system feedback
    return {
        "messages": [HumanMessage(content=f"TOOL OUTPUT: {result}")],
        "results": [agent_result]
    }

# --- Graph Logic ---

def router(state: AgentState):
    # If type is 'tool', go to executor. If 'finish', end.
    if state['next_action'].get('type') == 'tool':
        return "executor"
    return END

workflow = StateGraph(AgentState)

workflow.add_node("planner", planner_node)
workflow.add_node("executor", executor_node)

workflow.set_entry_point("planner")

workflow.add_conditional_edges(
    "planner",
    router
)

workflow.add_edge("executor", "planner") # Loop back to planner after tool

app = workflow.compile()
