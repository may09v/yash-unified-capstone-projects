
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from pathlib import Path
import yaml

CONFIG_PATH = Path(__file__).parent.parent.parent  / 'config' / 'all_urls.yaml'

def load_all_urls_config():
    with CONFIG_PATH.open('r') as f:
        return yaml.safe_load(f)

url_config = load_all_urls_config()
web_data_fetch_url =url_config['web_data_fetch_url']


def call_api(url, query):
    try:
        response = requests.post(web_data_fetch_url, json={'query':query,"url":url})
        return response.json()
    except Exception as e:
        return {}


# def perform_multithreaded_api_calls(api_calls,query):
#     results = []
#     with ThreadPoolExecutor(max_workers=5) as executor:
#         futures = [executor.submit(call_api, url,query) for url in api_calls]
#         for future in as_completed(futures):
#             try:
#                 result = future.result()
#                 results.append(result)
#             except Exception as e:
#                 results.append({"error": str(e)})
#     return results


def web_data_fetch(state):
    query=state['query']
    web_urls=state['web_urls']
    # res=requests.post(web_data_fetch_url,json={'query':query})
    # if res.status_code ==200:
    state['data_for_summarize']= call_api(web_urls,query)
    state["web_data_fetch_status"] =True
    return state