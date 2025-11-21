from fastapi import APIRouter, Body, HTTPException,Request
from services.final_report import SummarizationNewsRequest,perform_summarization
from utils.logging_engine import setup_logger

router = APIRouter()
@router.post("/final-report", tags=["summarization"], summary="Summarize text news content")
async def news_summarize(request: Request,payload: SummarizationNewsRequest = Body(...)) -> dict:
    try:
        loggin_obj =setup_logger('llm_main',request.state.logging_path)
        summary = await perform_summarization(payload.query, payload.search_results,loggin_obj)
        return {"summary": summary}
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {e}")
