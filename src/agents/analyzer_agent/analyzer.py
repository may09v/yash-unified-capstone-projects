import requests
from pathlib import Path
import yaml

CONFIG_PATH = Path(__file__).parent.parent.parent.parent  / 'config' / 'all_urls.yaml'

def load_all_urls_config():
    with CONFIG_PATH.open('r') as f:
        return yaml.safe_load(f)

url_config = load_all_urls_config()
analysis_output_url =url_config['analysis_output_url']


def analyze_generated_output(state):
    try:
        query = state['query']
        rag_data = str(state['relevent_query_rag_data'])
        web_data = str(state["data_for_summarize"])

        # search_results= state['all_search_summarize_data']
        res=requests.post(analysis_output_url,json={'query':query,"url_with_summary": rag_data+web_data,"with_summary":False })
        if res.status_code ==200:
            state['analyser_output']= res.json()
            state["analyser_status"] =True
            return state
        else:
            state["analyser_status"] =False
        return state
    except Exception as e:
        return state
    
    


