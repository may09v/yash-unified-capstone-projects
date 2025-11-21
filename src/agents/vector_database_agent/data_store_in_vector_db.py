
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from pathlib import Path
import yaml

CONFIG_PATH = Path(__file__).parent.parent.parent.parent  / 'config' / 'all_urls.yaml'

def load_all_urls_config():
    with CONFIG_PATH.open('r') as f:
        return yaml.safe_load(f)

url_config = load_all_urls_config()
store_vector_db_url =url_config['store_vector_db_url']


def call_api(output):
    try:
        response = requests.post(store_vector_db_url, json={'input':output})
        return response.json()
    except Exception as e:
        return ''

def store_data_in_vcdb(state):
    output=state['output']
    content = call_api(output)
    try:
        state['store_data_in_vcdb'] = content['status']
        if  state['store_data_in_vcdb']== '':
            state["store_data_in_vcdb_status"] =False
        else:
            state["store_data_in_vcdb_status"] =True
        return state
    except Exception as e:
        return state
