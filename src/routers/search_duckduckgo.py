from fastapi import APIRouter, Body, HTTPException,Request
from pydantic import BaseModel
from utils.logging_engine import setup_logger
import asyncio


from utils.duckduckgo_search import DuckDuckGo

router = APIRouter()

    
class MultiSearchRequest(BaseModel):
    queries: list[str]
 
@router.post("/search/web/")
async def search_multi(request: Request,payload: MultiSearchRequest):
    try:
        loggin_obj =setup_logger('llm_main',request.state.logging_path)
        loggin_obj.info('/search/web/ API started')
        duck = DuckDuckGo()
        tasks = [duck.search_duckduckgo(q) for q in payload.queries]
        results = await asyncio.gather(*tasks)
        flat_list = [item for sublist in results for item in sublist]
        loggin_obj.info(f'/search/web/ wokrded well ')
        return flat_list
    except Exception as e:
        loggin_obj.error(f"Parallel search failed: {str(e)}")
        raise HTTPException(500, f"Parallel search failed: {str(e)}")