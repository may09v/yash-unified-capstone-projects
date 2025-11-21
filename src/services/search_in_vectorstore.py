
from utils.milvus_vectorstore import search_in_vector_store

from fastapi import HTTPException

async def perform_search(query_text: str):
    try:
        status = await search_in_vector_store(query_text)
        if not status:
            raise HTTPException(status_code=404, detail="No relevant documents found in vector store.")
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching documents: {e}")
