from typing import TypedDict,Literal,Annotated,List, Any, Optional, Dict
from langchain_core.messages import BaseMessage
import operator
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: List[BaseMessage]
    query:str
    router: Literal["llm_chat_bot","get_relevent_query"] 

    #create new session for user
    new_session: Literal[True,False]

    # for relevent query 
    relevent_query: Optional[List[str]]
    relevent_query_operation_status: Literal[True,False] =False

    # for search and summarizing in duckduckgo
    search_summarize_data: Optional[Any]
    search_summarize_state: Literal[True,False] =False

    # for verifier
    verifier_output_data: Optional[Any]
    verifier_output_status: Literal[True,False] =False

    #rag_collected_data
    relevent_query_rag_data: Any
    relevent_query_rag_data_status : Literal[True,False] =False
    store_data_in_vcdb : Any
    store_data_in_vcdb_status: Literal[True,False] =False

    refined_query_rag_data: str


    # all_data
    all_relevant_query: Optional[List[str]]
    all_search_summarize_data: Optional[List[Dict]]
    all_verify_output: Optional[Any]

    # refinement verifier
    refine_verifier_output_data: Optional[Any]

    # refinement count (max = 1)
    refinement_count: int

    # for analyser
    analyser_output: Optional[Any]
    analyser_status: Literal[True,False] =False 

    # Final Report output
    summarized_output: Any
    summarize_output_status:Literal[True,False] =False
    output: Optional[str] = 'Failed to fetch response'

    # refinement url & summarize data
    data_for_summarize : Optional[Any]
    web_urls:List[str]= []
    web_data_fetch_status: Literal[True,False] =False 