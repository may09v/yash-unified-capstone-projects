from fastapi import APIRouter, Body, HTTPException
from services.store_in_vectorstore import perform_store

router = APIRouter()

@router.post("/store_in_vectorstore", tags=["Store"], summary="Store in vector db", description="Store important data in milvus vector database")
async def store_documents_in_vectorstore(input: dict = Body(..., description="Input text to store in vector store")):
    if 'input' not in input:
        raise HTTPException(status_code=400, detail="Missing 'input' in request body.")
    result = await perform_store(input['input'])
    return {"status": "Documents stored successfully in vector store."}
