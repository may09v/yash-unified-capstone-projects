# File: /agent/workflow.py
# Location: agent/
# Description: Role-based travel agent with unified tool access and session memory

"""
Single Agent with Role-Based Tool Access for Corporate Travel Management System

This module implements a unified agent that handles all user roles:
- employee: Can create travel requests, track status, save drafts
- irm, srm, buh, ssuh, bgh, ssgh, cfo: Multi-level approval authority with message capability
- travel_desk: Can track, plan, book, and manage travel

The agent dynamically assigns tools based on the user's role and includes context about
employee information in the system prompt.

Includes conversation memory management with session support for multi-turn conversations.
"""

import asyncio
import json
from typing import Optional, List, Dict, Any
from datetime import datetime

from langchain_litellm import ChatLiteLLM
from langchain_core.tools import Tool
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage, BaseMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict

from agent.tools import ALL_TOOLS
from agent.schema import *
from src.config.settings import settings


# ============================================================================
# ROLE-BASED TOOL MAPPING
# ============================================================================

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
    "irm": [
        "get_pending_irm_applications",
        "get_trf_approval_details",
        "get_trf_status",
        "approve_trf",
        "policy_qa",
        "reject_trf",
    ],
    "srm": [
        "get_pending_srm_applications",
        "get_trf_approval_details",
        "get_trf_status",
        "approve_trf",
        "policy_qa",
        "reject_trf",
        "list_employee_trfs",
    ],
    "buh": [
        "get_pending_buh_applications",
        "get_trf_approval_details",
        "get_trf_status",
        "policy_qa",
        "approve_trf",
        "reject_trf",
    ],
    "ssuh": [
        "get_pending_ssuh_applications",
        "get_trf_approval_details",
        "get_trf_status",
        "policy_qa",
        "approve_trf",
        "reject_trf",
    ],
    "bgh": [
        "get_pending_bgh_applications",
        "get_trf_approval_details",
        "get_trf_status",
        "policy_qa",
        "approve_trf",
        "reject_trf",
    ],
    "ssgh": [
        "get_pending_ssgh_applications",
        "get_trf_approval_details",
        "get_trf_status",
        "policy_qa",
        "approve_trf",
        "reject_trf",
    ],
    "cfo": [
        "get_pending_cfo_applications",
        "get_trf_approval_details",
        "get_trf_status",
        "approve_trf",
        "reject_trf",
        "policy_qa",
        "list_employee_trfs",
    ],
  "travel_desk": [
        "get_approved_for_travel_desk",
        "track_all_applications",
        "approve_trf",
        "complete_travel_plan",
        "search_flights",
        "search_alternate_flights",
        "confirm_flight_booking",
        "search_hotels",
        "search_alternate_hotels",
        "confirm_hotel_booking",
        "mark_trf_completed",
        "get_trf_status",
        "list_employee_trfs",
        "policy_qa",
    ],
}

# Approver levels for role mapping
APPROVER_ROLE_MAP = {
    "irm": "irm",
    "srm": "srm",
    "buh": "buh",
    "ssuh": "ssuh",
    "bgh": "bgh",
    "ssgh": "ssgh",
    "cfo": "cfo",
    "travel_desk": "travel_desk",
}


# ============================================================================
# CONVERSATION STATE AND MEMORY
# ============================================================================

class ConversationMessage(TypedDict):
    """Structure for storing conversation messages."""
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: str
    tool_calls: Optional[List[Dict[str, Any]]]
    tool_results: Optional[List[Dict[str, Any]]]


class AgentState(TypedDict):
    """State for LangGraph workflow."""
    messages: List[BaseMessage]
    user_input: str
    response: str
    chat_history: List[ConversationMessage]
    role: str
    employee_id: str
    employee_name: str
    employee_info: Dict[str, Any]


class SessionMemoryManager:
    """
    Manages conversation memory and session storage for the travel agent.
    Stores chat history with timestamps and tool execution details.
    """
    
    def __init__(self):
        """Initialize session memory manager with in-memory storage."""
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.checkpointer = InMemorySaver()
    
    def get_or_create_session(self, session_id: str, role: str, employee_id: str, 
                              employee_name: str, employee_info: Dict[str, Any]) -> Dict[str, Any]:
        """Get or create a session for a user."""
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "session_id": session_id,
                "role": role,
                "employee_id": employee_id,
                "employee_name": employee_name,
                "employee_info": employee_info,
                "messages": [],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "message_count": 0,
            }
        return self.sessions[session_id]
    
    def add_message(self, session_id: str, role: str, content: str, 
                   tool_calls: Optional[List[Dict[str, Any]]] = None,
                   tool_results: Optional[List[Dict[str, Any]]] = None) -> None:
        """Add a message to the session history."""
        if session_id not in self.sessions:
            return
        
        message: ConversationMessage = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "tool_calls": tool_calls,
            "tool_results": tool_results,
        }
        self.sessions[session_id]["messages"].append(message)
        self.sessions[session_id]["updated_at"] = datetime.now().isoformat()
        self.sessions[session_id]["message_count"] += 1
    
    def get_session_history(self, session_id: str) -> List[ConversationMessage]:
        """Get all messages in a session."""
        if session_id not in self.sessions:
            return []
        return self.sessions[session_id]["messages"]
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session metadata."""
        return self.sessions.get(session_id)
    
    def clear_session(self, session_id: str) -> None:
        """Clear a session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def get_all_sessions(self) -> Dict[str, Dict[str, Any]]:
        """Get all active sessions."""
        return self.sessions.copy()


# Global session memory manager
_session_memory = SessionMemoryManager()


# ============================================================================
# ROLE-BASED AGENT
# ============================================================================

class RoleBasedTravelAgent:
    """
    Single agent with role-based tool access for corporate travel management.
    
    Handles multiple user roles with appropriate tool restrictions and system
    prompts tailored to each role's responsibilities. Includes session-based
    memory for multi-turn conversations.
    """

    def __init__(self, user_role: str, session_id: str, employee_id: Optional[str] = None, 
                 employee_name: Optional[str] = None, employee_info: Optional[Dict[str, Any]] = None):
        """
        Initialize the role-based agent with session support.
        
        Args:
            user_role: User's role (employee, irm, srm, buh, ssuh, bgh, ssgh, cfo, travel_desk)
            session_id: Unique session identifier for conversation history
            employee_id: Current employee's ID (for employees)
            employee_name: Current employee's name (for employees)
            employee_info: Additional employee information
        """
        self.user_role = user_role.lower()
        self.session_id = session_id
        self.employee_id = employee_id
        self.employee_name = employee_name
        self.employee_info = employee_info or {}
        
        # Validate role
        if self.user_role not in ROLE_TOOLS_MAP:
            raise ValueError(f"Invalid role: {user_role}. Must be one of {list(ROLE_TOOLS_MAP.keys())}")
        
        # Initialize or get session
        self.session = _session_memory.get_or_create_session(
            session_id, self.user_role, employee_id or "", employee_name or "", self.employee_info
        )
        
        # Initialize LLM using ChatLiteLLM with configured Azure OpenAI
        self.llm = ChatLiteLLM(
            model=settings.AZURE_MODEL,
            temperature=0.7,
            verbose=settings.LLM_VERBOSE,
        )
        
        # Get allowed tools for this role
        self.allowed_tool_names = ROLE_TOOLS_MAP[self.user_role]
        self.tools = self._get_role_tools()
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # Create tool dict for easy access
        self.named_tools = {tool.name: tool for tool in self.tools}

    def _get_role_tools(self) -> List[Tool]:
        """Get filtered tools based on user role."""
        tools = []
        for tool in ALL_TOOLS:
            if tool.name in self.allowed_tool_names:
                tools.append(tool)
        return tools

    def _create_system_prompt(self) -> str:
        """Create a role-specific system prompt."""
        
        role_prompts = {
            "employee": """You are a corporate travel assistant for employees.

MISSION: Help employees create, save, and submit travel requisition forms (TRFs) with minimal friction.

WORKFLOW:
1. Gather travel details: destination, departure/return dates, purpose, estimated cost
2. Call create_trf_draft with all information; confirm next steps with the employee
3. When ready, offer to submit using submit_trf
4. Use list_employee_drafts or list_employee_trfs to show history when asked
5. Use get_trf_status or get_trf_approval_details to explain where a TRF stands in the approval chain

POLICY QUESTIONS:
Use policy_qa tool to answer questions about YASH travel policies covering domestic and international travel.
Get answers about: travel eligibility by grade (M1+, E6-E8, E3-E5, T-E2), daily allowance rates by destination/region,
accommodation and airline entitlements, per diem eligibility, travel advance limits, client-borne expense scenarios,
family emergency procedures, and reimbursement requirements. For domestic travel: Tier I vs Tier II city rates, train/air/bus
eligibility by grade. For international travel: region-specific allowances (Americas, Asia, Europe, Africa, Oceania),
passport requirements, visa procedures. The tool retrieves accurate policy answers with source citations from official company
travel policies, ensuring employees understand entitlements before submitting travel requests.

TONE: Friendly, clear, and action-oriented. Assume users are non-technical.
ERRORS: If draft creation fails, ask for clarification on dates or cost. If submission fails, explain the error and suggest retrying or saving as draft.

Available tools: create_trf_draft, submit_trf, list_employee_drafts, list_employee_trfs, get_trf_status, get_trf_approval_details, policy_qa.""",

            "irm": """You are a travel approver assistant for IRMs (Immediate Reporting Managers).

MISSION: First-level approval of travel requests. Act decisively when user says "approve TRF[number]".

APPROVAL WORKFLOW (when user says "approve TRF###"):
1. Extract the TRF number (e.g., "TRF202500002")
2. Call get_trf_approval_details(trf_number) to fetch full context
3. When details show status="pending_irm", immediately call approve_trf(trf_number, "irm", comments)
4. Present approval result with travel details and next approval step
5. Do NOT wait for confirmation or ask follow-up questions; the user's "approve" intent is clear

OTHER ACTIONS:
- View pending: Use get_pending_irm_applications to see your approval queue
- Reject: Use reject_trf with a specific business reason (min 10 chars)
- Status: Use get_trf_status to check any TRF's progress

ERRORS: If a TRF is not in "pending_irm" status, explain why it cannot be approved at your level.

Approval level: IRM (first approval) → routes to SRM when approved.""",

            "srm": """You are a travel approver assistant for SRMs (Senior/Second Reporting Managers).

MISSION: Second-level approval. Review approvals from IRM and add leadership perspective.

APPROVAL WORKFLOW (when user says "approve TRF###"):
1. Extract TRF number
2. Call get_trf_approval_details(trf_number) for full context, including IRM approval details
3. When status="pending_srm", immediately call approve_trf(trf_number, "srm", comments)
4. Return result with full approval chain history
5. Act decisively; do not ask for confirmation

OTHER ACTIONS:
- View pending: Use get_pending_srm_applications to see your queue
- Reject: Use reject_trf with business reason
- Status/history: Use get_trf_status or list_employee_trfs

ERRORS: If status is not "pending_srm", explain the current stage and next approver.

Approval level: SRM (second approval) → routes to BUH when approved.""",

            "buh": """You are a travel approver assistant for BUHs (Business Unit Heads).

MISSION: Business unit-level approval. Balance budget and operational needs.

APPROVAL WORKFLOW:
1. Call get_trf_approval_details(trf_number) to see full history (IRM, SRM approvals)
2. Review estimated cost, travel purpose, and previous approvals
3. If status="pending_buh", call approve_trf(trf_number, "buh", comments including budget rationale)
4. If rejecting, explain budget or operational constraint

CONSIDERATIONS:
- Check estimated cost against unit budget
- Review employee's travel frequency and purpose
- Provide clear business justification in approval comments

Available tools: get_pending_buh_applications, get_trf_approval_details, get_trf_status, approve_trf, reject_trf.
Approval level: BUH → routes to SSUH when approved.""",

            "ssuh": """You are a travel approver assistant for SSUHs (Senior/Secondary Unit Heads).

MISSION: Strategic unit-level review. Ensure strategic alignment and policy compliance.

APPROVAL WORKFLOW:
1. Call get_trf_approval_details(trf_number) to review full approval chain (IRM, SRM, BUH)
2. Focus on strategic business value and policy adherence
3. If status="pending_ssuh", call approve_trf(trf_number, "ssuh", strategic justification)
4. If rejecting, provide clear strategic reason

TONE: Professional, focused on business impact and alignment.

Available tools: get_pending_ssuh_applications, get_trf_approval_details, get_trf_status, approve_trf, reject_trf.
Approval level: SSUH → routes to BGH when approved.""",

            "bgh": """You are a travel approver assistant for BGHs (Business Group Heads).

MISSION: Group-level leadership approval. Ensure policy compliance and group strategy alignment.

APPROVAL WORKFLOW:
1. Call get_trf_approval_details(trf_number) to review full approval history
2. Review all previous approvals (IRM, SRM, BUH, SSUH)
3. Check total cost and business value
4. If status="pending_bgh", call approve_trf(trf_number, "bgh", executive summary)
5. If rejecting, provide executive-level reason

FOCUS: Group-wide compliance, strategic fit, total cost impact.

Available tools: get_pending_bgh_applications, get_trf_approval_details, get_trf_status, approve_trf, reject_trf.
Approval level: BGH → routes to SSGH when approved.""",

            "ssgh": """You are a travel approver assistant for SSGHs (Senior/Secondary Group Heads).

MISSION: Senior leadership approval. Ensure company-wide strategic alignment.

APPROVAL WORKFLOW:
1. Call get_trf_approval_details(trf_number) to review complete approval chain
2. Assess strategic alignment with company objectives
3. Review all approvals and final cost
4. If status="pending_ssgh", call approve_trf(trf_number, "ssgh", strategic approval rationale)
5. If rejecting, explain misalignment with company strategy

TONE: Strategic and concise. Focus on big-picture alignment.

Available tools: get_pending_ssgh_applications, get_trf_approval_details, get_trf_status, approve_trf, reject_trf.
Approval level: SSGH → routes to CFO when approved.""",

            "cfo": """You are a travel approver assistant for the CFO (Chief Financial Officer).

MISSION: Final financial review before travel desk execution. Approve decisively when requested.

APPROVAL WORKFLOW (when user says "approve TRF###"):
1. Extract TRF number
2. Call get_trf_approval_details(trf_number) to review full approval chain and final cost
3. When status="pending_cfo", immediately call approve_trf(trf_number, "cfo", financial review notes)
4. Return result with financial summary
5. Act decisively; do not ask for confirmation or additional details

CRITICAL: If user says "approve", they have already decided. Execute approval in one flow.

OTHER ACTIONS:
- View pending: Use get_pending_cfo_applications to see your approval queue
- Reject: Use reject_trf with financial reason
- Status: Use get_trf_status or list_employee_trfs

ERRORS: If status is not "pending_cfo", explain the current stage and next handler.

Approval level: CFO (pre-travel desk) → routes to Travel Desk when approved.""",

            "travel_desk": """You are a travel planning assistant for the Travel Desk.

MISSION: Manage travel arrangements for approved TRFs.

WORKFLOW:
1. **ACKNOWLEDGE**: Use `get_approved_for_travel_desk()` -> `approve_trf()`.
2. **PLAN & BOOK**:
   - **Context**: Always call `get_trf_status()` first to get travel details.
   - **Search**: Use `search_flights()` or `search_hotels()`.
   - **Alternatives**: If specific dates are unavailable, **DO NOT** spam single-day searches. Use `search_alternate_flights()` or `search_alternate_hotels()` to check a date range in one go.
   - **Book**: Use `confirm_flight_booking()` / `confirm_hotel_booking()`.
3. **COMPLETE**: Use `mark_trf_completed()` only after booking.

TOOL USAGE:
- `get_approved_for_travel_desk()`: Dashboard for Pending/Active requests.
- `get_trf_status(trf_number)`: **ALWAYS use this to get flight/hotel parameters (cities, dates) if unknown.**
- `search_flights(...)`: Requires origin, destination, date. Fetch these from TRF status first.
- `mark_trf_completed()`: Use only after bookings are done.

INTERACTION EXAMPLES:
User: "Search flights for TRF2025001"
You: (Call `get_trf_status` -> see it's Delhi to Mumbai on Dec 1st) -> (Call `search_flights(..., origin="Delhi", destination="Mumbai", date="2025-12-01")`)
User: "Book flight ID 5"
You: `confirm_flight_booking(...)`
User: "Done"
You: `mark_trf_completed(...)`

TONE: Professional. Do not be lazy; look up details yourself before asking.""",
        }
        
        base_prompt = role_prompts.get(self.user_role, "You are a corporate travel management assistant.")
        
        # Add employee context if provided
        if self.employee_id and self.user_role == "employee":
            base_prompt += f"""

EMPLOYEE CONTEXT:
- Employee ID: {self.employee_id}
- Name: {self.employee_name}
"""
            if self.employee_info:
                for key, value in self.employee_info.items():
                    base_prompt += f"- {key.replace('_', ' ').title()}: {value}\n"

        base_prompt += """

UNIVERSAL PRINCIPLES:
1. Only call tools available to your role (enforce strict tool access)
2. Be concise and action-oriented in responses
3. Always include business justification when approving/rejecting
4. Ask clarifying questions only when information is genuinely missing
5. Never ask for technical parameters; use system defaults
6. If tool execution fails, explain the error clearly and suggest alternatives
7. Maintain audit trail in approval comments (record business rationale)"""

        return base_prompt

    async def process_message(self, user_message: str) -> Dict[str, Any]:
        """
        Process a user message using the role-based agent with session memory.
        
        Args:
            user_message: The user's input message
            
        Returns:
            Dictionary containing response, chat history, and metadata
        """
        system_prompt = self._create_system_prompt()
        
        # Get conversation history from session
        chat_history = _session_memory.get_session_history(self.session_id)
        
        # Build messages with history context
        messages = [SystemMessage(content=system_prompt)]
        
        # Add recent conversation history (last 10 messages to keep context manageable)
        for hist_msg in chat_history[-10:]:
            if hist_msg["role"] == "user":
                messages.append(HumanMessage(content=hist_msg["content"]))
            elif hist_msg["role"] == "assistant":
                messages.append(AIMessage(content=hist_msg["content"]))
        
        # Add current user message
        messages.append(HumanMessage(content=user_message))
        
        # Store user message in session
        _session_memory.add_message(self.session_id, "user", user_message)
        
        # Get initial response from LLM
        response = await self.llm_with_tools.ainvoke(messages)

        tool_calls_info: List[Dict[str, Any]] = []
        tool_results_info: List[Dict[str, Any]] = []

        # Shortcut return when no tool calls are required
        if not getattr(response, "tool_calls", None):
            assistant_response = response.content or "I understand. How can I help you further?"
            _session_memory.add_message(self.session_id, "assistant", assistant_response)

            return {
                "response": assistant_response,
                "chat_history": _session_memory.get_session_history(self.session_id),
                "session_id": self.session_id,
                "tool_calls": None,
            }

        max_tool_iterations = 5
        iteration = 0

        # Multi-turn agent loop: continues until LLM stops calling tools (max 5 iterations)
        # This enables tool chaining where LLM can call tools, see results, then call more tools
        while getattr(response, "tool_calls", None):
            iteration += 1
            if iteration > max_tool_iterations:
                assistant_response = (
                    "I tried using multiple tools but couldn't finish within the allowed steps. "
                    "Please restate your request with more specifics."
                )
                _session_memory.add_message(self.session_id, "assistant", assistant_response)
                updated_history = _session_memory.get_session_history(self.session_id)
                return {
                    "response": assistant_response,
                    "chat_history": updated_history,
                    "session_id": self.session_id,
                    "tool_calls": tool_calls_info if tool_calls_info else None,
                    "tool_results": tool_results_info if tool_results_info else None,
                }

            # Add LLM response with tool calls to message chain for context
            messages.append(AIMessage(content=response.content or "", tool_calls=response.tool_calls))

            iteration_tool_calls: List[Dict[str, Any]] = []
            iteration_tool_results: List[Dict[str, Any]] = []
            tool_execution_tasks: List[Any] = []
            tool_call_map: Dict[str, Dict[str, Any]] = {}

            # Prepare all tool executions (collect tasks for parallel execution)
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call.get("args") or {}
                tool_id = tool_call["id"]

                iteration_tool_calls.append({
                    "name": tool_name,
                    "id": tool_id,
                    "args": tool_args,
                })

                if tool_name not in self.named_tools:
                    error_msg = f"Tool '{tool_name}' is not available for role '{self.user_role}'."
                    tool_message = ToolMessage(tool_call_id=tool_id, content=error_msg, is_error=True)
                    messages.append(tool_message)
                    iteration_tool_results.append({
                        "tool": tool_name,
                        "result": error_msg,
                        "is_error": True,
                    })
                    continue

                tool_call_map[tool_id] = {
                    "tool_name": tool_name,
                    "tool_args": tool_args,
                }
                tool = self.named_tools[tool_name]
                tool_execution_tasks.append(tool.ainvoke(tool_args))

            # Execute all tools in parallel for speed, with fallback to sequential if needed
            if tool_execution_tasks:
                try:
                    # Parallel execution: all tools run concurrently
                    results = await asyncio.gather(*tool_execution_tasks, return_exceptions=True)
                    for result, (tool_id, call_info) in zip(results, tool_call_map.items()):
                        if isinstance(result, Exception):
                            error_msg = f"Error executing tool '{call_info['tool_name']}': {str(result)}"
                            tool_message = ToolMessage(tool_call_id=tool_id, content=error_msg, is_error=True)
                            iteration_tool_results.append({
                                "tool": call_info["tool_name"],
                                "result": error_msg,
                                "is_error": True,
                            })
                        else:
                            tool_message = ToolMessage(
                                tool_call_id=tool_id,
                                content=json.dumps(result) if not isinstance(result, str) else result
                            )
                            iteration_tool_results.append({
                                "tool": call_info["tool_name"],
                                "result": result,
                                "is_error": False,
                            })
                        messages.append(tool_message)
                except Exception as e:
                    # Fallback: execute sequentially if parallel fails (resilience strategy)
                    for tool_call in response.tool_calls:
                        if tool_call["id"] not in tool_call_map:
                            continue
                        tool_name = tool_call_map[tool_call["id"]]["tool_name"]
                        tool_args = tool_call_map[tool_call["id"]]["tool_args"]
                        tool_id = tool_call["id"]
                        try:
                            tool = self.named_tools[tool_name]
                            result = await tool.ainvoke(tool_args)
                            tool_message = ToolMessage(
                                tool_call_id=tool_id,
                                content=json.dumps(result) if not isinstance(result, str) else result
                            )
                            iteration_tool_results.append({
                                "tool": tool_name,
                                "result": result,
                                "is_error": False,
                            })
                        except Exception as te:
                            error_msg = f"Error executing tool '{tool_name}': {str(te)}"
                            tool_message = ToolMessage(tool_call_id=tool_id, content=error_msg, is_error=True)
                            iteration_tool_results.append({
                                "tool": tool_name,
                                "result": error_msg,
                                "is_error": True,
                            })
                        messages.append(tool_message)

            # Persist iteration details for analytics
            tool_calls_info.extend(iteration_tool_calls)
            tool_results_info.extend(iteration_tool_results)

            _session_memory.add_message(
                self.session_id,
                "assistant",
                response.content or "Processing tools...",
                tool_calls=iteration_tool_calls or None,
                tool_results=iteration_tool_results or None
            )

            response = await self.llm_with_tools.ainvoke(messages)

        assistant_response = response.content or "I completed the requested action."
        _session_memory.add_message(self.session_id, "assistant", assistant_response)

        updated_history = _session_memory.get_session_history(self.session_id)

        return {
            "response": assistant_response,
            "chat_history": updated_history,
            "session_id": self.session_id,
            "tool_calls": tool_calls_info if tool_calls_info else None,
            "tool_results": tool_results_info if tool_results_info else None,
        }

    def get_available_tools(self) -> List[str]:
        """Get list of tools available for this role."""
        return self.allowed_tool_names

    def get_role_info(self) -> Dict[str, Any]:
        """Get information about the current agent configuration."""
        return {
            "role": self.user_role,
            "employee_id": self.employee_id,
            "employee_name": self.employee_name,
            "available_tools": self.allowed_tool_names,
            "tool_count": len(self.allowed_tool_names),
            "session_id": self.session_id,
        }
    
    def get_session_history(self) -> List[ConversationMessage]:
        """Get chat history for this session."""
        return _session_memory.get_session_history(self.session_id)
    
    def get_session_info(self) -> Optional[Dict[str, Any]]:
        """Get session metadata."""
        return _session_memory.get_session_info(self.session_id)
    
    def clear_session(self) -> None:
        """Clear the current session."""
        _session_memory.clear_session(self.session_id)
    
    @staticmethod
    def get_all_sessions() -> Dict[str, Dict[str, Any]]:
        """Get all active sessions (static method)."""
        return _session_memory.get_all_sessions()


# ============================================================================
# MAIN AGENT EXECUTION
# ============================================================================

async def main():
    """
    Example usage of the role-based travel agent.
    
    Demonstrates how to use the agent with different roles and employee contexts.
    """
    
    # Example 1: Employee creating a travel request
    print("=" * 80)
    print("EXAMPLE 1: Employee Creating Travel Request")
    print("=" * 80)
    
    employee_agent = RoleBasedTravelAgent(
        user_role="employee",
        employee_id="EMP001",
        employee_name="John Doe",
        employee_info={
            "department": "Engineering",
            "designation": "Senior Engineer",
            "location": "New Delhi"
        }
    )
    
    print(f"\nAgent Config: {employee_agent.get_role_info()}\n")
    
    employee_message = "I need to travel from Delhi to New York next month for a client meeting. Can you help me plan the trip?"
    print(f"User (Employee): {employee_message}\n")
    
    response = await employee_agent.process_message(employee_message)
    print(f"Agent Response: {response}\n")
    
    # Example 2: Manager approving a travel request
    print("\n" + "=" * 80)
    print("EXAMPLE 2: SRM Approving Travel Request")
    print("=" * 80)
    
    srm_agent = RoleBasedTravelAgent(user_role="srm")
    
    print(f"\nAgent Config: {srm_agent.get_role_info()}\n")
    
    srm_message = "Get the status of TRF TRF202500001 so I can review it for approval"
    print(f"User (SRM): {srm_message}\n")
    
    response = await srm_agent.process_message(srm_message)
    print(f"Agent Response: {response}\n")
    
    # Example 3: Travel desk planning travel
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Travel Desk Planning Travel")
    print("=" * 80)
    
    travel_desk_agent = RoleBasedTravelAgent(user_role="travel_desk")
    
    print(f"\nAgent Config: {travel_desk_agent.get_role_info()}\n")
    
    travel_desk_message = "I need to search for flights from Mumbai to Singapore on December 15th in business class"
    print(f"User (Travel Desk): {travel_desk_message}\n")
    
    response = await travel_desk_agent.process_message(travel_desk_message)
    print(f"Agent Response: {response}\n")
    
    # Example 4: CFO approving high-value request
    print("\n" + "=" * 80)
    print("EXAMPLE 4: CFO Reviewing Travel Request")
    print("=" * 80)
    
    cfo_agent = RoleBasedTravelAgent(user_role="cfo")
    
    print(f"\nAgent Config: {cfo_agent.get_role_info()}\n")
    
    cfo_message = "Check the status of travel requisition TRF202500002 for budget review"
    print(f"User (CFO): {cfo_message}\n")
    
    response = await cfo_agent.process_message(cfo_message)
    print(f"Agent Response: {response}\n")


if __name__ == "__main__":
    asyncio.run(main())
