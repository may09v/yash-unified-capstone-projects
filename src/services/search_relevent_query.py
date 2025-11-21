
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel
from typing import List,Optional,Any
from datetime import datetime


from prompt_engineering.prompt_template import generate_search_queries_prompt,generate_search_queries_system_prompt,generate_alternative_search_queries_system_prompt,generate_alternative_search_queries_prompt
from llm.lite_llm_client import create_chat_model

class SearchQueryBody(BaseModel):
    query: str
    max_query_generation: int = 3
    previous_query_generated: Optional[List[str]] = None

async def generate_queries_logic(user_query: str,logger_obj: Any, max_gen: int, previous_queries: Optional[List[str]]):
    current_date = datetime.today().strftime("%d %B %Y")
    connection_status = create_chat_model()
    logger_obj.info('Start operation')

    if not connection_status.get('status'):
        raise RuntimeError("Unable to connect to LLM model")

    llm = connection_status['model']

    if not previous_queries:
        system_msg = SystemMessage(content=generate_search_queries_system_prompt)
        human_msg = HumanMessage(content=generate_search_queries_prompt.format(
            user_query=user_query,
            current_date=current_date,
            MAX_QUERY_GENERATIONS=max_gen,
        ))
    else:
        system_msg = SystemMessage(content=generate_alternative_search_queries_system_prompt)
        human_msg = HumanMessage(content=generate_alternative_search_queries_prompt.format(
            user_query=user_query,
            previous_queries="\n".join(previous_queries),
            MAX_QUERY_GENERATIONS=max_gen
        ))

    response = llm.invoke([system_msg, human_msg])
    refined_queries = [
        q.strip().strip("'\"").strip("-").strip()
        for q in response.content.split("\n")
        if q and q.lower() != "none"
    ]
    logger_obj.warning('end')
    return refined_queries[:max_gen]
