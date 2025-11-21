"""FastAPI entry point exposing the corporate travel role-based agent."""

from __future__ import annotations

import asyncio
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

import jwt
from fastapi import (
    BackgroundTasks,
    Depends,
    FastAPI,
    Header,
    HTTPException,
    status,
    UploadFile,
    File,
)
from pydantic import BaseModel, Field

from agent.workflow import RoleBasedTravelAgent
from src.config.settings import settings
from scripts.ingest_policies import ingest_files as ingest_policy_files

app = FastAPI(title="Corporate Travel Agent", version="1.0.0")

UPLOAD_DIR = Path(settings.UPLOAD_STORAGE_DIR).resolve()
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED_UPLOAD_EXTENSIONS = {".md", ".txt", ".pdf"}


class ChatRequest(BaseModel):
    message: str = Field(..., description="Natural language prompt for the travel bot.")


class ChatResponse(BaseModel):
    success: bool
    message: str
    chat_history: Optional[List[Dict[str, Any]]] = None
    session_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    error_details: Optional[str] = None
    suggestions: Optional[List[str]] = None


class IdentityPayload(BaseModel):
    user_id: str
    role: str
    name: str
    email: str


class UploadResponse(BaseModel):
    success: bool
    message: str
    stored_files: List[str]
    upload_dir: str
    rejected_files: Optional[List[str]] = None
    ingestion_triggered: bool = False


def _extract_token(authorization: str) -> str:
    scheme, _, token = authorization.partition(" ")
    if token:
        return token
    return scheme  # When token provided without Bearer prefix


def get_identity(authorization: str = Header(..., alias="Authorization")) -> IdentityPayload:
    """Decode the inbound JWT and expose the identity to route handlers."""

    token = _extract_token(authorization)
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except jwt.PyJWTError as exc:  # pragma: no cover - external dependency
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    missing = [field for field in ("user_id", "role", "name", "email") if field not in payload]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token missing required claims: {', '.join(missing)}",
        )

    return IdentityPayload(
        user_id=payload["user_id"],
        role=payload["role"],
        name=payload["name"],
        email=payload["email"],
    )


def _ingest_uploaded_files(file_paths: List[str]) -> None:
    """Background task to ingest uploaded files into Milvus."""

    if not file_paths:
        return

    for path in file_paths:
        try:
            print(f"📥 Ingesting file: {path}")
            ingest_policy_files([path])
            print(f"✅ Background ingestion complete for file: {path}")
        except Exception as exc:
            print(f"❌ Background ingestion failed for {path}: {exc}")


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, identity: IdentityPayload = Depends(get_identity)) -> ChatResponse:
    """Process user messages using role-based travel agent with session memory."""

    try:
        # Use employee_id as session_id for consistent session management
        session_id = identity.user_id
        
        # Initialize role-based agent with session support
        agent = RoleBasedTravelAgent(
            user_role=identity.role,
            session_id=session_id,
            employee_id=identity.user_id,
            employee_name=identity.name,
            employee_info={
                "email": identity.email,
            }
        )
        
        # Process message through the agent (returns dict with history)
        result = await agent.process_message(request.message)
        
        return ChatResponse(
            success=True,
            message=result.get("response", ""),
            chat_history=result.get("chat_history", []),
            session_id=session_id,
            data={
                "role": identity.role,
                "employee_id": identity.user_id,
                "available_tools": agent.get_available_tools(),
                "tool_count": len(agent.get_available_tools()),
                "message_count": len(result.get("chat_history", [])),
                "tool_calls": result.get("tool_calls"),
                "tool_results": result.get("tool_results"),
            }
        )
    except ValueError as e:
        # Invalid role
        return ChatResponse(
            success=False,
            message="Invalid user role configuration.",
            error="invalid_role",
            error_details=str(e)
        )
    except Exception as e:
        return ChatResponse(
            success=False,
            message="An error occurred while processing your request.",
            error="processing_error",
            error_details=str(e),
            suggestions=[
                "Check your message format",
                "Verify you have permission for the requested action",
                "Try again with a simpler request"
            ]
        )


@app.get("/health", summary="Health check")
async def healthcheck() -> Dict[str, str]:
    return {"status": "ok"}



@app.post("/documents/upload", response_model=UploadResponse, summary="Upload policy/reference files")
async def upload_documents(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(..., description="One or more markdown/text/PDF files"),
    trigger_ingestion: bool = True,
    identity: IdentityPayload = Depends(get_identity),
) -> UploadResponse:
    """Accept one or more files and store them for later ingestion."""

    if identity.role != "travel_desk":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only travel desk users can upload policy documents.",
        )

    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one file is required",
        )

    stored_files: List[str] = []
    stored_paths: List[Path] = []
    rejected_files: List[str] = []

    for upload in files:
        original_name = (upload.filename or "unnamed").strip()
        sanitized_name = Path(original_name).name
        extension = Path(sanitized_name).suffix.lower()

        if ALLOWED_UPLOAD_EXTENSIONS and extension not in ALLOWED_UPLOAD_EXTENSIONS:
            rejected_files.append(f"{sanitized_name} (unsupported extension)")
            continue

        content = await upload.read()
        if not content:
            rejected_files.append(f"{sanitized_name} (empty file)")
            continue

        destination = UPLOAD_DIR / f"{uuid.uuid4().hex}_{sanitized_name}"
        destination.write_bytes(content)
        stored_files.append(destination.name)
    stored_paths.append(destination)

    if not stored_files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files were stored successfully. Please check file format/contents.",
        )

    ingestion_triggered = False
    if trigger_ingestion and stored_paths:
        ingestion_triggered = True
        background_tasks.add_task(
            _ingest_uploaded_files,
            [str(path) for path in stored_paths],
        )

    return UploadResponse(
        success=True,
        message=f"Stored {len(stored_files)} file(s) for user {identity.user_id}",
        stored_files=stored_files,
        upload_dir=str(UPLOAD_DIR),
        rejected_files=rejected_files or None,
        ingestion_triggered=ingestion_triggered,
    )


@app.get("/sessions/{session_id}/history", summary="Get chat history for a session")
async def get_session_history(session_id: str, identity: IdentityPayload = Depends(get_identity)) -> Dict[str, Any]:
    """Get full chat history for a session (only accessible by session owner)."""
    
    # Security: Only allow users to access their own sessions
    if session_id != identity.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this session."
        )
    
    try:
        agent = RoleBasedTravelAgent(
            user_role=identity.role,
            session_id=session_id,
            employee_id=identity.user_id,
            employee_name=identity.name,
        )
        
        history = agent.get_session_history()
        session_info = agent.get_session_info()
        
        return {
            "success": True,
            "session_id": session_id,
            "session_info": session_info,
            "chat_history": history,
            "message_count": len(history),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.delete("/sessions/{session_id}", summary="Clear session history")
async def clear_session(session_id: str, identity: IdentityPayload = Depends(get_identity)) -> Dict[str, Any]:
    """Clear chat history for a session (only accessible by session owner)."""
    
    # Security: Only allow users to clear their own sessions
    if session_id != identity.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this session."
        )
    
    try:
        agent = RoleBasedTravelAgent(
            user_role=identity.role,
            session_id=session_id,
            employee_id=identity.user_id,
            employee_name=identity.name,
        )
        
        agent.clear_session()
        
        return {
            "success": True,
            "message": f"Session {session_id} cleared successfully.",
            "session_id": session_id,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
