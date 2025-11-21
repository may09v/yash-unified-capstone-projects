from langchain_core.messages import HumanMessage,SystemMessage
from pathlib import Path
import sys

src_path = Path.cwd().parent 
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

prompt_path = Path.cwd().parent
if str(prompt_path) not in sys.path:
    sys.path.insert(0, str(prompt_path))

from prompt_engineering.prompt_template import general_purpose_system_prompt, general_purpose_human_prompt
from llm.lite_llm_client import create_chat_model

def llm_chat_bot(state):
    try:
        user_query= state['query']
        system_msg = SystemMessage(content=general_purpose_system_prompt)
        human_msg = HumanMessage(content=general_purpose_human_prompt.format(user_query=user_query, chat_history=''))
        connection_status = create_chat_model()

        if not connection_status.get('status'):
            state['output'] = "Unable to perfrom operation" +  + str(connection_status.text)
        llm =connection_status['model']
        response = llm.invoke([system_msg, human_msg]).content
        state['output']= response
        return state
    except Exception as e:
        state['output'] = "Unable to perfrom operation" + str(e)
        return state
    
