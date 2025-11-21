from fastapi import APIRouter, Body, HTTPException,Request
from services.web_fetch import SearchRequest, fetch_web_data
from utils.logging_engine import setup_logger


router = APIRouter()

@router.post("/web/fetch", tags=["search"], summary="Fetch web data through API and summarize")
async def search_web(request: Request,payload: SearchRequest = Body(...)):
    try:
        loggin_obj =setup_logger('llm_main',request.state.logging_path)
        search_results = await fetch_web_data(payload.url, payload.query,loggin_obj)
        return search_results
    except RuntimeError as e:
        loggin_obj.error('issue have with web detch')
        raise HTTPException(status_code=500, detail=str(e))
