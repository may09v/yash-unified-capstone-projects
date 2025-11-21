from fastapi import APIRouter, Body, HTTPException
from services.analysis import perform_analysis,AnlysisContentBody

router = APIRouter()

@router.post("/analysis/", tags=["Analysis"], summary="Analysis data with query")
async def analysis_content(payload: AnlysisContentBody = Body(...)):
    try:
        result = await perform_analysis(payload.query, payload.url_with_summary, payload.with_summarize)
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during analysis: {e}")
