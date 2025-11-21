
from pydantic import BaseModel

from graph.workflow import AgentGraph

agent_graph = AgentGraph()
compiled = agent_graph.compile()

class SearchRequest(BaseModel):
    query: str

async def perform_agent_graph_search(query: str,logging_obj):
    try:
        logging_obj.info('Operation started')
        output = compiled.invoke({'query': query})
        logging_obj.info(f'output came')
        return output
    except Exception as e:
        logging_obj.error(f"Agent graph invocation failed: {str(e)}")
        raise RuntimeError(f"Agent graph invocation failed: {str(e)}")
