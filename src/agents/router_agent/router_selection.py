from langgraph.graph import StateGraph,START,END
from typing import TypedDict,Literal,Annotated,List, Any
from langchain_core.messages import HumanMessage,SystemMessage
from pathlib import Path
import sys

src_path = Path.cwd().parent.parent / 'src'
print(src_path,'11111111111111111')
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

prompt_path = Path.cwd().parent.parent / 'src' 
if str(prompt_path) not in sys.path:
    sys.path.insert(0, str(prompt_path))

from llm.lite_llm_client import create_chat_model
from prompt_engineering.prompt_template import router_agent_system_prompt,router_agent_human_prompt

class AgentSelection(TypedDict):
    agent_flow:Literal["llm_chat_bot","get_relevent_query"] 

def router(state):
    try:
        query = state["query"]
        system = SystemMessage(content=router_agent_system_prompt)
        human = HumanMessage(content=router_agent_human_prompt.format(query=query))
        llm =create_chat_model('azure','gpt-4o')['model']
        structured_llm = llm.with_structured_output(AgentSelection)
        response = structured_llm.invoke([system, human])
        state["router"] = response["agent_flow"]
        print(f"state[router] : {state['router']}")
        return state
    except Exception as e:
        print(e)
        return state