
from pydantic import BaseModel

from graph.workflow import AgentGraph

from pathlib import Path
import yaml

CONFIG_PATH = Path(__file__).parent.parent.parent  / 'config' / 'central_api_config.yaml'

def load_central_api_config():
    with CONFIG_PATH.open('r') as f:
        return yaml.safe_load(f)

central_api_config = load_central_api_config()

API_TOKEN = central_api_config['API_TOKEN']
agent_graph = AgentGraph()
compiled = agent_graph.compile()

class SearchRequest(BaseModel):
    query: str

async def perform_agent_graph_search(query: str,logging_obj):
    try:
        logging_obj.info('Gemini started')
        output = compiled.invoke({'query': query,'API_TOKEN':API_TOKEN})
        logging_obj.info(f'output came')
        return output
    except Exception as e:
        logging_obj.error(f"Agent graph invocation failed: {str(e)}")
        raise RuntimeError(f"Agent graph invocation failed: {str(e)}")
