"""
Database Utility Functions for Corporate Travel Management System
PostgreSQL NeonDB Version with Pydantic Models and LangChain Tools
Uses schemas.py for type validation
"""

from sqlalchemy import create_engine, and_, or_, func
from sqlalchemy.orm import sessionmaker, Session
from models import *
from agent.schema import *
from src.rag.retrieval.policy_qa import get_policy_qa
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from langchain_core.tools import tool
import json
from dotenv import load_dotenv

# Ensure values from .env land in os.environ for downstream libraries
load_dotenv()
import os
# PostgreSQL NeonDB Connection
DATABASE_URL = os.getenv("DATABASE_URL")


# ============================================================================
# DATABASE SESSION MANAGEMENT
# ============================================================================

def get_session() -> Session:
    """Get database session"""
    engine = create_engine(DATABASE_URL, echo=False)
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()


# ============================================================================
# LANGCHAIN TOOLS - TRF OPERATIONS
# ============================================================================

@tool(args_schema=TRFDraftInput)
def create_trf_draft(
    employee_id: str,
    employee_name: str,
    employee_email: str,
    travel_type: str,
    purpose: str,
    origin_city: str,
    destination_city: str,
    departure_date: str,
    return_date: Optional[str] = None,
    estimated_cost: Optional[float] = None,
    employee_phone: Optional[str] = None,
    employee_department: Optional[str] = None,
    employee_designation: Optional[str] = None,
    employee_location: Optional[str] = None,
    irm_name: Optional[str] = None,
    irm_email: Optional[str] = None,
    srm_name: Optional[str] = None,
    srm_email: Optional[str] = None
) -> str:
    """
    Create a draft TRF (Travel Requisition Form) that can be edited later.
    Draft TRFs are saved with DRAFT status and not submitted for approval.
    User can continue editing or submit later using submit_trf().
    
    Use this tool when user wants to:
    - Start a travel request
    - Save travel details for later
    - Create a travel plan without submitting
    
    Example: "Create a draft travel request for my trip to New York"
    """
    session = get_session()
    
    try:
        try:
            dep = datetime.strptime(departure_date, "%Y-%m-%d").date()
            ret = datetime.strptime(return_date, "%Y-%m-%d").date() if return_date else None
        except ValueError:
            return TRFDraftOutput(
                success=False,
                message="Invalid date format. Please use YYYY-MM-DD.",
                error=ErrorCodes.INVALID_DATE_FORMAT,
                error_details="departure_date/return_date failed strict ISO parsing."
            ).model_dump_json()
        
        if ret and ret <= dep:
            return TRFDraftOutput(
                success=False,
                message="Return date must be after departure date",
                error=ErrorCodes.INVALID_DATE_RANGE,
                error_details="return_date must be greater than departure_date"
            ).model_dump_json()
        
        count = session.query(func.count(TravelRequisitionForm.id)).scalar()
        trf_num = f"DRAFT-TRF{datetime.now().year}{count+1:05d}"
        
        trf = TravelRequisitionForm(
            trf_number=trf_num,
            employee_id=employee_id,
            employee_name=employee_name,
            employee_email=employee_email,
            employee_phone=employee_phone,
            employee_department=employee_department,
            employee_designation=employee_designation,
            employee_location=employee_location,
            irm_name=irm_name,
            irm_email=irm_email,
            srm_name=srm_name,
            srm_email=srm_email,
            travel_type=TravelType.DOMESTIC if travel_type.lower() == "domestic" else TravelType.INTERNATIONAL,
            purpose=purpose,
            origin_city=origin_city,
            destination_city=destination_city,
            departure_date=dep,
            return_date=ret,
            estimated_cost=estimated_cost,
            status=TRFStatus.DRAFT
        )
        
        session.add(trf)
        session.commit()
        
        data = TRFDraftData(
            trf_number=trf_num,
            status=TRFStatusValues.DRAFT,
            employee_name=employee_name,
            travel=f"{origin_city} to {destination_city}",
            departure=departure_date,
            next_steps=[
                "Edit: Update any details before submission",
                f"Submit: Use submit_trf('{trf_num}') when ready",
                f"View: Use list_employee_drafts('{employee_id}') to see all drafts"
            ]
        )
        return TRFDraftOutput(
            success=True,
            message=f"Draft TRF created successfully: {trf_num}",
            data=data
        ).model_dump_json()
        
    except Exception as e:
        session.rollback()
        return TRFDraftOutput(
            success=False,
            message=str(e),
            error=ErrorCodes.SYSTEM_ERROR,
            error_details=str(e)
        ).model_dump_json()
    finally:
        session.close()


@tool(args_schema=TRFSubmitInput)
def submit_trf(trf_number: str) -> str:
    """
    Submit a draft TRF for approval. Changes status from DRAFT to PENDING_IRM.
    Once submitted, TRF enters the approval workflow starting with IRM.
    
    Use this tool when user wants to:
    - Submit a draft TRF for approval
    - Start the approval process
    - Finalize a draft
    
    Example: "Submit my draft TRF for approval"
    """
    session = get_session()
    
    try:
        trf = session.query(TravelRequisitionForm).filter_by(trf_number=trf_number).first()
        
        if not trf:
            return TRFSubmitOutput(
                success=False,
                message=f"TRF {trf_number} not found",
                error=ErrorCodes.TRF_NOT_FOUND,
                error_details="No draft TRF matched the provided number."
            ).model_dump_json()
        
        if trf.status != TRFStatus.DRAFT:
            return TRFSubmitOutput(
                success=False,
                message=f"Cannot submit, current status: {trf.status.value}",
                error=ErrorCodes.INVALID_STATUS,
                error_details=f"Expected DRAFT but found {trf.status.value}."
            ).model_dump_json()
        
        new_num = trf_number.replace("DRAFT-", "")
        trf.trf_number = new_num
        trf.status = TRFStatus.PENDING_IRM
        session.commit()
        
        data = TRFSubmitData(
            trf_number=new_num,
            previous_number=trf_number,
            status=TRFStatusValues.PENDING_IRM,
            submitted_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            next_steps=[
                "TRF is now pending IRM approval",
                f"Track status: get_trf_status('{new_num}')"
            ]
        )
        return TRFSubmitOutput(
            success=True,
            message=f"TRF submitted successfully: {new_num}",
            data=data
        ).model_dump_json()
        
    except Exception as e:
        session.rollback()
        return TRFSubmitOutput(
            success=False,
            message=str(e),
            error=ErrorCodes.SYSTEM_ERROR,
            error_details=str(e)
        ).model_dump_json()
    finally:
        session.close()


@tool(args_schema=TRFListInput)
def list_employee_drafts(employee_id: str) -> str:
    """
    List all draft TRFs for an employee.
    Shows TRFs that are saved but not yet submitted.
    
    Use this tool when user wants to:
    - See their saved drafts
    - Continue working on a draft
    - Find a specific draft
    
    Example: "Show me my draft travel requests"
    """
    session = get_session()
    
    try:
        drafts = session.query(TravelRequisitionForm).filter_by(
            employee_id=employee_id,
            status=TRFStatus.DRAFT
        ).order_by(TravelRequisitionForm.updated_at.desc()).all()
        
        draft_list = [
            TRFDraftSummary(
                trf_number=d.trf_number,
                travel=f"{d.origin_city} to {d.destination_city}",
                departure=str(d.departure_date),
                return_date=str(d.return_date) if d.return_date else None,
                purpose=d.purpose[:100],
                created=d.created_at.strftime("%Y-%m-%d"),
                last_updated=d.updated_at.strftime("%Y-%m-%d")
            )
            for d in drafts
        ]
        data = TRFListData(employee_id=employee_id, total=len(draft_list), drafts=draft_list)
        return TRFListOutput(
            success=True,
            message=f"Found {len(drafts)} draft(s)",
            data=data
        ).model_dump_json()
        
    except Exception as e:
        return TRFListOutput(
            success=False,
            message="Unable to fetch draft TRFs",
            error=ErrorCodes.SYSTEM_ERROR,
            error_details=str(e)
        ).model_dump_json()
    finally:
        session.close()


@tool(args_schema=TRFStatusInput)
def get_trf_status(trf_number: str) -> str:
    """
    Get detailed status of a TRF including complete approval history.
    Shows who approved, when, and any comments.
    
    Use this tool when user wants to:
    - Check TRF status
    - See approval progress
    - View approval history
    - Find rejection reason
    
    Example: "What's the status of my TRF?"
    """
    session = get_session()
    
    try:
        trf = session.query(TravelRequisitionForm).filter_by(trf_number=trf_number).first()
        
        if not trf:
            return TRFStatusOutput(
                success=False,
                message=f"TRF {trf_number} not found",
                error=ErrorCodes.TRF_NOT_FOUND,
                error_details="No TRF matched the provided identifier."
            ).model_dump_json()
        
        approvals: List[ApprovalInfo] = []
        if trf.irm_approved_at:
            approvals.append(ApprovalInfo(role="IRM", status="APPROVED", at=str(trf.irm_approved_at), comments=trf.irm_comments))
        if trf.srm_approved_at:
            approvals.append(ApprovalInfo(role="SRM", status="APPROVED", at=str(trf.srm_approved_at), comments=trf.srm_comments))
        if trf.buh_approved_at:
            approvals.append(ApprovalInfo(role="BUH", status="APPROVED", at=str(trf.buh_approved_at), comments=trf.buh_comments))
        if trf.ssuh_approved_at:
            approvals.append(ApprovalInfo(role="SSUH", status="APPROVED", at=str(trf.ssuh_approved_at), comments=trf.ssuh_comments))
        if trf.bgh_approved_at:
            approvals.append(ApprovalInfo(role="BGH", status="APPROVED", at=str(trf.bgh_approved_at), comments=trf.bgh_comments))
        if trf.ssgh_approved_at:
            approvals.append(ApprovalInfo(role="SSGH", status="APPROVED", at=str(trf.ssgh_approved_at), comments=trf.ssgh_comments))
        if trf.cfo_approved_at:
            approvals.append(ApprovalInfo(role="CFO", status="APPROVED", at=str(trf.cfo_approved_at), comments=trf.cfo_comments))
        if trf.travel_desk_approved_at:
            approvals.append(ApprovalInfo(role="Travel Desk", status="APPROVED", at=str(trf.travel_desk_approved_at), comments=trf.travel_desk_comments))
        
        booking_summaries: List[Dict[str, Any]] = []
        for booking in trf.travel_bookings:
            hotel_details = []
            for hotel_booking in booking.hotel_bookings:
                room = hotel_booking.room
                hotel_name = room.hotel.name if room and room.hotel else None
                hotel_details.append({
                    "confirmation_number": hotel_booking.confirmation_number,
                    "hotel_name": hotel_name,
                    "check_in": str(hotel_booking.check_in_date),
                    "check_out": str(hotel_booking.check_out_date),
                    "final_cost": hotel_booking.final_cost
                })

            flight_details = []
            for flight_booking in booking.flight_bookings:
                flight = flight_booking.flight
                flight_details.append({
                    "pnr": flight_booking.pnr,
                    "flight_number": flight.flight_number if flight else None,
                    "cabin_class": flight_booking.cabin_class.value if flight_booking.cabin_class else None,
                    "departure_date": str(flight.departure_date) if flight else None,
                    "origin_city": flight.origin_city if flight else None,
                    "destination_city": flight.destination_city if flight else None,
                    "final_fare": flight_booking.final_fare
                })
            booking_summaries.append({
                "booking_number": booking.booking_number,
                "status": booking.status.value if booking.status else BookingStatus.PENDING.value,
                "total_cost": booking.total_cost,
                "total_hotel_cost": booking.total_hotel_cost,
                "total_flight_cost": booking.total_flight_cost,
                "confirmed_hotels": hotel_details,
                "confirmed_flights": flight_details,
                "booked_at": booking.booking_date.strftime("%Y-%m-%d %H:%M:%S") if booking.booking_date else None,
                "confirmed_at": booking.confirmation_date.strftime("%Y-%m-%d %H:%M:%S") if booking.confirmation_date else None
            })
        
        data = TRFStatusData(
            trf_number=trf_number,
            status=trf.status.value,
            employee=trf.employee_name,
            travel=f"{trf.origin_city} to {trf.destination_city}",
            departure=str(trf.departure_date),
            approvals=approvals,
            rejection_reason=trf.rejection_reason,
            created=trf.created_at.strftime("%Y-%m-%d"),
            travel_bookings=booking_summaries
        )
        
        return TRFStatusOutput(
            success=True,
            message="TRF status retrieved",
            data=data
        ).model_dump_json()
        
    except Exception as e:
        return TRFStatusOutput(
            success=False,
            message="Unable to fetch TRF status",
            error=ErrorCodes.SYSTEM_ERROR,
            error_details=str(e)
        ).model_dump_json()
    finally:
        session.close()


@tool(args_schema=EmployeeTRFListInput)
def list_employee_trfs(employee_id: str, status_filter: Optional[str] = None) -> str:
    """
    List all TRFs for an employee with optional status filter.
    Shows complete travel history.
    
    Use this tool when user wants to:
    - See all their travel requests
    - Filter by status
    - View travel history
    
    Example: "Show me all my pending travel requests"
    """
    session = get_session()
    
    try:
        query = session.query(TravelRequisitionForm).filter_by(employee_id=employee_id)
        
        if status_filter:
            if status_filter.lower() == "pending":
                query = query.filter(TravelRequisitionForm.status.in_([
                    TRFStatus.PENDING_IRM, TRFStatus.PENDING_SRM, TRFStatus.PENDING_BUH,
                    TRFStatus.PENDING_SSUH, TRFStatus.PENDING_BGH, TRFStatus.PENDING_SSGH,
                    TRFStatus.PENDING_CFO, TRFStatus.PENDING_TRAVEL_DESK
                ]))
            elif status_filter.lower() != "all":
                try:
                    query = query.filter(TravelRequisitionForm.status == TRFStatus[status_filter.upper()])
                except KeyError:
                    pass
        
        trfs = query.order_by(TravelRequisitionForm.created_at.desc()).all()
        
        trf_list = [
            EmployeeTRFSummary(
                trf_number=t.trf_number,
                status=t.status.value,
                travel=f"{t.origin_city} to {t.destination_city}",
                departure=str(t.departure_date),
                purpose=t.purpose[:80],
                created=t.created_at.strftime("%Y-%m-%d")
            )
            for t in trfs
        ]
        data = EmployeeTRFListData(
            employee_id=employee_id,
            total=len(trf_list),
            filter=status_filter or "all",
            trfs=trf_list
        )
        
        return EmployeeTRFListOutput(
            success=True,
            message=f"Found {len(trfs)} TRF(s)",
            data=data
        ).model_dump_json()
        
    except Exception as e:
        return EmployeeTRFListOutput(
            success=False,
            message="Unable to fetch TRF list",
            error=ErrorCodes.SYSTEM_ERROR,
            error_details=str(e)
        ).model_dump_json()
    finally:
        session.close()


# ============================================================================
# LANGCHAIN TOOLS - APPROVAL OPERATIONS
# ============================================================================

@tool(args_schema=TRFApprovalContextInput)
def get_trf_approval_details(trf_number: str) -> str:
    """
    Retrieve TRF details with context to determine the next approval level automatically.
    This tool should be called BEFORE approve_trf() so the LLM is contextually aware
    of the TRF's current status and can determine the correct approval level.
    
    Returns:
    - Current status of the TRF
    - Next approval level that should review it
    - Complete travel details (employee, dates, cost, purpose)
    - Approval chain history (who already approved)
    
    Use this tool when:
    - Manager wants to approve a TRF but doesn't know what level to approve at
    - Need to see TRF details before making approval decision
    - Want to understand the approval workflow state
    
    Example workflow:
    1. User: "approve TRF202500002"
    2. Agent calls: get_trf_approval_details('TRF202500002')
    3. Agent receives: "TRF is pending CFO approval, you are CFO so you can approve it now"
    4. Agent calls: approve_trf('TRF202500002', 'cfo', comments='Looks good')
    
    This ensures the LLM is always contextually aware before taking approval actions.
    """
    session = get_session()
    
    try:
        trf = session.query(TravelRequisitionForm).filter_by(trf_number=trf_number).first()
        
        if not trf:
            return TRFApprovalContextOutput(
                success=False,
                message=f"TRF {trf_number} not found",
                error=ErrorCodes.TRF_NOT_FOUND,
                error_details="No TRF matched the provided identifier."
            ).model_dump_json()
        
        # Determine next approval level based on current status
        status_to_level = {
            TRFStatus.PENDING_IRM: "irm",
            TRFStatus.PENDING_SRM: "srm",
            TRFStatus.PENDING_BUH: "buh",
            TRFStatus.PENDING_SSUH: "ssuh",
            TRFStatus.PENDING_BGH: "bgh",
            TRFStatus.PENDING_SSGH: "ssgh",
            TRFStatus.PENDING_CFO: "cfo",
            TRFStatus.PENDING_TRAVEL_DESK: "travel_desk",
        }
        
        next_level = status_to_level.get(trf.status, None)
        
        if not next_level:
            return TRFApprovalContextOutput(
                success=False,
                message=f"TRF is in {trf.status.value} status - cannot be approved",
                error=ErrorCodes.INVALID_STATUS,
                error_details=f"Only TRFs in PENDING status can be approved. Current: {trf.status.value}"
            ).model_dump_json()
        
        data = TRFApprovalContextInfo(
            trf_number=trf_number,
            current_status=trf.status.value,
            next_approval_level=next_level,
            employee_name=trf.employee_name,
            employee_id=trf.employee_id,
            travel_type=trf.travel_type.value if trf.travel_type else None,
            origin_city=trf.origin_city,
            destination_city=trf.destination_city,
            departure_date=str(trf.departure_date) if trf.departure_date else None,
            return_date=str(trf.return_date) if trf.return_date else None,
            purpose=trf.purpose,
            estimated_cost=trf.estimated_cost,
            irm_approved="Yes" if trf.irm_approved_at else "No",
            irm_approved_at=trf.irm_approved_at.strftime("%Y-%m-%d %H:%M") if trf.irm_approved_at else None,
            irm_comments=trf.irm_comments,
            srm_approved="Yes" if trf.srm_approved_at else "No",
            srm_approved_at=trf.srm_approved_at.strftime("%Y-%m-%d %H:%M") if trf.srm_approved_at else None,
            buh_approved="Yes" if trf.buh_approved_at else "No",
            buh_approved_at=trf.buh_approved_at.strftime("%Y-%m-%d %H:%M") if trf.buh_approved_at else None,
            ssuh_approved="Yes" if trf.ssuh_approved_at else "No",
            ssuh_approved_at=trf.ssuh_approved_at.strftime("%Y-%m-%d %H:%M") if trf.ssuh_approved_at else None,
            bgh_approved="Yes" if trf.bgh_approved_at else "No",
            bgh_approved_at=trf.bgh_approved_at.strftime("%Y-%m-%d %H:%M") if trf.bgh_approved_at else None,
            ssgh_approved="Yes" if trf.ssgh_approved_at else "No",
            ssgh_approved_at=trf.ssgh_approved_at.strftime("%Y-%m-%d %H:%M") if trf.ssgh_approved_at else None,
            cfo_approved="Yes" if trf.cfo_approved_at else "No",
            cfo_approved_at=trf.cfo_approved_at.strftime("%Y-%m-%d %H:%M") if trf.cfo_approved_at else None,
            travel_desk_approved="Yes" if trf.travel_desk_approved_at else "No"
        )
        
        return TRFApprovalContextOutput(
            success=True,
            message=f"TRF {trf_number} is pending {next_level.upper()} approval",
            data=data
        ).model_dump_json()
        
    except Exception as e:
        return TRFApprovalContextOutput(
            success=False,
            message="Unable to fetch TRF approval details",
            error=ErrorCodes.SYSTEM_ERROR,
            error_details=str(e)
        ).model_dump_json()
    finally:
        session.close()


@tool(args_schema=TRFApprovalInput)
def approve_trf(
    trf_number: str,
    approver_level: str,
    comments: Optional[str] = None,
    require_cfo: bool = False
) -> str:
    """
    Approve a TRF at the specified approval level.
    Moves TRF to next stage in approval workflow.
    
    ⚠️  WORKFLOW: Always call get_trf_approval_details(trf_number) FIRST
    This ensures you know:
    - Current TRF status
    - What approval level is needed next (auto-detected)
    - Complete travel details for context
    - Approval chain history
    
    Then call this tool with the approver_level returned from get_trf_approval_details().
    
    Use this tool when manager wants to:
    - Approve a travel request
    - Move TRF forward in workflow
    - Add approval comments
    
    Example workflow:
    1. get_trf_approval_details('TRF202500002') -> Returns: "pending CFO approval"
    2. approve_trf('TRF202500002', 'cfo', 'Approved for travel')
    """
    session = get_session()
    
    try:
        trf = session.query(TravelRequisitionForm).filter_by(trf_number=trf_number).first()
        
        if not trf:
            return TRFApprovalOutput(
                success=False,
                message=f"TRF {trf_number} not found",
                error=ErrorCodes.TRF_NOT_FOUND,
                error_details="Approval attempted on missing TRF."
            ).model_dump_json()
        
        level = approver_level.lower()
        now = datetime.now()
        
        # ✅ CORRECTED: Proper workflow status progression
        # Each approval moves TRF to the NEXT pending status in the chain
        # CFO approval (final approver) → moves to PENDING_TRAVEL_DESK (not APPROVED)
        # Travel Desk approval (booking phase) → moves to COMPLETED
        status_map = {
            "irm": (TRFStatus.PENDING_IRM, TRFStatus.PENDING_SRM),
            "srm": (TRFStatus.PENDING_SRM, TRFStatus.PENDING_BUH),
            "buh": (TRFStatus.PENDING_BUH, TRFStatus.PENDING_SSUH),
            "ssuh": (TRFStatus.PENDING_SSUH, TRFStatus.PENDING_BGH),
            "bgh": (TRFStatus.PENDING_BGH, TRFStatus.PENDING_SSGH),
            "ssgh": (TRFStatus.PENDING_SSGH, TRFStatus.PENDING_CFO),
            "cfo": (TRFStatus.PENDING_CFO, TRFStatus.PENDING_TRAVEL_DESK),  # CFO → Travel Desk queue
            "travel_desk": (TRFStatus.PENDING_TRAVEL_DESK, TRFStatus.COMPLETED)  # Travel Desk → Complete
        }
        
        if level not in status_map:
            return TRFApprovalOutput(
                success=False,
                message=f"Invalid level: {level}",
                error=ErrorCodes.INVALID_LEVEL,
                error_details="Valid levels are irm, srm, buh, ssuh, bgh, ssgh, cfo, travel_desk."
            ).model_dump_json()
        
        expected, next_status = status_map[level]
        if trf.status != expected:
            return TRFApprovalOutput(
                success=False,
                message=f"Wrong status: {trf.status.value}, expected: {expected.value}",
                error=ErrorCodes.INVALID_SEQUENCE,
                error_details=f"TRF must be in {expected.value} before approving at {level}. "
                              f"This TRF is currently {trf.status.value} and waiting for the next approver."
            ).model_dump_json()
        
        # ✅ Update approval status and comments based on approver level
        # Each approver records their approval timestamp and comments
        if level == "irm":
            trf.irm_approved_at = now
            trf.irm_comments = comments
        elif level == "srm":
            trf.srm_approved_at = now
            trf.srm_comments = comments
        elif level == "buh":
            trf.buh_approved_at = now
            trf.buh_comments = comments
        elif level == "ssuh":
            trf.ssuh_approved_at = now
            trf.ssuh_comments = comments
        elif level == "bgh":
            trf.bgh_approved_at = now
            trf.bgh_comments = comments
        elif level == "ssgh":
            trf.ssgh_approved_at = now
            trf.ssgh_comments = comments
        elif level == "cfo":
            trf.cfo_approved_at = now
            trf.cfo_comments = comments
            # CFO is final financial approver, but Travel Desk still needs to complete booking
        elif level == "travel_desk":
            trf.travel_desk_approved_at = now
            trf.travel_desk_comments = comments
            # ✅ ONLY set final_approved_at when Travel Desk completes (marking entire process complete)
            trf.final_approved_at = now
        
        # ✅ Move to next status in approval chain
        # This ensures workflow progression: PENDING_X → PENDING_Y → ... → COMPLETED
        trf.status = next_status
        session.commit()
        
        # ✅ Include context in response showing what was approved and workflow progression
        data = TRFApprovalData(
            trf_number=trf_number,
            new_status=trf.status.value,
            approved_at=now.strftime("%Y-%m-%d %H:%M:%S"),
            travel_type=trf.travel_type.value if trf.travel_type else None,
            employee_name=trf.employee_name,
            origin_city=trf.origin_city,
            destination_city=trf.destination_city,
            departure_date=str(trf.departure_date) if trf.departure_date else None,
            purpose=trf.purpose,
            estimated_cost=trf.estimated_cost
        )
        
        # ✅ Provide clear message about workflow progression
        progression_messages = {
            "irm": "TRF approved by IRM, now pending SRM review",
            "srm": "TRF approved by SRM, now pending BUH review",
            "buh": "TRF approved by BUH, now pending SSUH review",
            "ssuh": "TRF approved by SSUH, now pending BGH review",
            "bgh": "TRF approved by BGH, now pending SSGH review",
            "ssgh": "TRF approved by SSGH, now pending CFO review",
            "cfo": "TRF approved by CFO - Ready for Travel Desk to book flights & hotels",
            "travel_desk": "✅ Travel Desk approval complete - All bookings confirmed, travel COMPLETED"
        }
        
        workflow_message = progression_messages.get(level, f"TRF approved at {level.upper()} level")
        
        return TRFApprovalOutput(
            success=True,
            message=workflow_message,
            data=data
        ).model_dump_json()
        
    except Exception as e:
        session.rollback()
        return TRFApprovalOutput(
            success=False,
            message=str(e),
            error=ErrorCodes.SYSTEM_ERROR,
            error_details=str(e)
        ).model_dump_json()
    finally:
        session.close()


@tool(args_schema=TRFRejectionInput)
def reject_trf(trf_number: str, approver_level: str, rejection_reason: str) -> str:
    """
    Reject a TRF at specified approval level with mandatory reason.
    Rejection reason must be at least 10 characters for audit trail.
    
    IMPORTANT: This tool automatically fetches complete TRF details from the database
    including travel type (domestic/international), employee info, dates, etc.
    You don't need to ask about these - they're all included in the response.
    
    Use this tool when:
    - Manager needs to reject a travel request
    - Provide rejection reason (minimum 10 characters)
    - Record why the TRF was rejected
    """
    session = get_session()
    
    try:
        if len(rejection_reason) < 10:
            return TRFRejectionOutput(
                success=False,
                message="Rejection reason must be at least 10 characters",
                error=ErrorCodes.INVALID_REASON,
                error_details="Provided reason length is below the minimum threshold."
            ).model_dump_json()
        
        trf = session.query(TravelRequisitionForm).filter_by(trf_number=trf_number).first()
        
        if not trf:
            return TRFRejectionOutput(
                success=False,
                message=f"TRF {trf_number} not found",
                error=ErrorCodes.TRF_NOT_FOUND,
                error_details="Cannot reject a TRF that does not exist."
            ).model_dump_json()
        
        trf.status = TRFStatus.REJECTED
        trf.rejection_reason = f"[{approver_level.upper()}] {rejection_reason}"
        trf.rejected_by = approver_level.lower()
        session.commit()
        
        # ✅ NEW: Include application context in response so approver knows what they rejected
        data = TRFRejectionData(
            trf_number=trf_number,
            status=TRFStatusValues.REJECTED,
            reason=rejection_reason,
            travel_type=trf.travel_type.value if trf.travel_type else None,
            employee_name=trf.employee_name,
            origin_city=trf.origin_city,
            destination_city=trf.destination_city,
            departure_date=str(trf.departure_date) if trf.departure_date else None
        )
        
        return TRFRejectionOutput(
            success=True,
            message=f"TRF rejected at {approver_level.upper()} level",
            data=data
        ).model_dump_json()
        
    except Exception as e:
        session.rollback()
        return TRFRejectionOutput(
            success=False,
            message=str(e),
            error=ErrorCodes.SYSTEM_ERROR,
            error_details=str(e)
        ).model_dump_json()
    finally:
        session.close()





# ============================================================================
# LANGCHAIN TOOLS - ROLE-SPECIFIC PENDING APPLICATIONS
# ============================================================================

@tool(args_schema=BaseToolInput)
def get_pending_irm_applications() -> str:
    """
    Get all TRFs pending IRM approval.
    Shows TRFs that have been submitted but not yet approved by IRM.
    
    Use this tool when:
    - IRM wants to see pending applications
    - Review what needs approval
    - Check approval queue
    
    Example: "Show me my pending applications"
    """
    session = get_session()
    
    try:
        trfs = session.query(TravelRequisitionForm).filter_by(
            status=TRFStatus.PENDING_IRM
        ).order_by(TravelRequisitionForm.created_at.desc()).all()
        
        trf_list = [
            {
                "trf_number": t.trf_number,
                "employee_name": t.employee_name,
                "employee_id": t.employee_id,
                "travel": f"{t.origin_city} to {t.destination_city}",
                "departure_date": str(t.departure_date),
                "estimated_cost": t.estimated_cost,
                "purpose": t.purpose[:100],
                "created": t.created_at.strftime("%Y-%m-%d %H:%M"),
                "days_pending": (datetime.now() - t.created_at).days
            }
            for t in trfs
        ]
        
        data = PendingApplicationsData(
            role="IRM",
            total_pending=len(trf_list),
            applications=trf_list,
            message=f"Found {len(trf_list)} pending application(s) awaiting your approval"
        )
        
        return PendingApplicationsOutput(
            success=True,
            message=f"Found {len(trf_list)} pending application(s) for IRM",
            data=data
        ).model_dump_json()
        
    except Exception as e:
        return PendingApplicationsOutput(
            success=False,
            message=str(e),
            error=ErrorCodes.SYSTEM_ERROR,
            error_details=str(e)
        ).model_dump_json()
    finally:
        session.close()


@tool(args_schema=BaseToolInput)
def get_pending_srm_applications() -> str:
    """
    Get all TRFs pending SRM approval (after IRM approval).
    Shows TRFs that have been approved by IRM but need SRM review.
    
    Use this tool when:
    - SRM wants to see pending applications
    - Review what needs approval
    - Check approval queue
    
    Example: "Show me my pending applications"
    """
    session = get_session()
    
    try:
        trfs = session.query(TravelRequisitionForm).filter_by(
            status=TRFStatus.PENDING_SRM
        ).order_by(TravelRequisitionForm.created_at.desc()).all()
        
        trf_list = [
            {
                "trf_number": t.trf_number,
                "employee_name": t.employee_name,
                "employee_id": t.employee_id,
                "travel": f"{t.origin_city} to {t.destination_city}",
                "departure_date": str(t.departure_date),
                "estimated_cost": t.estimated_cost,
                "purpose": t.purpose[:100],
                "irm_approved": "Yes" if t.irm_approved_at else "No",
                "irm_comments": t.irm_comments or "No comments",
                "created": t.created_at.strftime("%Y-%m-%d %H:%M"),
                "days_pending": (datetime.now() - t.created_at).days
            }
            for t in trfs
        ]
        
        data = PendingApplicationsData(
            role="SRM",
            total_pending=len(trf_list),
            applications=trf_list,
            message=f"Found {len(trf_list)} pending application(s) awaiting your approval"
        )
        
        return PendingApplicationsOutput(
            success=True,
            message=f"Found {len(trf_list)} pending application(s) for SRM",
            data=data
        ).model_dump_json()
        
    except Exception as e:
        return PendingApplicationsOutput(
            success=False,
            message=str(e),
            error=ErrorCodes.SYSTEM_ERROR,
            error_details=str(e)
        ).model_dump_json()
    finally:
        session.close()


@tool(args_schema=BaseToolInput)
def get_pending_buh_applications() -> str:
    """
    Get all TRFs pending BUH approval (after IRM and SRM approval).
    """
    session = get_session()
    
    try:
        trfs = session.query(TravelRequisitionForm).filter_by(
            status=TRFStatus.PENDING_BUH
        ).order_by(TravelRequisitionForm.created_at.desc()).all()
        
        trf_list = [
            {
                "trf_number": t.trf_number,
                "employee_name": t.employee_name,
                "employee_id": t.employee_id,
                "travel": f"{t.origin_city} to {t.destination_city}",
                "departure_date": str(t.departure_date),
                "estimated_cost": t.estimated_cost,
                "purpose": t.purpose[:100],
                "irm_approved": "Yes" if t.irm_approved_at else "No",
                "srm_approved": "Yes" if t.srm_approved_at else "No",
                "created": t.created_at.strftime("%Y-%m-%d %H:%M"),
                "days_pending": (datetime.now() - t.created_at).days
            }
            for t in trfs
        ]
        
        data = PendingApplicationsData(
            role="BUH",
            total_pending=len(trf_list),
            applications=trf_list,
            message=f"Found {len(trf_list)} pending application(s) awaiting your approval"
        )
        
        return PendingApplicationsOutput(
            success=True,
            message=f"Found {len(trf_list)} pending application(s) for BUH",
            data=data
        ).model_dump_json()
        
    except Exception as e:
        return PendingApplicationsOutput(
            success=False,
            message=str(e),
            error=ErrorCodes.SYSTEM_ERROR,
            error_details=str(e)
        ).model_dump_json()
    finally:
        session.close()


@tool(args_schema=BaseToolInput)
def get_pending_ssuh_applications() -> str:
    """
    Get all TRFs pending SSUH approval (after BUH approval).
    """
    session = get_session()
    
    try:
        trfs = session.query(TravelRequisitionForm).filter_by(
            status=TRFStatus.PENDING_SSUH
        ).order_by(TravelRequisitionForm.created_at.desc()).all()
        
        trf_list = [
            {
                "trf_number": t.trf_number,
                "employee_name": t.employee_name,
                "employee_id": t.employee_id,
                "travel": f"{t.origin_city} to {t.destination_city}",
                "departure_date": str(t.departure_date),
                "estimated_cost": t.estimated_cost,
                "purpose": t.purpose[:100],
                "buh_approved": "Yes" if t.buh_approved_at else "No",
                "buh_comments": t.buh_comments or "No comments",
                "created": t.created_at.strftime("%Y-%m-%d %H:%M"),
                "days_pending": (datetime.now() - t.created_at).days
            }
            for t in trfs
        ]
        
        data = PendingApplicationsData(
            role="SSUH",
            total_pending=len(trf_list),
            applications=trf_list,
            message=f"Found {len(trf_list)} pending application(s) awaiting your approval"
        )
        
        return PendingApplicationsOutput(
            success=True,
            message=f"Found {len(trf_list)} pending application(s) for SSUH",
            data=data
        ).model_dump_json()
        
    except Exception as e:
        return PendingApplicationsOutput(
            success=False,
            message=str(e),
            error=ErrorCodes.SYSTEM_ERROR,
            error_details=str(e)
        ).model_dump_json()
    finally:
        session.close()


@tool(args_schema=BaseToolInput)
def get_pending_bgh_applications() -> str:
    """
    Get all TRFs pending BGH approval (after SSUH approval).
    """
    session = get_session()
    
    try:
        trfs = session.query(TravelRequisitionForm).filter_by(
            status=TRFStatus.PENDING_BGH
        ).order_by(TravelRequisitionForm.created_at.desc()).all()
        
        trf_list = [
            {
                "trf_number": t.trf_number,
                "employee_name": t.employee_name,
                "employee_id": t.employee_id,
                "travel": f"{t.origin_city} to {t.destination_city}",
                "departure_date": str(t.departure_date),
                "estimated_cost": t.estimated_cost,
                "purpose": t.purpose[:100],
                "ssuh_approved": "Yes" if t.ssuh_approved_at else "No",
                "created": t.created_at.strftime("%Y-%m-%d %H:%M"),
                "days_pending": (datetime.now() - t.created_at).days
            }
            for t in trfs
        ]
        
        data = PendingApplicationsData(
            role="BGH",
            total_pending=len(trf_list),
            applications=trf_list,
            message=f"Found {len(trf_list)} pending application(s) awaiting your approval"
        )
        
        return PendingApplicationsOutput(
            success=True,
            message=f"Found {len(trf_list)} pending application(s) for BGH",
            data=data
        ).model_dump_json()
        
    except Exception as e:
        return PendingApplicationsOutput(
            success=False,
            message=str(e),
            error=ErrorCodes.SYSTEM_ERROR,
            error_details=str(e)
        ).model_dump_json()
    finally:
        session.close()


@tool(args_schema=BaseToolInput)
def get_pending_ssgh_applications() -> str:
    """
    Get all TRFs pending SSGH approval (after BGH approval).
    """
    session = get_session()
    
    try:
        trfs = session.query(TravelRequisitionForm).filter_by(
            status=TRFStatus.PENDING_SSGH
        ).order_by(TravelRequisitionForm.created_at.desc()).all()
        
        trf_list = [
            {
                "trf_number": t.trf_number,
                "employee_name": t.employee_name,
                "employee_id": t.employee_id,
                "travel": f"{t.origin_city} to {t.destination_city}",
                "departure_date": str(t.departure_date),
                "estimated_cost": t.estimated_cost,
                "purpose": t.purpose[:100],
                "bgh_approved": "Yes" if t.bgh_approved_at else "No",
                "bgh_comments": t.bgh_comments or "No comments",
                "created": t.created_at.strftime("%Y-%m-%d %H:%M"),
                "days_pending": (datetime.now() - t.created_at).days
            }
            for t in trfs
        ]
        
        data = PendingApplicationsData(
            role="SSGH",
            total_pending=len(trf_list),
            applications=trf_list,
            message=f"Found {len(trf_list)} pending application(s) awaiting your approval"
        )
        
        return PendingApplicationsOutput(
            success=True,
            message=f"Found {len(trf_list)} pending application(s) for SSGH",
            data=data
        ).model_dump_json()
        
    except Exception as e:
        return PendingApplicationsOutput(
            success=False,
            message=str(e),
            error=ErrorCodes.SYSTEM_ERROR,
            error_details=str(e)
        ).model_dump_json()
    finally:
        session.close()


@tool(args_schema=BaseToolInput)
def get_pending_cfo_applications() -> str:
    """
    Get all TRFs pending CFO approval (after all lower-level approvals).
    """
    session = get_session()
    
    try:
        trfs = session.query(TravelRequisitionForm).filter_by(
            status=TRFStatus.PENDING_CFO
        ).order_by(TravelRequisitionForm.created_at.desc()).all()
        
        trf_list = [
            {
                "trf_number": t.trf_number,
                "employee_name": t.employee_name,
                "employee_id": t.employee_id,
                "travel": f"{t.origin_city} to {t.destination_city}",
                "departure_date": str(t.departure_date),
                "estimated_cost": t.estimated_cost,
                "purpose": t.purpose[:100],
                "ssgh_approved": "Yes" if t.ssgh_approved_at else "No",
                "ssgh_comments": t.ssgh_comments or "No comments",
                "created": t.created_at.strftime("%Y-%m-%d %H:%M"),
                "days_pending": (datetime.now() - t.created_at).days
            }
            for t in trfs
        ]
        
        data = PendingApplicationsData(
            role="CFO",
            total_pending=len(trf_list),
            applications=trf_list,
            message=f"Found {len(trf_list)} pending application(s) awaiting your approval"
        )
        
        return PendingApplicationsOutput(
            success=True,
            message=f"Found {len(trf_list)} pending application(s) for CFO",
            data=data
        ).model_dump_json()
        
    except Exception as e:
        return PendingApplicationsOutput(
            success=False,
            message=str(e),
            error=ErrorCodes.SYSTEM_ERROR,
            error_details=str(e)
        ).model_dump_json()
    finally:
        session.close()


@tool(args_schema=BaseToolInput)
def get_pending_travel_desk_applications() -> str:
    """
    Get all TRFs pending Travel Desk approval (after CFO approval).
    Shows all approved TRFs ready for Travel Desk to plan, search, and book.
    
    ⭐️ FIXED: Now correctly includes ALL approved TRFs, including those where
    travel_desk_approved_at is already set. This ensures no approved applications
    are missed even if they were previously approved by Travel Desk.
    
    Use this tool when:
    - Travel Desk wants to see pending approvals
    - Plan travel itineraries
    - Search for flights and hotels
    - Check what needs booking
    
    Example: "Show me my pending applications"
    """
    session = get_session()
    
    try:
        # Include TRFs that are:
        # 1. Pending Travel Desk status (awaiting travel desk approval)
        # 2. Processing status (being processed)
        # 3. APPROVED status (regardless of whether travel_desk_approved_at is set)
        #    - This catches applications that were approved but may not have bookings
        pending_statuses = [TRFStatus.PENDING_TRAVEL_DESK, TRFStatus.PROCESSING, TRFStatus.APPROVED]
        trfs = (
            session.query(TravelRequisitionForm)
            .filter(TravelRequisitionForm.status.in_(pending_statuses))
            .order_by(TravelRequisitionForm.created_at.desc())
            .all()
        )
        
        readiness_counts = {
            "pending_travel_desk": 0,
            "processing": 0,
            "legacy_cfo_approved": 0,
            "other": 0,
        }
        trf_list: List[TravelDeskApplicationInfo] = []
        
        for t in trfs:
            readiness_state = "pending_travel_desk"
            if t.status == TRFStatus.PROCESSING:
                readiness_state = "processing"
            elif t.status == TRFStatus.APPROVED and t.travel_desk_approved_at is None:
                readiness_state = "legacy_cfo_approved"
            elif t.status != TRFStatus.PENDING_TRAVEL_DESK:
                readiness_state = f"status_{t.status.value}"
            
            readiness_counts.setdefault(readiness_state, 0)
            readiness_counts[readiness_state] += 1
            
            trf_list.append(
                TravelDeskApplicationInfo(
                    trf_number=t.trf_number,
                    employee_name=t.employee_name,
                    employee_id=t.employee_id,
                    employee_email=t.employee_email,
                    travel=f"{t.origin_city} to {t.destination_city}",
                    travel_type=t.travel_type.value if t.travel_type else None,
                    departure_date=str(t.departure_date),
                    return_date=str(t.return_date) if t.return_date else None,
                    estimated_cost=t.estimated_cost,
                    purpose=t.purpose[:100],
                    current_status=t.status.value,
                    readiness_state=readiness_state,
                    all_approvals_complete="Yes",
                    cfo_approved="Yes" if t.cfo_approved_at else "No",
                    cfo_comments=t.cfo_comments or "No comments",
                    irm_approved="Yes" if t.irm_approved_at else "No",
                    srm_approved="Yes" if t.srm_approved_at else "No",
                    buh_approved="Yes" if t.buh_approved_at else "No",
                    ssuh_approved="Yes" if t.ssuh_approved_at else "No",
                    bgh_approved="Yes" if t.bgh_approved_at else "No",
                    ssgh_approved="Yes" if t.ssgh_approved_at else "No",
                    created=t.created_at.strftime("%Y-%m-%d %H:%M"),
                    days_pending=(datetime.now() - t.created_at).days
                )
            )
        
        summary_parts = []
        if readiness_counts.get("pending_travel_desk"):
            summary_parts.append(f"{readiness_counts['pending_travel_desk']} newly cleared by CFO")
        if readiness_counts.get("legacy_cfo_approved"):
            summary_parts.append(
                f"{readiness_counts['legacy_cfo_approved']} legacy APPROVED awaiting travel desk"
            )
        if readiness_counts.get("processing"):
            summary_parts.append(f"{readiness_counts['processing']} currently in processing")
        summary_detail = f" ({'; '.join(summary_parts)})" if summary_parts else ""
        
        data = TravelDeskPendingData(
            role="TRAVEL_DESK",
            total_pending=len(trf_list),
            applications=trf_list,
            message=(
                f"Found {len(trf_list)} application(s) ready for travel planning and booking"
                f"{summary_detail}"
            )
        )
        
        return TravelDeskPendingOutput(
            success=True,
            message=f"Found {len(trf_list)} application(s) ready for Travel Desk",
            data=data
        ).model_dump_json()
        
    except Exception as e:
        return TravelDeskPendingOutput(
            success=False,
            message=str(e),
            error=ErrorCodes.SYSTEM_ERROR,
            error_details=str(e)
        ).model_dump_json()
    finally:
        session.close()


# ============================================================================
# LANGCHAIN TOOLS - TRACK ALL APPLICATIONS (TRAVEL DESK)
# ============================================================================

@tool(args_schema=TrackAllApplicationsInput)
def track_all_applications() -> str:
    """
    Track all TRF applications (excluding drafts) for Travel Desk oversight.
    Shows complete information about every submitted application including
    travel details, employee info, current status, and entire approval chain history.
    
    Use this tool when Travel Desk wants to:
    - See all applications across all approval stages
    - Track application status and progress
    - Get comprehensive overview of all travel requests
    - Monitor approval workflow for all submissions
    - Access complete application details for any TRF
    - Monitor approval chain completeness
    - Get statistics on application distribution
    
    Returns:
    - List of all non-draft applications with full details
    - Status breakdown and approval statistics
    - Approval chain history for each application
    - Employee and travel information
    - Rejection tracking
    
    Example: "Show me all travel applications being tracked in the system"
    """
    session = get_session()
    
    try:
        # Get all non-draft TRFs, excluding drafts
        trfs = session.query(TravelRequisitionForm).filter(
            TravelRequisitionForm.status != TRFStatus.DRAFT
        ).order_by(TravelRequisitionForm.created_at.desc()).all()
        
        if not trfs:
            data = TrackAllApplicationsData(
                total_applications=0,
                draft_count=0,
                status_breakdown={},
                fully_approved=0,
                pending_approval=0,
                rejected_applications=0,
                completed_applications=0,
                applications=[],
                summary_message="No applications found. All TRFs are in draft status."
            )
            return TrackAllApplicationsOutput(
                success=True,
                message="No active applications to track",
                data=data
            ).model_dump_json()
        
        # Categorize applications
        status_breakdown = {}
        fully_approved_count = 0
        pending_approval_count = 0
        rejected_applications_count = 0
        completed_applications_count = 0
        
        applications_list = []
        
        for trf in trfs:
            # Build status breakdown
            status_val = trf.status.value
            status_breakdown[status_val] = status_breakdown.get(status_val, 0) + 1
            
            # Categorize by approval completion
            if trf.status == TRFStatus.REJECTED:
                rejected_applications_count += 1
            elif trf.status == TRFStatus.COMPLETED:
                completed_applications_count += 1
            elif trf.status == TRFStatus.APPROVED:
                fully_approved_count += 1
            elif trf.status == TRFStatus.PROCESSING:
                completed_applications_count += 1
            else:
                pending_approval_count += 1
            
            # Build detailed application info
            app_info = TrackAllApplicationsInfo(
                trf_number=trf.trf_number,
                employee_id=trf.employee_id,
                employee_name=trf.employee_name,
                employee_email=trf.employee_email,
                employee_designation=trf.employee_designation or "N/A",
                employee_department=trf.employee_department or "N/A",
                travel=f"{trf.origin_city} to {trf.destination_city}",
                travel_type=trf.travel_type.value if trf.travel_type else "N/A",
                departure_date=str(trf.departure_date),
                return_date=str(trf.return_date) if trf.return_date else None,
                estimated_cost=trf.estimated_cost,
                purpose=trf.purpose[:150],
                status=trf.status.value,
                
                # IRM Approval
                irm_approved="Yes" if trf.irm_approved_at else "No",
                irm_approved_at=trf.irm_approved_at.strftime("%Y-%m-%d %H:%M") if trf.irm_approved_at else None,
                irm_comments=trf.irm_comments,
                
                # SRM Approval
                srm_approved="Yes" if trf.srm_approved_at else "No",
                srm_approved_at=trf.srm_approved_at.strftime("%Y-%m-%d %H:%M") if trf.srm_approved_at else None,
                srm_comments=trf.srm_comments,
                
                # BUH Approval
                buh_approved="Yes" if trf.buh_approved_at else "No",
                buh_approved_at=trf.buh_approved_at.strftime("%Y-%m-%d %H:%M") if trf.buh_approved_at else None,
                buh_comments=trf.buh_comments,
                
                # SSUH Approval
                ssuh_approved="Yes" if trf.ssuh_approved_at else "No",
                ssuh_approved_at=trf.ssuh_approved_at.strftime("%Y-%m-%d %H:%M") if trf.ssuh_approved_at else None,
                ssuh_comments=trf.ssuh_comments,
                
                # BGH Approval
                bgh_approved="Yes" if trf.bgh_approved_at else "No",
                bgh_approved_at=trf.bgh_approved_at.strftime("%Y-%m-%d %H:%M") if trf.bgh_approved_at else None,
                bgh_comments=trf.bgh_comments,
                
                # SSGH Approval
                ssgh_approved="Yes" if trf.ssgh_approved_at else "No",
                ssgh_approved_at=trf.ssgh_approved_at.strftime("%Y-%m-%d %H:%M") if trf.ssgh_approved_at else None,
                ssgh_comments=trf.ssgh_comments,
                
                # CFO Approval
                cfo_approved="Yes" if trf.cfo_approved_at else "No",
                cfo_approved_at=trf.cfo_approved_at.strftime("%Y-%m-%d %H:%M") if trf.cfo_approved_at else None,
                cfo_comments=trf.cfo_comments,
                
                # Travel Desk Approval
                travel_desk_approved="Yes" if trf.travel_desk_approved_at else "No",
                travel_desk_approved_at=trf.travel_desk_approved_at.strftime("%Y-%m-%d %H:%M") if trf.travel_desk_approved_at else None,
                travel_desk_comments=trf.travel_desk_comments,
                
                # Metadata
                created=trf.created_at.strftime("%Y-%m-%d %H:%M"),
                updated=trf.updated_at.strftime("%Y-%m-%d %H:%M"),
                days_old=(datetime.now() - trf.created_at).days,
                rejection_reason=trf.rejection_reason,
                rejected_by=trf.rejected_by
            )
            applications_list.append(app_info)
        
        # Get draft count for reference
        draft_count = session.query(func.count(TravelRequisitionForm.id)).filter_by(
            status=TRFStatus.DRAFT
        ).scalar()
        
        # Build summary message
        total = len(trfs)
        summary_msg = f"Tracking {total} application(s): "
        summary_msg += f"{fully_approved_count} fully approved, "
        summary_msg += f"{pending_approval_count} pending approval, "
        summary_msg += f"{rejected_applications_count} rejected, "
        summary_msg += f"{completed_applications_count} completed."
        
        data = TrackAllApplicationsData(
            total_applications=len(trfs),
            draft_count=draft_count,
            status_breakdown=status_breakdown,
            fully_approved=fully_approved_count,
            pending_approval=pending_approval_count,
            rejected_applications=rejected_applications_count,
            completed_applications=completed_applications_count,
            applications=applications_list,
            summary_message=summary_msg
        )
        
        return TrackAllApplicationsOutput(
            success=True,
            message=f"Retrieved {len(trfs)} application(s) for tracking",
            data=data
        ).model_dump_json()
        
    except Exception as e:
        return TrackAllApplicationsOutput(
            success=False,
            message="Unable to track applications",
            error=ErrorCodes.SYSTEM_ERROR,
            error_details=str(e)
        ).model_dump_json()
    finally:
        session.close()


@tool(args_schema=GetApprovedTRFsInput)
def get_approved_trfs(limit: int = 20) -> str:
    """
    Get all approved TRFs ready for Travel Desk booking.
    Automatically fetches TRFs that have completed all approval levels.
    
    Use this tool to:
    - See which employees need travel booking
    - Find TRFs ready for flight/hotel booking
    - Get overview of pending travel arrangements
    
    Example: "Show me approved travel requests"
    """
    session = get_session()
    
    try:
        # Get TRFs that are fully approved and ready for Travel Desk
        trfs = session.query(TravelRequisitionForm).filter(
            TravelRequisitionForm.status == TRFStatus.APPROVED
        ).order_by(TravelRequisitionForm.created_at.desc()).limit(limit).all()
        
        if not trfs:
            return GetApprovedTRFsOutput(
                success=True,
                message="No approved TRFs ready for booking at this time.",
                data=ApprovedTRFsData(
                    total_approved=0,
                    trfs=[],
                    ready_for_booking=0
                )
            ).model_dump_json()
        
        trf_summaries = [
            ApprovedTRFSummary(
                trf_number=trf.trf_number,
                employee_id=trf.employee_id,
                employee_name=trf.employee_name,
                employee_email=trf.employee_email,
                origin_city=trf.origin_city,
                destination_city=trf.destination_city,
                departure_date=str(trf.departure_date),
                return_date=str(trf.return_date) if trf.return_date else None,
                purpose=trf.purpose,
                estimated_cost=trf.estimated_cost,
                travel_type=trf.travel_type.value if trf.travel_type else "domestic"
            )
            for trf in trfs
        ]
        
        data = ApprovedTRFsData(
            total_approved=len(trf_summaries),
            trfs=trf_summaries,
            ready_for_booking=len(trf_summaries)
        )
        
        return GetApprovedTRFsOutput(
            success=True,
            message=f"Found {len(trf_summaries)} approved TRF(s) ready for booking",
            data=data
        ).model_dump_json()
        
    except Exception as e:
        return GetApprovedTRFsOutput(
            success=False,
            message="Error fetching approved TRFs",
            error=ErrorCodes.SYSTEM_ERROR,
            error_details=str(e)
        ).model_dump_json()
    finally:
        session.close()


@tool(args_schema=GetApprovedTRFsInput)
def get_approved_for_travel_desk(limit: int = 20) -> str:
    """
    ⭐️ COMPREHENSIVE: Get ALL approved TRFs that need Travel Desk attention.
    
    This tool captures both:
    1. Applications approved by CFO but not yet touched by Travel Desk
    2. Applications already approved by Travel Desk but may not have bookings
    
    This is more comprehensive than get_approved_trfs() and handles the case
    where approved TRFs might be stuck in the queue.
    
    Use this tool to:
    - See ALL approved applications (with or without Travel Desk approval)
    - Find applications ready for booking or that need booking completion
    - Get a complete view of what needs Travel Desk action
    
    Example: "Show me all approved travel requests ready for booking"
    """
    session = get_session()
    
    try:
        # Fetch ALL TRFs with APPROVED status, regardless of travel_desk_approved_at
        trfs = session.query(TravelRequisitionForm).filter(
            TravelRequisitionForm.status == TRFStatus.APPROVED
        ).order_by(TravelRequisitionForm.created_at.desc()).limit(limit).all()
        
        if not trfs:
            return GetApprovedTRFsOutput(
                success=True,
                message="No approved TRFs ready for Travel Desk at this time.",
                data=ApprovedTRFsData(
                    total_approved=0,
                    trfs=[],
                    ready_for_booking=0
                )
            ).model_dump_json()
        
        trf_summaries = []
        for trf in trfs:
            # Check if this TRF already has bookings
            has_bookings = bool(trf.travel_bookings)
            
            summary = ApprovedTRFSummary(
                trf_number=trf.trf_number,
                employee_id=trf.employee_id,
                employee_name=trf.employee_name,
                employee_email=trf.employee_email,
                origin_city=trf.origin_city,
                destination_city=trf.destination_city,
                departure_date=str(trf.departure_date),
                return_date=str(trf.return_date) if trf.return_date else None,
                purpose=trf.purpose,
                estimated_cost=trf.estimated_cost,
                travel_type=trf.travel_type.value if trf.travel_type else "domestic"
            )
            trf_summaries.append(summary)
        
        data = ApprovedTRFsData(
            total_approved=len(trf_summaries),
            trfs=trf_summaries,
            ready_for_booking=len(trf_summaries)
        )
        
        return GetApprovedTRFsOutput(
            success=True,
            message=f"Found {len(trf_summaries)} approved TRF(s) - some may need booking completion",
            data=data
        ).model_dump_json()
        
    except Exception as e:
        return GetApprovedTRFsOutput(
            success=False,
            message="Error fetching approved TRFs",
            error=ErrorCodes.SYSTEM_ERROR,
            error_details=str(e)
        ).model_dump_json()
    finally:
        session.close()


@tool(args_schema=CompleteTravelPlanInput)
def complete_travel_plan(
    trf_number: str,
    include_hotels: bool = True,
    cabin_class: Optional[str] = "economy"
) -> str:
    """
    Create a complete travel plan with flights and hotels for an approved TRF.
    Searches for and plans entire trip including accommodations.
    
    Use this tool to:
    - Generate complete travel plans
    - Book flights and hotels together
    - Get cost estimates for entire trip
    - Create comprehensive travel itineraries
    
    Example: "Create complete travel plan for TRF202500001"
    """
    session = get_session()
    
    try:
        # Get TRF details
        trf = session.query(TravelRequisitionForm).filter_by(trf_number=trf_number).first()
        if not trf:
            return CompleteTravelPlanOutput(
                success=False,
                message=f"TRF {trf_number} not found",
                error=ErrorCodes.TRF_NOT_FOUND
            ).model_dump_json()
        
        if trf.status != TRFStatus.APPROVED:
            return CompleteTravelPlanOutput(
                success=False,
                message=f"TRF must be approved before planning. Current status: {trf.status.value}",
                error=ErrorCodes.INVALID_STATUS
            ).model_dump_json()
        
        # Get flights
        flights_data = []
        total_flight_cost = 0
        
        try:
            flight_results = session.query(FlightInventory).filter(
                FlightInventory.origin_city == trf.origin_city,
                FlightInventory.destination_city == trf.destination_city,
                FlightInventory.departure_date == trf.departure_date,
                FlightInventory.is_available == True
            ).limit(3).all()
            
            for flight in flight_results:
                airline = session.query(Airline).get(flight.airline_id)
                if airline:
                    price_map = {
                        "economy": flight.economy_price,
                        "premium_economy": flight.premium_economy_price,
                        "business": flight.business_price,
                        "first": flight.first_price
                    }
                    price = price_map.get(cabin_class, flight.economy_price)
                    discount = price * (airline.corporate_discount / 100)
                    final_price = price - discount
                    total_flight_cost = final_price
                    
                    flights_data.append(BookedFlightInfo(
                        flight_id=flight.id,
                        flight_number=flight.flight_number,
                        airline=airline.name,
                        airline_code=airline.code,
                        origin_city=flight.origin_city,
                        destination_city=flight.destination_city,
                        departure_date=str(flight.departure_date),
                        arrival_date=str(flight.arrival_date),
                        departure_time=flight.departure_time.strftime("%H:%M"),
                        arrival_time=flight.arrival_time.strftime("%H:%M"),
                        duration=f"{flight.duration_minutes // 60}h {flight.duration_minutes % 60}m",
                        price=round(final_price, 2),
                        cabin_class=cabin_class or "economy",
                        is_direct=flight.is_direct
                    ))
        except:
            flights_data = []
        
        # Get hotels if requested
        hotels_data = []
        total_hotel_cost = 0
        
        if include_hotels:
            try:
                checkin = trf.departure_date
                checkout = trf.return_date or (trf.departure_date + timedelta(days=1))
                
                hotels = session.query(Hotel).filter(
                    Hotel.city == trf.destination_city
                ).limit(3).all()
                
                for hotel in hotels:
                    rooms = session.query(HotelRoomInventory).filter(
                        HotelRoomInventory.hotel_id == hotel.id,
                        HotelRoomInventory.date >= checkin,
                        HotelRoomInventory.date < checkout,
                        HotelRoomInventory.is_available == True
                    ).all()
                    
                    if rooms:
                        nights = (checkout - checkin).days
                        total_cost = sum(r.discounted_price for r in rooms)
                        total_hotel_cost = total_cost
                        
                        hotels_data.append(BookedHotelInfo(
                                hotel_id=hotel.id,
                            hotel_name=hotel.name,
                            city=hotel.city,
                            rating=hotel.rating,
                                room_type=rooms[0].room_type if rooms else None,
                            per_night_rate=round(rooms[0].discounted_price, 2),
                            total_nights=nights,
                            total_cost=round(total_cost, 2),
                                amenities=hotel.amenities or [],
                                inventory_ids=[r.id for r in rooms]
                        ))
            except:
                hotels_data = []
        
        total_cost = total_flight_cost + total_hotel_cost
        
        booking_summary = TravelBookingSummary(
            trf_number=trf_number,
            employee_name=trf.employee_name,
            origin=trf.origin_city,
            destination=trf.destination_city,
            departure_date=str(trf.departure_date),
            return_date=str(trf.return_date) if trf.return_date else None,
            flights_booked=f"Flight {flights_data[0].flight_number}" if flights_data else None,
            hotels_booked=f"Hotel {hotels_data[0].hotel_name}" if hotels_data else None,
            total_estimated_cost=round(total_cost, 2),
            booking_status="planned"
        )
        
        data = CompleteTravelPlanData(
            booking_summary=booking_summary,
            flights=flights_data,
            hotels=hotels_data,
            total_cost=round(total_cost, 2),
            next_steps=[
                "Review the travel plan above",
                "Confirm flights and hotels selection",
                "Proceed with booking confirmation"
            ]
        )
        
        return CompleteTravelPlanOutput(
            success=True,
            message=f"Complete travel plan created for {trf.employee_name}",
            data=data
        ).model_dump_json()
        
    except Exception as e:
        return CompleteTravelPlanOutput(
            success=False,
            message="Error creating travel plan",
            error=ErrorCodes.SYSTEM_ERROR,
            error_details=str(e)
        ).model_dump_json()
    finally:
        session.close()


# ============================================================================
# SIMPLIFIED SEARCH & BOOKING TOOLS (NEW APPROACH)
# ============================================================================

@tool(args_schema=SearchFlightsInput)
def search_flights(
    trf_number: str,
    origin_city: str,
    destination_city: str,
    departure_date: str,
    cabin_class: Optional[str] = "economy",
    max_results: int = 5
) -> str:
    """
    Search available flights for an approved TRF. Returns flight options with IDs 
    for use with confirm_flight_booking().
    
    Use this tool when:
    - Travel Desk wants to see flight options
    - Check availability before confirming
    
    Example: "Search flights for TRF202500004"
    """
    session = get_session()
    try:
        trf = session.query(TravelRequisitionForm).filter_by(trf_number=trf_number).first()
        if not trf:
            return BookFlightOutput(
                success=False,
                message=f"TRF {trf_number} not found",
                error=ErrorCodes.TRF_NOT_FOUND
            ).model_dump_json()
        
        if trf.status not in (TRFStatus.APPROVED, TRFStatus.PROCESSING):
            return BookFlightOutput(
                success=False,
                message=f"TRF must be approved. Current status: {trf.status.value}",
                error=ErrorCodes.INVALID_STATUS
            ).model_dump_json()
        
        try:
            dep_date = datetime.strptime(departure_date, "%Y-%m-%d").date()
        except ValueError:
            return BookFlightOutput(
                success=False,
                message="Invalid date format. Use YYYY-MM-DD",
                error=ErrorCodes.INVALID_DATE_FORMAT
            ).model_dump_json()
        
        base_cabin = (cabin_class or "economy").lower()
        flights = session.query(FlightInventory).filter(
            FlightInventory.origin_city == origin_city,
            FlightInventory.destination_city == destination_city,
            FlightInventory.departure_date == dep_date,
            FlightInventory.is_available == True
        ).limit(max_results).all()
        
        if not flights:
            return BookFlightOutput(
                success=True,
                message=f"No flights available",
                data=BookFlightData(
                    trf_number=trf_number,
                    employee_name=trf.employee_name,
                    route=f"{origin_city} to {destination_city}",
                    available_flights=[],
                    booking_status="no_flights_available"
                )
            ).model_dump_json()
        
        flight_results = []
        for flight in flights:
            airline = session.query(Airline).get(flight.airline_id)
            if not airline:
                continue
            
            price_map = {
                "economy": flight.economy_price,
                "premium_economy": flight.premium_economy_price,
                "business": flight.business_price,
                "first": flight.first_price
            }
            price = price_map.get(base_cabin, flight.economy_price) or flight.economy_price
            discount = price * (airline.corporate_discount / 100)
            final_price = price - discount
            
            flight_results.append(BookedFlightInfo(
                flight_id=flight.id,
                flight_number=flight.flight_number,
                airline=airline.name,
                airline_code=airline.code,
                origin_city=flight.origin_city,
                destination_city=flight.destination_city,
                departure_date=str(flight.departure_date),
                arrival_date=str(flight.arrival_date),
                departure_time=flight.departure_time.strftime("%H:%M"),
                arrival_time=flight.arrival_time.strftime("%H:%M"),
                duration=f"{flight.duration_minutes // 60}h {flight.duration_minutes % 60}m",
                price=round(final_price, 2),
                cabin_class=base_cabin,
                is_direct=flight.is_direct
            ))
        
        data = BookFlightData(
            trf_number=trf_number,
            employee_name=trf.employee_name,
            route=f"{origin_city} to {destination_city}",
            available_flights=flight_results,
            booking_status="available"
        )
        
        return BookFlightOutput(
            success=True,
            message=f"Found {len(flight_results)} flights. Use flight_id with confirm_flight_booking to book.",
            data=data
        ).model_dump_json()
        
    except Exception as e:
        return BookFlightOutput(
            success=False,
            message="Error searching flights",
            error=ErrorCodes.SYSTEM_ERROR,
            error_details=str(e)
        ).model_dump_json()
    finally:
        session.close()


@tool(args_schema=ConfirmFlightBookingInput)
def confirm_flight_booking(
    trf_number: str,
    flight_id: int,
    number_of_passengers: int = 1
) -> str:
    """
    Confirm and book a specific flight. Flight must exist and match the TRF route/date.
    
    Use this tool when:
    - Ready to book a specific flight from search results
    - Pass the flight_id from search_flights response
    
    Example: "Book flight with ID 123"
    """
    session = get_session()
    try:
        trf = session.query(TravelRequisitionForm).filter_by(trf_number=trf_number).first()
        if not trf:
            return BookFlightOutput(
                success=False,
                message=f"TRF {trf_number} not found",
                error=ErrorCodes.TRF_NOT_FOUND
            ).model_dump_json()
        
        if trf.status not in (TRFStatus.APPROVED, TRFStatus.PROCESSING):
            return BookFlightOutput(
                success=False,
                message=f"TRF must be approved. Current status: {trf.status.value}",
                error=ErrorCodes.INVALID_STATUS
            ).model_dump_json()
        
        flight = session.query(FlightInventory).filter_by(id=flight_id).first()
        if not flight:
            return BookFlightOutput(
                success=False,
                message=f"Flight {flight_id} not found",
                error=ErrorCodes.NO_FLIGHTS
            ).model_dump_json()
        
        if not flight.is_available:
            return BookFlightOutput(
                success=False,
                message="Flight is no longer available",
                error=ErrorCodes.NO_FLIGHTS
            ).model_dump_json()
        
        if flight.origin_city.lower() != trf.origin_city.lower() or flight.destination_city.lower() != trf.destination_city.lower():
            return BookFlightOutput(
                success=False,
                message="Flight does not match TRF route",
                error=ErrorCodes.INVALID_STATUS
            ).model_dump_json()
        
        if flight.departure_date != trf.departure_date:
            return BookFlightOutput(
                success=False,
                message="Flight date does not match TRF",
                error=ErrorCodes.INVALID_DATE_RANGE
            ).model_dump_json()
        
        airline = session.query(Airline).get(flight.airline_id)
        if not airline:
            return BookFlightOutput(
                success=False,
                message="Airline not found",
                error=ErrorCodes.SYSTEM_ERROR
            ).model_dump_json()
        
        price_map = {
            "economy": flight.economy_price,
            "premium_economy": flight.premium_economy_price,
            "business": flight.business_price,
            "first": flight.first_price
        }
        price = price_map.get("economy", flight.economy_price) or flight.economy_price
        discount = price * (airline.corporate_discount / 100)
        passengers = number_of_passengers or 1
        base_total = round(price * passengers, 2)
        discount_total = round(discount * passengers, 2)
        final_cost = base_total - discount_total
        
        travel_booking = (
            session.query(TravelBooking)
            .filter(TravelBooking.trf_id == trf.id)
            .order_by(TravelBooking.booking_date.desc())
            .first()
        )
        
        if not travel_booking:
            booking_number = f"TB{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{trf.id}"
            travel_booking = TravelBooking(
                booking_number=booking_number,
                trf_id=trf.id,
                traveler_name=trf.employee_name,
                traveler_email=trf.employee_email,
                traveler_phone=trf.employee_phone,
                traveler_employee_id=trf.employee_id,
                status=BookingStatus.PENDING
            )
            session.add(travel_booking)
            session.flush()
        
        pnr = f"PNR{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{flight.id}"
        flight_booking = FlightBooking(
            pnr=pnr,
            travel_booking_id=travel_booking.id,
            flight_id=flight.id,
            cabin_class=CabinClass.ECONOMY,
            passenger_name=trf.employee_name,
            seat_number=None,
            base_fare=base_total,
            taxes=0.0,
            discount_applied=discount_total,
            final_fare=final_cost,
            status=BookingStatus.CONFIRMED
        )
        session.add(flight_booking)
        flight.is_available = False
        
        travel_booking.total_flight_cost = (travel_booking.total_flight_cost or 0) + final_cost
        travel_booking.total_cost = (travel_booking.total_cost or 0) + final_cost
        travel_booking.status = BookingStatus.CONFIRMED
        travel_booking.confirmation_date = datetime.utcnow()
        
        if trf.status == TRFStatus.APPROVED:
            trf.status = TRFStatus.PROCESSING
        trf.travel_desk_approved_at = trf.travel_desk_approved_at or datetime.utcnow()
        trf.travel_desk_comments = f"Flight booked: {flight.flight_number}"
        
        session.commit()
        
        data = BookFlightData(
            trf_number=trf_number,
            employee_name=trf.employee_name,
            route=f"{flight.origin_city} to {flight.destination_city}",
            available_flights=[],
            booking_status="booked",
            booking_reference=travel_booking.booking_number,
            pnr=pnr,
            flight_number=flight.flight_number,
            total_cost=final_cost
        )
        
        return BookFlightOutput(
            success=True,
            message=f"Flight {flight.flight_number} booked successfully! PNR: {pnr}",
            data=data
        ).model_dump_json()
        
    except Exception as e:
        session.rollback()
        return BookFlightOutput(
            success=False,
            message="Error booking flight",
            error=ErrorCodes.SYSTEM_ERROR,
            error_details=str(e)
        ).model_dump_json()
    finally:
        session.close()


@tool(args_schema=SearchHotelsInput)
def search_hotels(
    trf_number: str,
    city: str,
    check_in_date: str,
    check_out_date: str,
    min_rating: Optional[int] = 3,
    max_results: int = 5
) -> str:
    """
    Search available hotels for an approved TRF. Returns hotel options with IDs 
    for use with confirm_hotel_booking().
    
    Use this tool when:
    - Travel Desk wants to see hotel options
    - Check availability before confirming
    
    Example: "Search hotels for TRF202500004"
    """
    session = get_session()
    try:
        trf = session.query(TravelRequisitionForm).filter_by(trf_number=trf_number).first()
        if not trf:
            return BookHotelOutput(
                success=False,
                message=f"TRF {trf_number} not found",
                error=ErrorCodes.TRF_NOT_FOUND
            ).model_dump_json()
        
        if trf.status not in (TRFStatus.APPROVED, TRFStatus.PROCESSING):
            return BookHotelOutput(
                success=False,
                message=f"TRF must be approved. Current status: {trf.status.value}",
                error=ErrorCodes.INVALID_STATUS
            ).model_dump_json()
        
        try:
            checkin = datetime.strptime(check_in_date, "%Y-%m-%d").date()
            checkout = datetime.strptime(check_out_date, "%Y-%m-%d").date()
        except ValueError:
            return BookHotelOutput(
                success=False,
                message="Invalid date format. Use YYYY-MM-DD",
                error=ErrorCodes.INVALID_DATE_FORMAT
            ).model_dump_json()
        
        if checkout <= checkin:
            return BookHotelOutput(
                success=False,
                message="Check-out date must be after check-in date",
                error=ErrorCodes.INVALID_DATE_RANGE
            ).model_dump_json()
        
        nights = (checkout - checkin).days
        
        query = session.query(Hotel).filter(Hotel.city == city)
        if min_rating:
            query = query.filter(Hotel.rating >= min_rating)
        
        hotels = query.limit(max_results).all()
        
        if not hotels:
            return BookHotelOutput(
                success=True,
                message=f"No hotels found in {city}",
                data=BookHotelData(
                    trf_number=trf_number,
                    employee_name=trf.employee_name,
                    available_hotels=[],
                    booking_status="no_hotels_available"
                )
            ).model_dump_json()
        
        hotel_results = []
        for hotel in hotels:
            rooms = session.query(HotelRoomInventory).filter(
                HotelRoomInventory.hotel_id == hotel.id,
                HotelRoomInventory.date >= checkin,
                HotelRoomInventory.date < checkout,
                HotelRoomInventory.is_available == True
            ).order_by(HotelRoomInventory.date.asc()).all()
            
            if rooms:
                total_cost = sum(r.discounted_price for r in rooms)
                per_night = rooms[0].discounted_price if rooms else 0
                
                hotel_results.append(BookedHotelInfo(
                    hotel_id=hotel.id,
                    hotel_name=hotel.name,
                    city=hotel.city,
                    rating=hotel.rating,
                    room_type=rooms[0].room_type,
                    per_night_rate=round(per_night, 2),
                    total_nights=nights,
                    total_cost=round(total_cost, 2),
                    amenities=hotel.amenities or [],
                    inventory_ids=[r.id for r in rooms]
                ))
        
        data = BookHotelData(
            trf_number=trf_number,
            employee_name=trf.employee_name,
            available_hotels=hotel_results,
            booking_status="available"
        )
        
        return BookHotelOutput(
            success=True,
            message=f"Found {len(hotel_results)} hotels. Use hotel_id with confirm_hotel_booking to book.",
            data=data
        ).model_dump_json()
        
    except Exception as e:
        return BookHotelOutput(
            success=False,
            message="Error searching hotels",
            error=ErrorCodes.SYSTEM_ERROR,
            error_details=str(e)
        ).model_dump_json()
    finally:
        session.close()


@tool(args_schema=ConfirmHotelBookingInput)
def confirm_hotel_booking(
    trf_number: str,
    hotel_id: int,
    check_in_date: str,
    check_out_date: str,
    number_of_guests: int = 1,
    special_requests: Optional[str] = None
) -> str:
    """
    Confirm and book a specific hotel. Hotel must exist and have availability.
    
    Use this tool when:
    - Ready to book a specific hotel from search results
    - Pass the hotel_id from search_hotels response
    
    Example: "Book hotel with ID 9"
    """
    session = get_session()
    try:
        trf = session.query(TravelRequisitionForm).filter_by(trf_number=trf_number).first()
        if not trf:
            return BookHotelOutput(
                success=False,
                message=f"TRF {trf_number} not found",
                error=ErrorCodes.TRF_NOT_FOUND
            ).model_dump_json()
        
        if trf.status not in (TRFStatus.APPROVED, TRFStatus.PROCESSING):
            return BookHotelOutput(
                success=False,
                message=f"TRF must be approved. Current status: {trf.status.value}",
                error=ErrorCodes.INVALID_STATUS
            ).model_dump_json()
        
        try:
            checkin = datetime.strptime(check_in_date, "%Y-%m-%d").date()
            checkout = datetime.strptime(check_out_date, "%Y-%m-%d").date()
        except ValueError:
            return BookHotelOutput(
                success=False,
                message="Invalid date format. Use YYYY-MM-DD",
                error=ErrorCodes.INVALID_DATE_FORMAT
            ).model_dump_json()
        
        if checkout <= checkin:
            return BookHotelOutput(
                success=False,
                message="Check-out date must be after check-in date",
                error=ErrorCodes.INVALID_DATE_RANGE
            ).model_dump_json()
        
        nights = (checkout - checkin).days
        
        hotel = session.query(Hotel).filter_by(id=hotel_id).first()
        if not hotel:
            return BookHotelOutput(
                success=False,
                message=f"Hotel {hotel_id} not found",
                error=ErrorCodes.NO_HOTELS
            ).model_dump_json()
        
        selected_rooms = []
        current_date = checkin
        while current_date < checkout:
            room = (
                session.query(HotelRoomInventory)
                .filter(
                    HotelRoomInventory.hotel_id == hotel_id,
                    HotelRoomInventory.date == current_date,
                    HotelRoomInventory.is_available == True
                )
                .order_by(HotelRoomInventory.discounted_price.asc())
                .first()
            )
            if not room:
                return BookHotelOutput(
                    success=False,
                    message=f"Hotel no longer has availability for all dates",
                    error=ErrorCodes.NO_ROOMS
                ).model_dump_json()
            selected_rooms.append(room)
            current_date += timedelta(days=1)
        
        total_cost = sum(room.discounted_price for room in selected_rooms)
        per_night = round(total_cost / nights, 2)
        
        travel_booking = (
            session.query(TravelBooking)
            .filter(TravelBooking.trf_id == trf.id)
            .order_by(TravelBooking.booking_date.desc())
            .first()
        )
        
        if not travel_booking:
            booking_number = f"TB{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{trf.id}"
            travel_booking = TravelBooking(
                booking_number=booking_number,
                trf_id=trf.id,
                traveler_name=trf.employee_name,
                traveler_email=trf.employee_email,
                traveler_phone=trf.employee_phone,
                traveler_employee_id=trf.employee_id,
                status=BookingStatus.PENDING
            )
            session.add(travel_booking)
            session.flush()
        
        confirmation_number = f"HB{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{hotel_id}"
        hotel_booking = HotelBooking(
            confirmation_number=confirmation_number,
            travel_booking_id=travel_booking.id,
            room_id=selected_rooms[0].id,
            guest_name=trf.employee_name,
            check_in_date=checkin,
            check_out_date=checkout,
            number_of_nights=nights,
            number_of_guests=number_of_guests or 1,
            per_night_rate=per_night,
            total_room_cost=round(total_cost, 2),
            discount_applied=0.0,
            taxes=0.0,
            final_cost=round(total_cost, 2),
            status=BookingStatus.CONFIRMED,
            special_requests=special_requests
        )
        session.add(hotel_booking)
        
        for room in selected_rooms:
            room.is_available = False
        
        travel_booking.total_hotel_cost = (travel_booking.total_hotel_cost or 0) + round(total_cost, 2)
        travel_booking.total_cost = (travel_booking.total_cost or 0) + round(total_cost, 2)
        travel_booking.status = BookingStatus.CONFIRMED
        travel_booking.confirmation_date = datetime.utcnow()
        
        if trf.status == TRFStatus.APPROVED:
            trf.status = TRFStatus.PROCESSING
        trf.travel_desk_approved_at = trf.travel_desk_approved_at or datetime.utcnow()
        comment = f"Hotel booked: {hotel.name} ({check_in_date} to {check_out_date})"
        trf.travel_desk_comments = (
            f"{trf.travel_desk_comments}\n{comment}" if trf.travel_desk_comments else comment
        )
        
        session.commit()
        
        data = BookHotelData(
            trf_number=trf_number,
            employee_name=trf.employee_name,
            available_hotels=[],
            booking_status="booked",
            booking_reference=travel_booking.booking_number,
            hotel_confirmation_number=confirmation_number,
            hotel_name=hotel.name,
            total_cost=round(total_cost, 2)
        )
        
        return BookHotelOutput(
            success=True,
            message=f"Hotel {hotel.name} booked successfully! Confirmation: {confirmation_number}",
            data=data
        ).model_dump_json()
        
    except Exception as e:
        session.rollback()
        return BookHotelOutput(
            success=False,
            message="Error booking hotel",
            error=ErrorCodes.SYSTEM_ERROR,
            error_details=str(e)
        ).model_dump_json()
    finally:
        session.close()


# ============================================================================
# LANGCHAIN TOOLS - POLICY QA (RAG-BASED)
# ============================================================================

@tool
def policy_qa(question: str) -> str:
    """
    Ask questions about corporate travel policies using AI-powered retrieval.
    Query policy documents to get instant answers about travel rules, requirements,
    booking procedures, approvals, expenses, and compliance. Uses semantic search
    to find relevant policy sections and generates accurate answers with citations.
    
    Use this tool when:
    - You need to understand travel policy rules and requirements
    - Employee asking about travel procedures or eligibility
    - Clarify policy compliance or approval requirements
    - Get specific policy information for decision making
    
    Example: "What are the international travel policy guidelines?"
    """
    try:
        qa_system = get_policy_qa()
        result = qa_system.query(question, use_context=True)
        
        # Format response with sources
        answer = result.get("answer", "Unable to find answer")
        sources = result.get("sources", [])
        
        response = f"{answer}"
        
        if sources:
            response += "\n\nSources found:"
            for i, source in enumerate(sources, 1):
                response += f"\n{i}. {source.get('metadata', 'Unknown')} (Relevance: {source.get('score', 'N/A')})"
        
        return response
        
    except Exception as e:
        return f"Error querying policy: {str(e)}"


# ============================================================================
# TOOL LIST FOR EXPORT
# ============================================================================

# NEW simplified tools
ALL_TOOLS = [
    create_trf_draft,
    submit_trf,
    list_employee_drafts,
    get_trf_approval_details,
    get_trf_status,
    list_employee_trfs,
    approve_trf,
    reject_trf,
    get_pending_irm_applications,
    get_pending_srm_applications,
    get_pending_buh_applications,
    get_pending_ssuh_applications,
    get_pending_bgh_applications,
    get_pending_ssgh_applications,
    get_pending_cfo_applications,
    get_pending_travel_desk_applications,
    track_all_applications,
    get_approved_trfs,
    search_flights,
    confirm_flight_booking,
    search_hotels,
    confirm_hotel_booking,
    complete_travel_plan,
    policy_qa,
    get_approved_for_travel_desk
]


if __name__ == "__main__":
    print("=" * 70)
    print("Corporate Travel Management - LangChain Tools with Pydantic")
    print("=" * 70)
    print(f"\nTotal tools: {len(ALL_TOOLS)}")
    for i, tool in enumerate(ALL_TOOLS, 1):
        print(f"{i:2d}. {tool.name}")
    print("\nImport: from database_utils import ALL_TOOLS")