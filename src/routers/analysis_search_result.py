from fastapi import APIRouter, Body, HTTPException, Request
from services.analysis import perform_analysis,AnlysisContentBody
from utils.logging_engine import setup_logger

router = APIRouter()

@router.post("/analysis/", tags=["Analysis"], summary="Analysis data with query")
async def analysis_content(request: Request,payload: AnlysisContentBody = Body(...)):
    try:
        logging_obj =setup_logger('llm_main',request.state.logging_path)
        logging_obj.info('Analysis started')
        result = await perform_analysis(payload.query, payload.url_with_summary, payload.with_summarize)
        logging_obj.info('Analysis END')
        return result
    except RuntimeError as e:
        logging_obj.error(f'error with analysis report API {str(e)}')
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logging_obj.error(f'error with analysis report API {str(e)}')
        raise HTTPException(status_code=500, detail=f"Error during analysis: {e}")
