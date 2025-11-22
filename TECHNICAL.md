# Corporate Travel Agent - Technical Documentation

**Document Version**: 1.0  
**Last Updated**: November 2025  
**Audience**: Developers, Architects, DevOps Engineers, System Administrators

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Technology Stack](#technology-stack)
3. [System Components](#system-components)
4. [Database Schema](#database-schema)
5. [API Reference](#api-reference)
6. [LangGraph Workflow](#langgraph-workflow)
7. [RAG System](#rag-system)
8. [Authentication & Security](#authentication--security)
9. [Deployment Guide](#deployment-guide)
10. [Development Guide](#development-guide)
11. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                               │
│                  (Web/Mobile/Third-party APIs)                     │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │   JWT Validation    │
                    │   (Header: Bearer)  │
                    └──────────┬──────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│                      FASTAPI LAYER                                  │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │ Routes:                                                    │    │
│  │ • POST /chat - Message processing                        │    │
│  │ • POST /documents/upload - File upload                   │    │
│  │ • GET /sessions/{id}/history - History retrieval         │    │
│  │ • DELETE /sessions/{id} - Session cleanup                │    │
│  │ • GET /health - Health check                             │    │
│  └────────────────────────────────────────────────────────────┘    │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
┌──────────────────┐  ┌────────────────────┐  ┌──────────────────┐
│  LangGraph       │  │  Session Manager   │  │  File Uploader   │
│  Workflow        │  │  (In-Memory Store) │  │  (Background)    │
│  ┌────────────┐  │  │                    │  │                  │
│  │ State      │  │  │ Store:             │  │ Validates:       │
│  │ Graph      │  │  │ • Chat history     │  │ • File type      │
│  │ Processor  │  │  │ • Session info     │  │ • File size      │
│  └──────┬─────┘  │  │ • User context     │  │ Triggers:        │
│         │        │  │                    │  │ • Ingestion task │
│  ┌──────▼─────┐  │  └────────────────────┘  └──────────────────┘
│  │ Tool       │  │
│  │ Execution  │  │
│  │ (Parallel) │  │
│  └────────────┘  │
└──────────────────┘
        │
        ├─────────────┬──────────────┬────────────────┐
        │             │              │                │
        ▼             ▼              ▼                ▼
    ┌─────────┐  ┌────────────┐  ┌──────────────┐  ┌──────────────┐
    │   TRF   │  │   Flight   │  │    Hotel     │  │   Policy QA  │
    │  Tools  │  │    Tools   │  │    Tools     │  │    Tools     │
    └──┬──────┘  └──┬─────────┘  └──┬───────────┘  └──┬───────────┘
       │            │                │                │
       └────────────┼────────────────┼────────────────┘
                    │                │
                    ▼                ▼
        ┌──────────────────┐  ┌───────────────────┐
        │   PostgreSQL     │  │  Milvus Vector DB │
        │   (supabasenDB)       │  │  (RAG Index)      │
        │                  │  │                   │
        │ • TRF Data       │  │ • Policy Chunks   │
        │ • Flights/Hotels │  │ • Embeddings      │
        │ • Bookings       │  │ • Metadata        │
        │ • Airlines/Rooms │  │                   │
        └──────────────────┘  └──────┬────────────┘
                                     │
                          ┌──────────▼─────────┐
                          │  Embeddings Model  │
                          │  (Google Gemini)   │
                          └────────────────────┘
```

### Request Flow Sequence

```
Client Request
    │
    ├─ Extract JWT Token from Header
    │  ├─ Decode JWT
    │  ├─ Extract claims: user_id, role, name, email
    │  └─ Create IdentityPayload
    │
    ├─ Route Request (POST /chat)
    │  ├─ Extract Message from Request
    │  └─ Create ChatRequest Object
    │
    ├─ Initialize Agent
    │  ├─ Validate Role
    │  ├─ Load Role-Specific Tools
    │  ├─ Get/Create Session
    │  └─ Bind Tools to LLM
    │
    ├─ Process Message (Async)
    │  ├─ Build Message Chain with History
    │  ├─ Call LLM (Azure OpenAI)
    │  │  └─ LLM decides tool calls
    │  │
    │  ├─ Execute Tools (Parallel)
    │  │  ├─ Validate Tool Against Role
    │  │  ├─ Parse Tool Arguments
    │  │  ├─ Execute Tool (async)
    │  │  └─ Collect Results
    │  │
    │  ├─ Add Tool Results to Context
    │  ├─ Re-invoke LLM (if tool calls returned)
    │  └─ Repeat until no more tool calls (max 5 iterations)
    │
    ├─ Store Session Data
    │  ├─ Add User Message
    │  ├─ Add Tool Calls (if any)
    │  ├─ Add Tool Results (if any)
    │  └─ Add Assistant Response
    │
    └─ Return ChatResponse
       ├─ Success Status
       ├─ Assistant Message
       ├─ Chat History
       ├─ Session ID
       ├─ Metadata (tools used, role info)
       └─ Error/Warning Info (if applicable)
```

---

## Technology Stack

### Core Framework
- **FastAPI** (v0.100+) - Async web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Request/response validation

### AI/ML
- **LangChain** - LLM orchestration framework
- **LangGraph** - Graph-based workflow engine
- **langchain-litellm** - LLM abstraction layer
- **Azure OpenAI** - Large language model (GPT-4)
- **Google Genai** - Embeddings model

### Data & Database
- **SQLAlchemy** (v2.0+) - ORM for database operations
- **PostgreSQL** / **supabasenDB** - Primary relational database
- **psycopg2-binary** - PostgreSQL adapter
- **Milvus** - Vector database for semantic search (RAG)
- **langchain-milvus** - Milvus integration

### Document Processing
- **PyPDF** - PDF parsing
- **pdfplumber** - Advanced PDF extraction
- **python-docx** - DOCX parsing
- **python-pptx** - PPTX parsing
- **unstructured** - Document chunking and processing
- **Pillow** - Image processing

### Utilities
- **PyJWT** - JWT token handling
- **python-dotenv** - Environment variable management
- **python-multipart** - Multipart form data handling
- **langchain-text-splitters** - Document chunking

### Development
- **pytest** - Testing framework
- **black** - Code formatter
- **mypy** - Static type checking
- **flake8** - Linting

---

## System Components

### 1. FastAPI Application (main.py)

**Purpose**: HTTP API layer exposing travel agent functionality

**Key Components**:

```python
# FastAPI instance
app = FastAPI(title="Corporate Travel Agent", version="1.0.0")

# Middleware
- CORS middleware (if needed)
- JWT authentication dependency injection

# Routes
- POST /chat - Message processing
```

**Key Features**:
- Async request handling
- JWT-based authentication
- Background task support (document ingestion)
- Request/response validation with Pydantic
- Comprehensive error handling

---

### 2. LangGraph Workflow (agent/workflow.py)

**Purpose**: Multi-turn agent with role-based tool access

**Key Classes**:

#### RoleBasedTravelAgent
```python
class RoleBasedTravelAgent:
    """Single agent with role-based tool access."""
    
    Attributes:
    - user_role: User's role (employee, irm, srm, ...)
    - session_id: Unique session identifier
    - employee_id/name: Employee context
    - allowed_tool_names: Tools available to role
    - llm: Azure OpenAI LLM instance
    - llm_with_tools: LLM bound with tools
    - named_tools: Dict of available tools
    
    Methods:
    - process_message()  - Main message processing loop
    - _get_role_tools()  - Filter tools by role
    - _create_system_prompt()  - Generate role-specific system prompt
    - get_available_tools()  - List tools
    - get_session_history()  - Retrieve history
    - clear_session()  - Clear session
```

**Message Processing Flow**:

```
1. Build message chain (system + history + user message)
2. Invoke LLM with tools
3. If LLM returns tool calls:
   a. Validate tool against role
   b. Execute tools in parallel (with sequential fallback)
   c. Add tool results to message chain
   d. Re-invoke LLM (up to 5 iterations)
4. Return final response with chat history
```

**Role-Tool Mapping**:
```python
ROLE_TOOLS_MAP = {
    "employee": [
        "create_trf_draft",
        "submit_trf",
        "list_employee_drafts",
        "get_trf_approval_details",
        "get_trf_status",
        "list_employee_trfs",
        "policy_qa",
    ],
    "irm": [...],
    "srm": [...],
    # ... (BUH, SSUH, BGH, SSGH, CFO, travel_desk)
}
```

---

### 3. Tools System (agent/tools.py)

**Purpose**: LangChain tools for TRF operations, bookings, and policy QA

**Tool Categories**:

#### A. TRF Management Tools

```python
@tool(args_schema=TRFDraftInput)
def create_trf_draft(...) -> str:
    """Create draft TRF with auto-generated number."""

@tool(args_schema=TRFSubmitInput)
def submit_trf(trf_number: str) -> str:
    """Submit draft TRF for approval."""

@tool
def list_employee_drafts(employee_id: str) -> str:
    """List all draft TRFs for employee."""

@tool
def get_trf_approval_details(trf_number: str) -> str:
    """Get full approval chain and details."""

@tool
def get_trf_status(trf_number: str) -> str:
    """Get current TRF status."""
```

#### B. Approval Tools

```python
@tool
def get_pending_irm_applications(irm_name: str) -> str:
    """Get TRFs pending IRM approval."""

@tool(args_schema=ApproveTRFInput)
def approve_trf(trf_number: str, approver_role: str, 
                comments: str) -> str:
    """Approve TRF and advance workflow."""

@tool(args_schema=RejectTRFInput)
def reject_trf(trf_number: str, approver_role: str,
               rejection_reason: str) -> str:
    """Reject TRF and notify employee."""
```

#### C. Flight Booking Tools

```python
@tool(args_schema=SearchFlightsInput)
def search_flights(trf_number: str, origin: str, 
                   destination: str, departure_date: str,
                   cabin_class: str = "economy") -> str:
    """Search available flights."""

@tool(args_schema=ConfirmFlightBookingInput)
def confirm_flight_booking(trf_number: str, flight_id: int) -> str:
    """Confirm and book selected flight."""
```

#### D. Hotel Booking Tools

```python
@tool(args_schema=SearchHotelsInput)
def search_hotels(trf_number: str, city: str,
                  check_in_date: str, check_out_date: str) -> str:
    """Search available hotels."""

@tool(args_schema=ConfirmHotelBookingInput)
def confirm_hotel_booking(trf_number: str, hotel_id: int) -> str:
    """Confirm and book selected hotel."""
```

#### E. Policy QA Tool

```python
@tool(args_schema=PolicyQAInput)
def policy_qa(question: str) -> str:
    """Answer travel policy questions using RAG."""
```

---

### 4. Pydantic Schemas (agent/schema.py)

**Purpose**: Type validation for all inputs/outputs

**Key Schemas**:

```python
# Request Schemas
class TRFDraftInput(BaseModel):
    employee_id: str
    employee_name: str
    travel_type: str
    purpose: str
    origin_city: str
    destination_city: str
    departure_date: str
    # ... more fields

class ApproveTRFInput(BaseModel):
    trf_number: str
    approver_role: str
    comments: str

# Response Schemas
class TRFDraftOutput(BaseModel):
    success: bool
    message: str
    trf_number: Optional[str]
    error: Optional[str]
    error_details: Optional[str]

class ErrorCodes:
    INVALID_DATE_FORMAT = "invalid_date_format"
    INVALID_DATE_RANGE = "invalid_date_range"
    TRF_NOT_FOUND = "trf_not_found"
    INSUFFICIENT_PERMISSIONS = "insufficient_permissions"
```

---

### 5. Database Models (models.py)

**Purpose**: SQLAlchemy ORM models for data persistence

**Core Models**:

#### TravelRequisitionForm
```python
class TravelRequisitionForm(Base):
    __tablename__ = "travel_requisition_forms"
    
    id: int (PK)
    trf_number: str (unique)
    
    # Employee data (embedded)
    employee_id: str
    employee_name: str
    employee_email: str
    # ... more employee fields
    
    # Travel details
    travel_type: TravelType (enum)
    purpose: str
    origin_city: str
    destination_city: str
    departure_date: date
    return_date: date (optional)
    estimated_cost: float
    
    # Approval status and timestamps
    status: TRFStatus (enum)
    irm_approved_at: datetime
    srm_approved_at: datetime
    # ... more approval fields
    
    # Relationships
    travel_bookings: List[TravelBooking]
```

#### FlightInventory
```python
class FlightInventory(Base):
    __tablename__ = "flight_inventory"
    
    id: int (PK)
    airline_id: int (FK -> Airline)
    flight_number: str
    
    # Route
    origin_code: str
    destination_code: str
    origin_city: str
    destination_city: str
    
    # Schedule
    departure_date: date
    departure_time: time
    arrival_date: date
    arrival_time: time
    duration_minutes: int
    
    # Pricing by cabin
    economy_price: float
    premium_economy_price: float (optional)
    business_price: float (optional)
    first_price: float (optional)
```

#### HotelRoomInventory
```python
class HotelRoomInventory(Base):
    __tablename__ = "hotel_room_inventory"
    
    id: int (PK)
    hotel_id: int (FK -> Hotel)
    room_type: str
    occupancy: int
    
    # Date and pricing
    date: date
    base_price: float
    discounted_price: float
    
    # Availability
    is_available: bool
```

#### TravelBooking & Associated
```python
class TravelBooking(Base):
    trf_id: int (FK)
    flight_bookings: List[FlightBooking]
    hotel_bookings: List[HotelBooking]

class FlightBooking(Base):
    travel_booking_id: int (FK)
    flight_id: int (FK)
    pnr: str (unique)
    cabin_class: CabinClass
    
class HotelBooking(Base):
    travel_booking_id: int (FK)
    room_id: int (FK)
    confirmation_number: str (unique)
```

---

### 6. RAG System (src/rag/)

**Purpose**: Retrieval-Augmented Generation for policy Q&A

**Components**:

#### Embeddings (gemini_embedder.py)
```python
class GeminiEmbedder:
    """Google Gemini-based embeddings."""
    
    Methods:
    - embed_query()  - Embed question into vector
    - embed_documents()  - Embed documents for indexing
    
    Returns:
    - Dense vectors (768-dim for Gemini)
```

#### Milvus Retriever (milvus_retriever.py)
```python
class MilvusRetriever:
    """Vector similarity search for policy documents."""
    
    Methods:
    - search()  - Find similar chunks using vector search
    - index_chunks()  - Index document chunks
    - delete_collection()  - Remove old indexes
    
    Similarity:
    - L2 distance
    - Top-K retrieval (default K=5)
```

#### Policy QA (policy_qa.py)
```python
class PolicyQA:
    """Question-answering system for travel policies."""
    
    Flow:
    1. Embed question using Gemini
    2. Search Milvus for similar policy chunks
    3. Build context from retrieved chunks
    4. Send to LLM with context
    5. Return answer with source citations
    
    Methods:
    - query()  - Answer a policy question
```

---

### 7. Configuration (src/config/settings.py)

**Purpose**: Centralized environment configuration

```python
class Settings(BaseModel):
    # Azure OpenAI
    AZURE_API_KEY: str
    AZURE_API_BASE: str
    AZURE_API_VERSION: str = "2024-02-15-preview"
    AZURE_MODEL: str = "azure/gpt-4o"
    
    # Embeddings
    AZURE_OPENAI_KEY: str  # Maps to AZURE_API_KEY
    AZURE_OPENAI_ENDPOINT: str  # Maps to AZURE_API_BASE
    
    # LLM Config
    LLM_TEMPERATURE: float = 0.2
    LLM_VERBOSE: bool = False
    
    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    
    # Storage
    UPLOAD_STORAGE_DIR: str = "docs/uploads"
    
    # Milvus
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530
    
    # Google Gemini (for embeddings)
    GOOGLE_API_KEY: str
```

---

## Database Schema

### Entity-Relationship Diagram

```
┌─────────────────────────────────┐
│    TravelRequisitionForm        │
│  (trf_number PK, unique)        │
├─────────────────────────────────┤
│ id (PK)                         │
│ trf_number (unique)             │
│ employee_id/name/email          │
│ travel_type                     │
│ purpose                         │
│ status (enum)                   │
│ departure_date, return_date     │
│ estimated_cost                  │
│ irm_approved_at, comments       │
│ srm_approved_at, comments       │
│ ... (all approver fields)       │
└────────────────┬────────────────┘
                 │
        ┌────────▼────────┐
        │ 1:N relationship│
        │ (TravelBooking) │
        └────────┬────────┘
                 │
┌────────────────▼─────────────────┐
│      TravelBooking              │
│  (booking_number PK, unique)    │
├──────────────────────────────────┤
│ id (PK)                          │
│ trf_id (FK)                      │
│ booking_number (unique)          │
│ traveler_name/email              │
│ total_flight_cost                │
│ total_hotel_cost                 │
│ total_cost                       │
│ status (enum)                    │
└────────┬───────────┬─────────────┘
         │           │
         │      ┌────▼──────────────┐
         │      │ 1:N relationships │
         │      └────┬──────────────┘
         │           │
    ┌────▼─────────┐ │
    │FlightBooking │ │ ┌──────────────────┐
    │ (pnr PK)     │ │ │HotelBooking      │
    ├──────────────┤ │ │(conf_number PK)  │
    │id (PK)       │ │ ├──────────────────┤
    │pnr (unique)  │ │ │id (PK)           │
    │flight_id(FK) │ │ │confirmation_no   │
    │cabin_class   │ │ │room_id (FK)      │
    │status        │ │ │guest_name        │
    │base_fare     │ │ │check_in/out_date │
    │final_fare    │ │ │num_nights        │
    └──────┬───────┘ │ │per_night_rate    │
           │         │ │total_room_cost   │
           │      └──▼─┴──────────────────┘
           │         │
           │    ┌────▼──────────────┐
           │    │ FKs to Inventory  │
           │    └───────────────────┘
           │         │
    ┌──────▼────────────────────┐
    │  FlightInventory          │
    │ (flight_number PK, date)  │
    ├──────────────────────────┤
    │ id (PK)                  │
    │ airline_id (FK)          │
    │ flight_number            │
    │ origin/destination       │
    │ departure/arrival time   │
    │ economy/business_price   │
    │ is_available             │
    └───────┬──────────────────┘
            │
      ┌─────▼─────────────┐
      │  Airline          │
      │(code PK, unique)  │
      ├───────────────────┤
      │ code              │
      │ name              │
      │ corp_discount %   │
      └───────────────────┘

    ┌──────────────────────────────┐
    │  HotelRoomInventory          │
    │(hotel_id + date PK)          │
    ├──────────────────────────────┤
    │ id (PK)                      │
    │ hotel_id (FK)                │
    │ room_type                    │
    │ date                         │
    │ base_price                   │
    │ discounted_price             │
    │ is_available                 │
    └───────┬──────────────────────┘
            │
      ┌─────▼──────────────────┐
      │  Hotel               │
      │(id PK)               │
      ├──────────────────────┤
      │ name                 │
      │ city, country        │
      │ rating               │
      │ corp_discount %      │
      │ amenities (JSON)     │
      └──────────────────────┘

    ┌───────────────────────┐
    │  City (Reference)     │
    ├───────────────────────┤
    │ city (PK, unique)     │
    │ country               │
    │ currency              │
    │ tier_multiplier       │
    └───────────────────────┘

    ┌───────────────────────┐
    │  Airport (Reference)  │
    ├───────────────────────┤
    │ code (PK, unique)     │
    │ city                  │
    │ country               │
    │ timezone              │
    └───────────────────────┘
```

### Key Indexes

## API Reference

### 1. Chat Endpoint

**Endpoint**: `POST /chat`  
**Authentication**: JWT Bearer Token  
**Rate Limit**: 100 req/min per user

**Request**:
```json
{
  "message": "I need to travel to New York for a client meeting"
}
```

**Response**:
```json
{
  "success": true,
  "message": "I'd be happy to help you plan your travel...",
  "chat_history": [
    {
      "role": "user",
      "content": "I need to travel to New York for a client meeting",
      "timestamp": "2025-11-21T10:30:00Z",
      "tool_calls": null,
      "tool_results": null
    },
    {
      "role": "assistant",
      "content": "I'd be happy to help...",
      "timestamp": "2025-11-21T10:30:05Z",
      "tool_calls": [
        {
          "name": "create_trf_draft",
          "id": "call_123",
          "args": {...}
        }
      ],
      "tool_results": [
        {
          "tool": "create_trf_draft",
          "result": {...},
          "is_error": false
        }
      ]
    }
  ],
  "session_id": "EMP001",
  "data": {
    "role": "employee",
    "employee_id": "EMP001",
    "available_tools": ["create_trf_draft", "submit_trf", ...],
    "tool_count": 7,
    "message_count": 1,
    "tool_calls": [...],
    "tool_results": [...]
  }
}
```

**Error Response**:
```json
{
  "success": false,
  "message": "An error occurred while processing your request.",
  "error": "processing_error",
  "error_details": "Detailed error message",
  "suggestions": [
    "Check your message format",
    "Verify you have permission for the requested action"
  ]
}
```


---

## Authentication & Security

### JWT Token Structure

```python
# Payload
{
    "user_id": "EMP001",
    "role": "employee|irm|srm|buh|ssuh|bgh|ssgh|cfo|travel_desk",
    "name": "John Doe",
    "email": "john.doe@company.com",
    "iat": 1700000000,
    "exp": 1700086400,  # 24 hours
    "iss": "travel-agent",
    "sub": "EMP001"
}

# Signing Algorithm: HS256
# Secret: JWT_SECRET from environment
```

### Token Generation

```bash
# Generate test token
python jwt_gen.py --user-id EMP001 --role employee --name "John Doe"

# Output:
# eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiRU1QMDAxIiwi...
```

### Token Validation

```python
def get_identity(authorization: str = Header(...)) -> IdentityPayload:
    # Extract token from "Bearer <token>"
    # Decode JWT
    # Verify signature
    # Check expiration
    # Extract required claims
    # Return IdentityPayload
```

### Security Best Practices

1. **HTTPS**: All communication over HTTPS
2. **Token Expiration**: 24-hour token lifetime
3. **Rate Limiting**: 100 req/min per user
4. **Input Validation**: Pydantic validation on all inputs
5. **Tool Whitelisting**: Strict role-based tool access
6. **Session Isolation**: Users can only access own sessions
7. **Error Handling**: No sensitive data in error messages
8. **Audit Logging**: All actions logged with timestamps
9. **Database**: Encrypted at rest (PostgreSQL)

---

## Deployment Guide

### Prerequisites

- PostgreSQL 14+
- Milvus 2.0+
- Python 3.9+
- Azure OpenAI credentials
- Google Gemini API key

### Local Development Setup

```bash
# 1. Clone repository
git clone <repo-url>
cd travel_desk

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r req.txt

# 4. Setup environment
cp .env.example .env
# Edit .env with your credentials

# 5. Initialize database
python -c "from models import Base; from sqlalchemy import create_engine; \
engine = create_engine(os.getenv('DATABASE_URL')); \
Base.metadata.create_all(engine)"

# 6. Seed reference data (optional)
python seed.py

# 7. Start application
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
## Development Guide

### Adding a New Tool

**Step 1: Define Schema** (`agent/schema.py`)
```python
class MyToolInput(BaseModel):
    param1: str = Field(..., description="Parameter 1")
    param2: int = Field(default=10, description="Parameter 2")
```

**Step 2: Create Tool** (`agent/tools.py`)
```python
@tool(args_schema=MyToolInput)
def my_new_tool(param1: str, param2: int) -> str:
    """
    Tool description for LLM.
    
    Usage: When user wants to...
    """
    try:
        # Implementation
        result = do_something(param1, param2)
        return json.dumps({"success": True, "data": result})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})
```

**Step 3: Register Tool** (`agent/tools.py`)
```python
ALL_TOOLS = [
    create_trf_draft,
    my_new_tool,  # Add here
    # ... other tools
]
```

**Step 4: Add to Role** (`agent/workflow.py`)
```python
ROLE_TOOLS_MAP = {
    "employee": ["my_new_tool", ...],
    # ... other roles
}
```

### Running Tests

```bash

# Run specific test file
pytest tests/test_tools.py

# Run with coverage
pytest --cov=. --cov-report=html

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code
black .

# Lint
flake8 .

# Type check
mypy .

# Pre-commit hooks
pre-commit install
```

---

## Troubleshooting

### Common Issues

#### 1. PostgreSQL Connection Error

**Error**: `psycopg2.OperationalError: could not connect to server`

**Solution**:
```bash
# Check PostgreSQL is running
psql -U postgres -h localhost

# Verify DATABASE_URL in .env
# Format: postgresql://user:password@host:port/database

# If using supabasenDB, ensure connection pooling enabled
# Add: ?sslmode=require
```

#### 2. Azure OpenAI API Error

**Error**: `OpenAIError: Invalid API key`

**Solution**:
```bash
# Verify credentials
echo $AZURE_API_KEY
echo $AZURE_API_BASE

# Check Azure portal for valid endpoints
# Ensure API version matches
AZURE_API_VERSION=2024-02-15-preview
```

**Monitor Requests**:
```bash
# Use FastAPI debug mode
app = FastAPI(debug=True)

# Check /docs for interactive API testing
http://localhost:8000/docs
```

---

## Performance Optimization

### Database Indexes

Already configured. Check `sql_script.sql` for details.

### Caching Strategy

```python
# LRU cache for settings
@lru_cache(maxsize=1)
def _build_settings() -> Settings:
    return Settings(**data)
```

### Async Optimization

- All I/O operations are async
- Tool execution runs in parallel (asyncio.gather)
- Database connections use connection pooling

### Vector Search Optimization

- Milvus indexes with IVF_FLAT for accuracy
- Top-K retrieval set to 5 (configurable)
- Chunk size 1000 tokens with 50% overlap

---

**End of Technical Documentation**

**Last Updated**: November 2025  
**Contact**: tech-support@company.com
