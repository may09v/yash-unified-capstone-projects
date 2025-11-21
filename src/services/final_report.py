
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel

from typing import Any

from prompt_engineering.prompt_template import final_news_report_prompt,final_news_report_system_prompt
from llm.lite_llm_client import create_chat_model




class SummarizationNewsRequest(BaseModel):
    query: str
    search_results: Any

async def perform_summarization(query: str, search_results: Any,loggin_obj: Any) -> str:
    try:
        connection_status = create_chat_model()
        if not connection_status.get('status'):
            raise RuntimeError("Unable to connect to LLM model")
        loggin_obj.info('connected to llm ')
        llm = connection_status['model']
        system_msg = SystemMessage(content=final_news_report_system_prompt)
        human_msg = HumanMessage(content=final_news_report_prompt.format(user_query=query, search_results=search_results))
        summarized_content = llm.invoke([system_msg, human_msg])
        loggin_obj.info(f'llm output generated')
        return summarized_content.content
    except Exception as e:
        loggin_obj.info(f'failed to generate response {str(e)}')
        return 'failed to generate response'
        
