from fastapi import APIRouter, Body, HTTPException,Request
from services.gemini_competitor import SearchRequest,perform_agent_graph_search
from utils.logging_engine import setup_logger


router = APIRouter()
@router.post("/gemini/competitor", tags=["LLM"], summary="Deep search agent")
async def search_web(request: Request,payload: SearchRequest = Body(...)):
    try:
        loggin_obj =setup_logger('llm_main',request.state.logging_path)
        result = await perform_agent_graph_search(payload.query,loggin_obj)
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
