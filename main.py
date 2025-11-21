from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from contextlib import asynccontextmanager
from src.handlers.ticket_handler import TicketHandler
import uuid
from datetime import datetime
from src.rag.rag import get_retriever


from src.llm.base import LLMClient
llm_client = LLMClient()
db_available = False

try:
    from src.database.connection import get_db, init_db
    from src.database.models import Ticket
    db_available = True
except Exception as e:
    print(f"Database not available: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    if db_available:
        try:
            init_db()
            print("✅ Database connected successfully")
        except Exception as e:
            print(f"⚠️ Database connection failed: {e}")
            print("Running without database - tickets won't be persisted")
    yield

app = FastAPI(title="IT Help Desk API", version="1.0.0", lifespan=lifespan)

ticket_handler = TicketHandler()
pending_tickets = {}
conversation_history = {}

class TicketRequest(BaseModel):
    user_input: str
    user_id: str
    session_id: Optional[str] = None

class TicketResponse(BaseModel):
    ticket_id: Optional[str] = None
    session_id: str
    status: str
    message: str
    ticket_data: Optional[dict] = None
    detected_action: str

class TicketDetail(BaseModel):
    ticket_id: str
    user_id: str
    title: str
    description: str
    category: str
    priority: str
    assigned_team: str
    suggested_solution: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None

class RAGQuery(BaseModel):
    query: str
    top_k: Optional[int] = 6
    debug: Optional[bool] = False

@app.post("/ticket", response_model=TicketResponse)
async def manage_ticket(request: TicketRequest):
    """
    Single endpoint for IT Help Desk ticket management.
    LLM automatically detects intent from natural language.
    """
    
    session_id = request.session_id or str(uuid.uuid4())
    
    if session_id not in conversation_history:
        conversation_history[session_id] = {"messages": [], "ticket_id": None}
    
    conversation_history[session_id]["messages"].append(request.user_input)
    recent_context = conversation_history[session_id]["messages"][-3:]
    current_ticket_id = conversation_history[session_id]["ticket_id"]
    
    try:
        action = ticket_handler.detect_intent(
            request.user_input,
            recent_context,
            current_ticket_id,
            pending_tickets.get(current_ticket_id) if current_ticket_id else None
        )
        
        if action == "create":
            ticket_info = ticket_handler.process_ticket(request.user_input)
            ticket_id = str(uuid.uuid4())
            
            pending_tickets[ticket_id] = {
                **ticket_info,
                "user_id": request.user_id,
                "created_at": datetime.now().isoformat()
            }
            conversation_history[session_id]["ticket_id"] = ticket_id
            
            return TicketResponse(
                ticket_id=ticket_id,
                session_id=session_id,
                status="pending_confirmation",
                message="Ticket created. Please review and confirm the details.",
                ticket_data=pending_tickets[ticket_id],
                detected_action=action
            )
        
        elif action == "confirm":
            if not current_ticket_id or current_ticket_id not in pending_tickets:
                raise HTTPException(status_code=404, detail="No pending ticket found")
            
            ticket = pending_tickets[current_ticket_id]
            ticket["status"] = "confirmed"
            ticket["confirmed_at"] = datetime.now().isoformat()
            
            # Save to database if available
            if db_available:
                try:
                    db = next(get_db())
                    try:
                        db_ticket = Ticket(
                            ticket_id=current_ticket_id,
                            user_id=ticket.get("user_id", ""),
                            title=ticket.get("title", ""),
                            description=ticket.get("description", ""),
                            category=ticket.get("category", ""),
                            priority=ticket.get("priority", ""),
                            assigned_team=ticket.get("assigned_team", ""),
                            suggested_solution=ticket.get("suggested_solution", ""),
                            status="confirmed",
                            confirmed_at=datetime.now()
                        )
                        db.add(db_ticket)
                        db.commit()
                    finally:
                        db.close()
                except Exception as e:
                    print(f"Failed to save to database: {e}")
            
            db_status = " and saved to database" if db_available else ""
            return TicketResponse(
                ticket_id=current_ticket_id,
                session_id=session_id,
                status="confirmed",
                message=f"Ticket confirmed and assigned to {ticket['assigned_team']}{db_status}",
                ticket_data=ticket,
                detected_action=action
            )
        
        elif action == "modify":
            if not current_ticket_id or current_ticket_id not in pending_tickets:
                raise HTTPException(status_code=404, detail="No pending ticket found")
            
            updated_info = ticket_handler.process_ticket(request.user_input)
            pending_tickets[current_ticket_id].update(updated_info)
            
            return TicketResponse(
                ticket_id=current_ticket_id,
                session_id=session_id,
                status="pending_confirmation",
                message="Ticket updated. Please review and confirm the changes.",
                ticket_data=pending_tickets[current_ticket_id],
                detected_action=action
            )
        
        elif action == "cancel":
            if not current_ticket_id or current_ticket_id not in pending_tickets:
                raise HTTPException(status_code=404, detail="No pending ticket found")
            
            del pending_tickets[current_ticket_id]
            conversation_history[session_id]["ticket_id"] = None
            
            return TicketResponse(
                ticket_id=current_ticket_id,
                session_id=session_id,
                status="cancelled",
                message="Ticket cancelled successfully",
                ticket_data=None,
                detected_action=action
            )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/tickets/user/{user_id}")
async def get_tickets_by_user(user_id: str):
    """Get all tickets for a specific user."""
    if not db_available:
        raise HTTPException(
            status_code=503,
            detail="Database is not configured or not available"
        )
    
    try:
        db = next(get_db())
        try:
            tickets = (
                db.query(Ticket)
                .filter(Ticket.user_id == user_id)
                .order_by(Ticket.created_at.desc())
                .all()
            )
            
            return [{
                "ticket_id": ticket.ticket_id,
                "user_id": ticket.user_id,
                "title": ticket.title,
                "description": ticket.description,
                "category": ticket.category,
                "priority": ticket.priority,
                "assigned_team": ticket.assigned_team,
                "suggested_solution": ticket.suggested_solution,
                "status": ticket.status,
                "created_at": ticket.created_at,
                "confirmed_at": ticket.confirmed_at,
            } for ticket in tickets]
        finally:
            db.close()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error while fetching tickets: {str(e)}"
        )

@app.get("/ticket/{ticket_id}", response_model=TicketDetail)
async def get_ticket_by_id(ticket_id: str):
    if not db_available:
        raise HTTPException(
            status_code=503,
            detail="Database is not configured or not available"
        )
    
    try:
        db = next(get_db())
        try:
            db_ticket = (
                db.query(Ticket)
                .filter(Ticket.ticket_id == ticket_id)
                .first()
            )
            
            if not db_ticket:
                raise HTTPException(status_code=404, detail="Ticket not found")
            
            return TicketDetail(
                ticket_id=db_ticket.ticket_id,
                user_id=db_ticket.user_id,
                title=db_ticket.title,
                description=db_ticket.description,
                category=db_ticket.category,
                priority=db_ticket.priority,
                assigned_team=db_ticket.assigned_team,
                suggested_solution=db_ticket.suggested_solution,
                status=db_ticket.status,
                created_at=db_ticket.created_at,
                confirmed_at=db_ticket.confirmed_at,
            )
        finally:
            db.close()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error while fetching ticket: {str(e)}"
        )

class RAGQuery(BaseModel):
    query: str
    top_k: Optional[int] = 6
    debug: Optional[bool] = False

@app.post("/rag/ask")
def rag_ask(payload: RAGQuery):
    query = payload.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    retriever = get_retriever()
    results = retriever.search(query, limit=payload.top_k)
    # print('fetch_data:', results)
    # print('fetch_data type:', type(results))
    
    if not results or len(results) == 0:
        return {
            "query": query,
            "result": "I don't have any data related to your query in my knowledge base.",
            "chunks_used": 0,
            "chunks": None
        }
    
    chunks = []
    
    # Debug: Print structure of first result
    # if results:
    #     print('First result type:', type(results[0]))
    #     print('First result:', results[0])
    
    for result in results:
        text = None
        
        # Handle different possible structures
        if isinstance(result, dict):
            # Structure: {'entity': {'text': '...'}}
            if 'entity' in result and isinstance(result['entity'], dict):
                text = result['entity'].get('text')
            elif 'text' in result:
                text = result.get('text')
        
        # If result is an object with attributes instead of dict
        elif hasattr(result, 'entity'):
            entity = result.entity
            if isinstance(entity, dict):
                text = entity.get('text')
            elif hasattr(entity, 'text'):
                text = entity.text
        
        # If result has direct text attribute
        elif hasattr(result, 'text'):
            text = result.text
        
        if text and isinstance(text, str) and text.strip():
            chunks.append(text.strip())
    
    # print(f"Extracted {len(chunks)} chunks from {len(results)} results")
    
    # Debug: Print extracted chunks
    # if chunks:
    #     print(f"First chunk preview: {chunks[0][:100]}...")
    
    if not chunks:
        return {
            "query": query,
            "result": "I don't have any data related to your query in my knowledge base.",
            "chunks_used": 0,
            "chunks": None
        }
    
    kb_text = "\n\n".join(chunks)

    prompt = f"""
You are an ITSM expert assistant. Answer ONLY based on the provided knowledge base context.

IMPORTANT RULES:
- If the context does not contain relevant information to answer the query, respond with: "I don't have any data related to your query in my knowledge base."
- Do NOT use external knowledge or make assumptions
- Only provide answers that are directly supported by the context below

Knowledge Base Context:
-----------------------
{kb_text}

User Query:
-----------
{query}

Answer:
"""

    try:
        answer = llm_client.invoke(prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {e}")

    return {
        "query": query,
        "result": answer,
        "chunks_used": len(chunks),
        "chunks": chunks if payload.debug else None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)