
from typing import Any,List
from pydantic import BaseModel


from utils.duckduckgo_search import DuckDuckGo

class SearchRequest(BaseModel):
    url: List[str]
    query: str

async def fetch_web_data(urls: List[str], query: str,logging_obj) -> Any:
    duck_obj = DuckDuckGo()
    try:
        logging_obj.info('stated fetch web data')
        results = await duck_obj.fetch_web_data(urls, query)
        logging_obj.info(f'successful fetch web data  ')
        return results
    except Exception as e:
        logging_obj.error(f'ouptut of  fetch web data {str(e)} ')
        raise RuntimeError(f"Failed to fetch web data: {str(e)}")
    

