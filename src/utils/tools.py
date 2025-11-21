from langchain_core.messages import HumanMessage,SystemMessage
from pathlib import Path
import sys,requests, yaml
from typing import Set, List, Dict, Any

CONFIG_PATH = Path(__file__).parent.parent.parent  / 'config' / 'all_urls.yaml'
AZURE_CONFIG_PATH = Path(__file__).parent.parent.parent  / 'config' / 'azure_config.yaml'

def load_all_urls_config():
    with CONFIG_PATH.open('r') as f:
        return yaml.safe_load(f)
    
def load_azure_config():
    with AZURE_CONFIG_PATH.open('r') as f:
        return yaml.safe_load(f)

url_config = load_all_urls_config()
azure_config = load_azure_config()

def format_chat_history(messages) -> str:
    """Format chat history into a string."""
    if not messages:
        return ""

    formatted_history = []
    for msg in messages:
        role = "User" if msg['role'] == "user" else "Assistant"
        formatted_history.append(f"{role}: {msg['message']}")
    return "\n".join(formatted_history)

def chat_store_api_call(messages: List[Dict[str, Any]], session_id: str) -> bool:
    """Store chat messages by posting to the API."""
    token = azure_config['TOKEN']
    add_message_url = url_config['add_message_url']
    headers = {"Authorization": f"Bearer {token}"}
    url = add_message_url.format(session=session_id)  # format once outside loop

    for data_dict in messages:
        try:
            response = requests.post(url, params=data_dict, headers=headers)
            response.raise_for_status()  # raise exception for HTTP errors
        except Exception as e:
            print(f"ERROR: Could not store chat message: {e}")
            return False
    return True

def collect_format_chat_history(session_id: str) -> str:
    """Store chat messages by posting to the API."""
    try:
        token = azure_config['TOKEN']
        get_chat_history_url = url_config['get_chat_history_url']
        headers = {"Authorization": f"Bearer {token}"}
        url = get_chat_history_url.format(session=session_id)  # format once outside loop
        chat_history_data = requests.get(url, headers=headers)
        messages = chat_history_data.json()['messages'] if chat_history_data else []
        format_chat_data = format_chat_history(messages)
        return format_chat_data
    except Exception as e:
        print("ERROR : Unable to Collect format chat history")
        return ""
