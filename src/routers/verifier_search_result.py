from pydantic import BaseModel, Field
from typing import List, Dict, Optional

from fastapi import APIRouter, Body, HTTPException
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel
from typing import List,Optional, Any
from datetime import datetime
from pathlib import Path
import requests
import sys
import yaml

url_path = Path(__file__).parent.parent.parent  / 'config' / 'all_urls.yaml'

def load_all_urls_config():
    with url_path.open('r') as f:
        return yaml.safe_load(f)

url_config = load_all_urls_config()
summarize_output_url =url_config['summarize_output_url']


from prompt_engineering.prompt_template import verifier_result_content_prompt,verifier_report_system_prompt
from llm.lite_llm_client import create_chat_model
# from prompt_template import final_news_report_prompt,final_news_report_system_prompt
# from lite_llm_client import create_chat_model


router = APIRouter()


# class AnalysisModel(BaseModel):
#    competitors: List[CompetitorInfo] = Field(
#        default_factory=list,
#        description="Detailed competitor-level insights extracted strictly from evidence."
#    )
#    products: List[ProductInfo] = Field(
#        default_factory=list,
#        description="Detailed product-level insights extracted from evidence."
#    )
#    pricing: Dict[str, List[str]] = Field(
#        default_factory=dict,
#        description="Grouped pricing insights for each competitor or product."
#    )
#    features: Dict[str, List[str]] = Field(
#        default_factory=dict,
#        description="Grouped feature insights for each competitor or product."
#    )
#    strengths: Dict[str, List[str]] = Field(
#        default_factory=dict,
#        description="General strengths grouped per entity, strictly based on evidence."
#    )
#    weaknesses: Dict[str, List[str]] = Field(
#        default_factory=dict,
#        description="General weaknesses grouped per entity based on evidence."
#    )
#    opportunities: Dict[str, List[str]] = Field(
#        default_factory=dict,
#        description="Opportunities mentioned in the research documents."
#    )
#    threats: Dict[str, List[str]] = Field(
#        default_factory=dict,
#        description="Threats mentioned in the research documents."
#    )
#    market_moves: List[str] = Field(
#        default_factory=list,
#        description="Any important market moves or strategic actions taken, based strictly on evidence."
#    )
#    risks: List[str] = Field(
#        default_factory=list,
#        description="Risks identified from the verified research documents."
#    )
#    differentiators: List[str] = Field(
#        default_factory=list,
#        description="Unique differentiators found in the research."
#    )
#    summary: str = Field(
#        "",
#        description="A concise 500 sentence summary directly answering the main query."
#    )
#    best_url: Optional[str] = Field(
#        None,
#        description="The 5 most best relevant source URL supporting the summary."
#    )
#    class Config:
#        extra = "forbid"


class VerifierContentBody(BaseModel):
    query: str
    url_with_summary: List[Dict] = []
    with_summarize: bool = True


@router.post("/verifier/", tags=["Verifier"], summary="VerifY data with query")
async def verify_content(payload: VerifierContentBody = Body(...)):
    try:
        user_query = payload.query
        url_with_summary = payload.url_with_summary
        #TODO : API call for Rag data similar match
        # rag_data = payload.rag_data
        # with_summarize=payload.with_summarize
                
        verifier_prompt=verifier_result_content_prompt.format(
                main_query=user_query,
                documents_with_urls=str(url_with_summary)
            )
        connection_status = create_chat_model()

        if not connection_status.get('status'):
            raise HTTPException(status_code=503, detail="Unable to connect to LLM model")

        llm = connection_status['model']
        system_msg = SystemMessage(content=verifier_report_system_prompt)
        human_msg = HumanMessage(content=verifier_prompt)
        summarized_content=llm.invoke([system_msg, human_msg])
        return summarized_content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error to fetch relevant query: {e}")

   
