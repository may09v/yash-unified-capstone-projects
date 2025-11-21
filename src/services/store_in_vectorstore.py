from fastapi import  HTTPException


from utils.milvus_vectorstore import store_in_vector_store



async def perform_store(input_text: str):
    if not isinstance(input_text, str) or not input_text.strip():
        raise HTTPException(status_code=400, detail="Input text must be a non-empty string.")
    try:
        status = await store_in_vector_store(input_text)
        if not status:
            raise HTTPException(status_code=500, detail="Failed to store documents in vector store.")
        return status
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error during document storage.")
