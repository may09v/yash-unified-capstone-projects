from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel
from datetime import datetime
from pathlib import Path
import sys
import asyncio
# Add src/utils and src/prompt_engineering to sys.path for imports
utils_path = Path.cwd().parent / "src" / "utils"
if str(utils_path) not in sys.path:
    sys.path.insert(0, str(utils_path))

from duckduckgo_search import DuckDuckGo

router = APIRouter()


class SearchRequest(BaseModel):
    query: str
 
@router.post("/search/duckduckgo/single")
async def search_single(request: SearchRequest):
    try:
        duck = DuckDuckGo()
        result = await duck.get_all_data_about(request.query)
        return result
    except Exception as e:
        raise HTTPException(500, f"Search failed: {e}")
    
class MultiSearchRequest(BaseModel):
    queries: list[str]
 