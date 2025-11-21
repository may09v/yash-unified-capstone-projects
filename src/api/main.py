"""FastAPI application for sales transcript analysis."""
import os
import sys
import uuid
from pathlib import Path
from typing import Optional
import traceback

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Cookie, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.api.models import (
    TextAnalysisRequest,
    AnalysisResponse,
    SearchRequest,
    SearchResponse,
    SearchResult,
    HealthResponse,
    InputType,
    SalesHelperRequest,
    SalesHelperResponse,
    ChatRequest,
    ChatResponse
)
from src.agent.transcript_analyzer import TranscriptAnalyzer
from src.agent.vector_store import MilvusVectorStore
from src.agent.sales_helper_agent import SalesHelperAgent
from src.agent.chat_agent import ChatAgent
from src.utils.config_loader import get_config
from src.utils.logger import setup_logger
from src.utils.document_processor import DocumentProcessor
from src.utils.s3_utility import get_s3_file
from src.utils.exception_handler import (
    BaseApplicationError,
    ConfigurationError,
    DatabaseError,
    LLMError,
    DocumentProcessingError,
    ValidationError,
    log_exception
)

# Simple session storage
SESSIONS = {}
USERS = {"admin": "admin123", "demo": "demo123"}
USER_DATA = {
    "admin": {"email": "admin@rasa.com", "full_name": "Administrator", "user_id": "user_admin"},
    "demo": {"email": "demo@rasa.com", "full_name": "Demo User", "user_id": "user_demo"}
}
CHAT_HISTORY = {}  # {username: [{id, title, messages: [{role, content}]}]}

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    email: str
    full_name: str



# Initialize configuration and logger
config = get_config()
logger = setup_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title=config.get('fastapi.title', 'Sales Transcript Analysis API'),
    description=config.get('fastapi.description', 'API for analyzing sales conversations'),
    version=config.get('fastapi.version', '1.0.0')
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler for all unhandled exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler to catch and log all unhandled exceptions.

    Args:
        request: FastAPI request object
        exc: Exception that was raised

    Returns:
        JSON response with error details
    """
    # Log the exception with full context
    log_exception(
        exc,
        context=f"API endpoint: {request.method} {request.url.path}",
        extra_info={
            "client_host": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown")
        }
    )

    # Return appropriate error response
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail, "error_code": "HTTP_ERROR"}
        )
    elif isinstance(exc, BaseApplicationError):
        return JSONResponse(
            status_code=500,
            content=exc.to_dict()
        )
    else:
        # Generic error response for unexpected exceptions
        return JSONResponse(
            status_code=500,
            content={
                "error": "An unexpected error occurred. Please try again later.",
                "error_code": "INTERNAL_ERROR",
                "details": str(exc) if logger.level <= 10 else None  # Show details only in debug mode
            }
        )


# Custom exception handler for BaseApplicationError
@app.exception_handler(BaseApplicationError)
async def application_exception_handler(request: Request, exc: BaseApplicationError):
    """Handler for custom application exceptions.

    Args:
        request: FastAPI request object
        exc: Application exception

    Returns:
        JSON response with error details
    """
    log_exception(
        exc,
        context=f"API endpoint: {request.method} {request.url.path}",
        extra_info={"error_code": exc.error_code}
    )

    return JSONResponse(
        status_code=500,
        content=exc.to_dict()
    )


# Mount static files
app.mount("/static", StaticFiles(directory="src/api/static"), name="static")

# Initialize components
transcript_analyzer = TranscriptAnalyzer()
sales_helper_agent = SalesHelperAgent()

# Store user-specific vector stores and chat agents
USER_VECTOR_STORES = {}
USER_CHAT_AGENTS = {}
MILVUS_ENABLED = False

def get_user_vector_store(user_id: str):
    """Get or create vector store for user."""
    if user_id not in USER_VECTOR_STORES:
        try:
            USER_VECTOR_STORES[user_id] = MilvusVectorStore(user_id=user_id)
            logger.info(f"Created vector store for user: {user_id}")
        except Exception as e:
            logger.error(f"Failed to create vector store for {user_id}: {e}")
            return None
    return USER_VECTOR_STORES[user_id]

def get_user_chat_agent(user_id: str):
    """Get or create chat agent for user."""
    if user_id not in USER_CHAT_AGENTS:
        try:
            USER_CHAT_AGENTS[user_id] = ChatAgent(user_id=user_id)
            logger.info(f"Created chat agent for user: {user_id}")
        except Exception as e:
            logger.error(f"Failed to create chat agent for {user_id}: {e}")
            return None
    return USER_CHAT_AGENTS[user_id]

# Create temp directory for audio uploads
TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(exist_ok=True)


@app.get("/login", response_class=HTMLResponse)
def login_page():
    from pathlib import Path
    login_file = Path("src/api/templates/login.html")
    return HTMLResponse(content=login_file.read_text(encoding="utf-8"))

@app.post("/register")
async def register(request: RegisterRequest):
    if request.username in USERS:
        return JSONResponse({"success": False, "message": "Username already exists"}, status_code=400)
    USERS[request.username] = request.password
    user_id = f"user_{request.username}"
    USER_DATA[request.username] = {"email": request.email, "full_name": request.full_name, "user_id": user_id}
    return {"success": True, "message": "Registration successful"}

@app.post("/login")
async def login(request: LoginRequest, response: Response):
    import secrets
    if request.username in USERS and USERS[request.username] == request.password:
        token = secrets.token_urlsafe(32)
        SESSIONS[token] = request.username
        response.set_cookie(key="session", value=token, httponly=True)
        return {"success": True}
    return JSONResponse({"success": False, "message": "Invalid credentials"}, status_code=401)

@app.post("/logout")
async def logout(response: Response, session: Optional[str] = Cookie(None)):
    if session in SESSIONS:
        del SESSIONS[session]
    response.delete_cookie("session")
    return {"success": True}

@app.get("/", response_class=HTMLResponse)
def root(session: Optional[str] = Cookie(None)):
    """Root endpoint - Web UI for file upload."""
    if not session or session not in SESSIONS:
        return RedirectResponse(url="/login", status_code=302)
    from pathlib import Path
    dashboard_file = Path("src/api/templates/dashboard.html")
    return HTMLResponse(content=dashboard_file.read_text(encoding="utf-8"))


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version=config.get('fastapi.version', '1.0.0'),
        services={
            "api": "running",
            "llm": "configured",
            "milvus": "connected"
        }
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version=config.get('fastapi.version', '1.0.0'),
        services={
            "api": "running",
            "llm": "configured",
            "milvus": "connected"
        }
    )


@app.post("/analyze/text", response_model=AnalysisResponse)
async def analyze_text_transcript(request: TextAnalysisRequest, session: Optional[str] = Cookie(None)):
    """Analyze a text transcript.

    Args:
        request: Text analysis request containing the transcript

    Returns:
        Analysis results including requirements, recommendations, and summary
    """
    try:
        logger.info("Received text transcript analysis request")

        # Validate input
        if not request.transcript or not request.transcript.strip():
            raise ValidationError("Transcript text cannot be empty", details={"transcript_length": len(request.transcript or "")})

        # Generate transcript ID if not provided
        transcript_id = request.transcript_id or str(uuid.uuid4())

        # Analyze transcript
        try:
            analysis_result = transcript_analyzer.analyze_transcript(request.transcript)
        except Exception as e:
            log_exception(e, context="analyze_text_transcript (analysis)", extra_info={"transcript_id": transcript_id})
            raise LLMError(f"Failed to analyze transcript: {str(e)}", details={"transcript_id": transcript_id})

        # Check for errors in analysis
        if "error" in analysis_result:
            logger.warning(f"Analysis returned error: {analysis_result['error']}")
            return AnalysisResponse(
                success=False,
                transcript_id=transcript_id,
                transcript=request.transcript,
                error=analysis_result["error"],
                source_type=InputType.TEXT
            )

        # Store in database if requested
        if request.store_in_db and session and session in SESSIONS:
            username = SESSIONS[session]
            user_id = USER_DATA.get(username, {}).get("user_id")
            if user_id:
                try:
                    vector_store = get_user_vector_store(user_id)
                    if vector_store:
                        logger.info(f"Storing transcript {transcript_id} for user {user_id}")
                        vector_store.store_transcript(
                            transcript_id=transcript_id,
                            transcript_text=request.transcript,
                            analysis_result=analysis_result,
                            source_type=InputType.TEXT
                        )
                        logger.info(f"✅ Transcript {transcript_id} stored successfully")
                except Exception as e:
                    log_exception(e, context="analyze_text_transcript (storage)", extra_info={"transcript_id": transcript_id})
                    logger.warning(f"Failed to store transcript in database: {e}")
                    # Continue even if storage fails

        return AnalysisResponse(
            success=True,
            transcript_id=transcript_id,
            transcript=request.transcript,
            analysis=analysis_result,
            source_type=InputType.TEXT
        )

    except HTTPException:
        raise
    except (ValidationError, LLMError, DatabaseError) as e:
        log_exception(e, context="analyze_text_transcript")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        log_exception(e, context="analyze_text_transcript")
        logger.error(f"Unexpected error analyzing text transcript: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while analyzing the transcript")


@app.post("/analyze/file", response_model=AnalysisResponse)
async def analyze_file(
    s3_url: str = Form(..., description="S3 URL of the file"),
    transcript_id: Optional[str] = Form(None),
    session: Optional[str] = Cookie(None)
):
    """Analyze document from S3 URL and store in Milvus.

    Args:
        s3_url: S3 URL of the file
        transcript_id: Optional unique identifier

    Returns:
        Analysis results with requirements, recommendations, summary, etc.
    """
    try:
        logger.info(f"Received S3 file storage request: {s3_url}")

        # Validate session
        if not session or session not in SESSIONS:
            raise HTTPException(status_code=401, detail="Unauthorized: Please login first")

        username = SESSIONS[session]
        user_id = USER_DATA.get(username, {}).get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")

        # Download file from S3
        try:
            file_content = get_s3_file(s3_url)
            filename = s3_url.split('/')[-1].split('?')[0]
            logger.info(f"✅ Retrieved {len(file_content)} bytes from S3: {filename}")
        except Exception as e:
            log_exception(e, context="analyze_file (s3_download)", extra_info={"s3_url": s3_url})
            raise HTTPException(status_code=400, detail=f"Failed to download file from S3: {str(e)}")

        # Validate file content
        if not file_content:
            raise ValidationError("Downloaded file is empty", details={"s3_url": s3_url})

        # Generate transcript ID if not provided
        transcript_id = transcript_id or str(uuid.uuid4())

        # Extract text from file
        try:
            transcript_text = DocumentProcessor.process_file(filename, file_content)
        except DocumentProcessingError as e:
            log_exception(e, context="analyze_file (processing)")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            log_exception(e, context="analyze_file (processing)")
            raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")

        if not transcript_text or not transcript_text.strip():
            logger.warning(f"No text extracted from file: {filename}")
            return AnalysisResponse(
                success=False,
                transcript_id=transcript_id,
                error="No text could be extracted from the file",
                source_type=InputType.TEXT
            )

        logger.info(f"✅ Extracted {len(transcript_text)} characters from {filename}")

        # Analyze the transcript using LLM
        try:
            logger.info(f"Analyzing transcript with LLM")
            analysis_result = transcript_analyzer.analyze_transcript(transcript_text)
            logger.info(f"✅ Analysis completed successfully")
        except LLMError as e:
            log_exception(e, context="analyze_file (llm_analysis)")
            raise HTTPException(status_code=500, detail=f"LLM analysis failed: {str(e)}")
        except Exception as e:
            log_exception(e, context="analyze_file (llm_analysis)")
            raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

        # Store in Milvus with analysis
        vector_store = get_user_vector_store(user_id)
        if not vector_store:
            raise DatabaseError("Failed to initialize vector store", details={"user_id": user_id})

        try:
            logger.info(f"Storing transcript {transcript_id} in Milvus for user {user_id}")
            vector_store.store_transcript(
                transcript_id=transcript_id,
                transcript_text=transcript_text,
                analysis_result=analysis_result,
                source_type=f"s3_{Path(filename).suffix}"
            )
            logger.info(f"✅ Transcript {transcript_id} stored successfully in Milvus")
        except Exception as e:
            log_exception(e, context="analyze_file (storage)", extra_info={"transcript_id": transcript_id})
            raise DatabaseError(f"Failed to store in Milvus: {str(e)}", details={"transcript_id": transcript_id})

        return AnalysisResponse(
            success=True,
            transcript_id=transcript_id,
            transcript=transcript_text,
            analysis=analysis_result,
            source_type=InputType.TEXT
        )

    except HTTPException:
        raise
    except (ValidationError, DocumentProcessingError, LLMError, DatabaseError) as e:
        log_exception(e, context="analyze_file")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        log_exception(e, context="analyze_file", extra_info={"s3_url": s3_url})
        logger.error(f"Unexpected error analyzing file: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while analyzing the file")


@app.post("/search", response_model=SearchResponse)
async def search_transcripts(request: SearchRequest, session: Optional[str] = Cookie(None)):
    """Search for similar transcripts.

    Args:
        request: Search request with query text

    Returns:
        List of similar transcripts
    """
    try:
        logger.info(f"Searching for similar transcripts: {request.query[:100]}...")

        # Validate query
        if not request.query or not request.query.strip():
            raise ValidationError("Search query cannot be empty", details={"query_length": len(request.query or "")})

        if not session or session not in SESSIONS:
            logger.warning("Unauthorized search attempt")
            return SearchResponse(
                success=False,
                results=[],
                count=0,
                error="Unauthorized - Please log in"
            )

        username = SESSIONS[session]
        user_id = USER_DATA.get(username, {}).get("user_id")

        if not user_id:
            logger.error(f"User ID not found for username: {username}")
            return SearchResponse(
                success=False,
                results=[],
                count=0,
                error="User ID not found"
            )

        try:
            vector_store = get_user_vector_store(user_id)
            if not vector_store:
                logger.warning(f"Vector store not available for user: {user_id}")
                return SearchResponse(
                    success=False,
                    results=[],
                    count=0,
                    error="Vector store not available. Please try again later."
                )
        except Exception as e:
            log_exception(e, context="search_transcripts (get_vector_store)", extra_info={"user_id": user_id})
            return SearchResponse(
                success=False,
                results=[],
                count=0,
                error="Failed to access vector store"
            )

        try:
            results = vector_store.search_similar_transcripts(
                query_text=request.query,
                top_k=request.top_k
            )
        except (DatabaseError, LLMError) as e:
            log_exception(e, context="search_transcripts (search)")
            return SearchResponse(
                success=False,
                results=[],
                count=0,
                error=f"Search failed: {str(e)}"
            )

        try:
            search_results = [
                SearchResult(
                    transcript_id=r["transcript_id"],
                    transcript_text=r["transcript_text"],
                    analysis_result=r["analysis_result"],
                    source_type=r["source_type"],
                    timestamp=r["timestamp"],
                    distance=r["distance"]
                )
                for r in results
            ]
        except Exception as e:
            log_exception(e, context="search_transcripts (format_results)")
            logger.error(f"Failed to format search results: {e}")
            return SearchResponse(
                success=False,
                results=[],
                count=0,
                error="Failed to format search results"
            )

        logger.info(f"✅ Found {len(search_results)} similar transcripts")
        return SearchResponse(
            success=True,
            results=search_results,
            count=len(search_results)
        )

    except ValidationError as e:
        log_exception(e, context="search_transcripts")
        return SearchResponse(
            success=False,
            results=[],
            count=0,
            error=str(e)
        )
    except Exception as e:
        log_exception(e, context="search_transcripts")
        logger.error(f"Unexpected error searching transcripts: {e}")
        return SearchResponse(
            success=False,
            results=[],
            count=0,
            error="An unexpected error occurred during search"
        )


@app.get("/transcript/{transcript_id}")
async def get_transcript(transcript_id: str, session: Optional[str] = Cookie(None)):
    """Retrieve a transcript by ID.

    Args:
        transcript_id: Transcript identifier

    Returns:
        Transcript data and analysis
    """
    try:
        if not session or session not in SESSIONS:
            raise HTTPException(status_code=401, detail="Unauthorized")

        username = SESSIONS[session]
        user_id = USER_DATA.get(username, {}).get("user_id")

        if not user_id:
            raise HTTPException(status_code=400, detail="User ID not found")

        vector_store = get_user_vector_store(user_id)
        if not vector_store:
            raise HTTPException(status_code=500, detail="Vector store not available")

        result = vector_store.get_transcript_by_id(transcript_id)

        if result:
            return JSONResponse(content={
                "success": True,
                "data": result
            })
        else:
            raise HTTPException(status_code=404, detail="Transcript not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving transcript: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sales-helper", response_model=SalesHelperResponse)
async def sales_helper(request: SalesHelperRequest):
    """Sales helper agent endpoint.

    Captures requirements from salesperson, searches database, and provides recommendations.

    Args:
        request: Salesperson's description of client needs

    Returns:
        Requirements, search results, and recommendations
    """
    try:
        logger.info(f"Sales helper request received: {request.salesperson_input[:100]}...")

        result = sales_helper_agent.process_salesperson_input(request.salesperson_input)

        return SalesHelperResponse(**result)

    except Exception as e:
        logger.error(f"Error in sales helper: {e}")
        return SalesHelperResponse(
            success=False,
            error=str(e)
        )


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, session: Optional[str] = Cookie(None)):
    """Chat with AI agent about stored transcript data.

    Uses LangChain with conversation memory to answer questions based on stored data.

    Args:
        request: User's chat message and optional session ID

    Returns:
        AI response with relevant information from database
    """
    try:
        logger.info(f"Chat request received: {request.message[:100]}...")

        if not session or session not in SESSIONS:
            return ChatResponse(
                success=False,
                answer="Unauthorized",
                error="Unauthorized"
            )

        username = SESSIONS[session]
        user_id = USER_DATA.get(username, {}).get("user_id")

        if not user_id:
            return ChatResponse(
                success=False,
                answer="User ID not found",
                error="User ID not found"
            )

        chat_agent = get_user_chat_agent(user_id)
        if not chat_agent:
            return ChatResponse(
                success=False,
                answer="Chat agent not available",
                error="Chat agent not available"
            )

        result = chat_agent.chat(
            user_message=request.message,
            session_id=request.session_id
        )

        # Save to chat history
        if username not in CHAT_HISTORY:
            CHAT_HISTORY[username] = []

        chat_id = request.session_id or str(uuid.uuid4())
        existing_chat = next((c for c in CHAT_HISTORY[username] if c["id"] == chat_id), None)

        if existing_chat:
            existing_chat["messages"].append({"role": "user", "content": request.message})
            existing_chat["messages"].append({"role": "assistant", "content": result.get("answer", "")})
        else:
            title = request.message[:50] + "..." if len(request.message) > 50 else request.message
            CHAT_HISTORY[username].append({
                "id": chat_id,
                "title": title,
                "messages": [
                    {"role": "user", "content": request.message},
                    {"role": "assistant", "content": result.get("answer", "")}
                ]
            })

        return ChatResponse(**result)

    except Exception as e:
        logger.error(f"Error in chat: {e}")
        return ChatResponse(
            success=False,
            answer="I apologize, but I encountered an error processing your message.",
            error=str(e)
        )


@app.get("/chat/history")
def get_chat_history(session: Optional[str] = Cookie(None)):
    """Get chat history for current user."""
    username = SESSIONS.get(session, "guest")
    return {"success": True, "history": CHAT_HISTORY.get(username, [])}

@app.post("/chat/clear")
def clear_chat(session: Optional[str] = Cookie(None)):
    """Clear chat conversation memory."""
    try:
        if session and session in SESSIONS:
            username = SESSIONS[session]
            user_id = USER_DATA.get(username, {}).get("user_id")
            if user_id:
                chat_agent = get_user_chat_agent(user_id)
                if chat_agent:
                    chat_agent.clear_memory()
            if username in CHAT_HISTORY:
                CHAT_HISTORY[username] = []
        return {"success": True, "message": "Chat memory cleared"}
    except Exception as e:
        logger.error(f"Error clearing chat memory: {e}")
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    import uvicorn

    host = config.get('fastapi.host', '0.0.0.0')
    port = config.get('fastapi.port', 8000)
    reload = config.get('fastapi.reload', True)

    uvicorn.run("src.api.main:app", host=host, port=port, reload=reload)

