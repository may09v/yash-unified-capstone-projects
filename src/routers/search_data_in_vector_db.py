


from fastapi import APIRouter, Body, HTTPException
from services.search_in_vectorstore import perform_search

router = APIRouter()
@router.post("/search_in_vectorstore", tags=["search"], summary="Search in vector db", description="Search data in milvus vector database")
async def search_endpoint(query: dict = Body(..., description="search data in vector store")):
    if 'query' not in query or not query['query']:
        raise HTTPException(status_code=400, detail="Query parameter is required.")
    result = await perform_search(query['query'])
    return {"data": result}
