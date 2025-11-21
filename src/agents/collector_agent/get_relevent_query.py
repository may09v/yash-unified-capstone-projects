import requests
from pathlib import Path
import yaml

CONFIG_PATH = Path(__file__).parent.parent.parent.parent  / 'config' / 'all_urls.yaml'


def load_all_urls_config():
    with CONFIG_PATH.open('r') as f:
        return yaml.safe_load(f)

url_config = load_all_urls_config()
get_get_relevent_query_url =url_config['get_relevent_query_url']

def get_relevent_query(state):
    query=state['query']
    res=requests.post(get_get_relevent_query_url,json={'query':query})
    if res.status_code ==200:
        state['relevent_query']= res.json()['generated_queries']
        state["relevent_query_operation_status"] =True
        state['all_relevant_query']  = res.json()['generated_queries']
        return state
    else:
        state["relevent_query_operation_status"] =False
    return state
