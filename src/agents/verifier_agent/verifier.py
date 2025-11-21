

import requests
from pathlib import Path
import yaml

CONFIG_PATH = Path(__file__).parent.parent.parent.parent  / 'config' / 'all_urls.yaml'

def load_all_urls_config():
    with CONFIG_PATH.open('r') as f:
        return yaml.safe_load(f)

url_config = load_all_urls_config()
verifier_output_url =url_config['verifier_output_url']


def content_verifier(state):
    try:
        query = state['query']
        # search_results= state['data_for_summarize']
        search_data_list = state['all_search_summarize_data']
        res=requests.post(verifier_output_url,json={'query':query,"url_with_summary": search_data_list})
        if res.status_code ==200:
            state['verifier_output_data']= res.json()
            state['all_verify_output']= res.json()
            state["verifier_output_status"] =True
            return state
        else:
            state["verifier_output_status"] =False
        return state
    except Exception as e:
        return state


