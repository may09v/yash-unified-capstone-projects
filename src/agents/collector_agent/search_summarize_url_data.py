import requests
from pathlib import Path
import yaml


CONFIG_PATH = Path(__file__).parent.parent.parent.parent  / 'config' / 'all_urls.yaml'
# CONFIG_PATH =  Path.cwd().parent.parent.parent/ 'Deep_Research' / 'config' / 'all_urls.yaml'

def load_all_urls_config():
    with CONFIG_PATH.open('r') as f:
        return yaml.safe_load(f)

url_config = load_all_urls_config()
search_duckduck_go_url =url_config['search_duckduck_go_url']


def search_over_intenet_with_ddg(state):
    try:
        query = state['relevent_query']
        res=requests.post(search_duckduck_go_url,json={'queries':query})
        if res.status_code ==200:
            state['search_summarize_data']= res.json()
            out = [i['link'] for i in state['search_summarize_data']]
            state['web_urls']=out
            # out = [i['link'] for i in state['search_over_duckduckgo']]
            # state['web_urls']=out
            state["search_summarize_state"] =True
            # return {'web_urls':out}
        else:
            state["search_summarize_state"] =False
        return state
    except Exception as e:
        return state


