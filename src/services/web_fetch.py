
from typing import Any,List
from pydantic import BaseModel


from utils.duckduckgo_search import DuckDuckGo

class SearchRequest(BaseModel):
    url: List[str]
    query: str

async def fetch_web_data(urls: List[str], query: str,logging_obj) -> Any:
    duck_obj = DuckDuckGo()
    try:
        logging_obj.info('Fetch web data stated')
        results = await duck_obj.fetch_web_data(urls, query)
        logging_obj.info(f'Fetch web data END')
        return results
    except Exception as e:
        logging_obj.error(f'failed to Fetch web data {str(e)} ')
        raise RuntimeError(f"Failed to Fetch web data {str(e)}")
    

