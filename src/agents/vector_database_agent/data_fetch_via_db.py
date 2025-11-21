
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from pathlib import Path
import yaml

CONFIG_PATH = Path(__file__).parent.parent.parent.parent  / 'config' / 'all_urls.yaml'

def load_all_urls_config():
    with CONFIG_PATH.open('r') as f:
        return yaml.safe_load(f)

url_config = load_all_urls_config()
db_data_fetch_url =url_config['search_vector_db_url']


def call_api(query):
    try:
        response = requests.post(db_data_fetch_url, json={'query':query})
        return response.json()
    except Exception as e:
        return ''

def db_data_fetch(state):
    sub_queries=list(state['query'])
    sub_queries.extend(state['relevent_query'])
    all_queires = "  ".join(sub_queries)
    content = call_api(all_queires)
    state['relevent_query_rag_data'] = content['data']
    if state['relevent_query_rag_data'] == '':
        state["relevent_query_rag_data_status"] =False
    else: 
        state["relevent_query_rag_data_status"] =True
    return state
