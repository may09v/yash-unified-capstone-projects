"""Pydantic schemas for LangChain tools in the Corporate Travel Management system.

These schemas describe the input arguments and structured outputs that LangChain
agents and LLMs can rely on for consistent reasoning.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from models import CabinClass, TRFStatus, TravelType


# ============================================================================
# ENUMERATIONS AND COMMON TYPES
# ============================================================================


class ErrorCodes(str, Enum):
    """Machine-readable error codes surfaced to downstream agents."""

    INVALID_DATE_FORMAT = "invalid_date_format"
    INVALID_DATE_RANGE = "invalid_date_range"
    INVALID_STATUS = "invalid_status"
    INVALID_LEVEL = "invalid_level"
    INVALID_SEQUENCE = "invalid_sequence"
    INVALID_REASON = "invalid_reason"
    INVALID_AMOUNT = "invalid_amount"
    PAST_DATE = "past_date"
    FUTURE_DATE = "future_date"
    NO_FLIGHTS = "no_flights"
    NO_HOTELS = "no_hotels"
    NO_ROOMS = "no_rooms"
    TRF_NOT_FOUND = "trf_not_found"
    REIMBURSEMENT_NOT_FOUND = "reimbursement_not_found"
    SYSTEM_ERROR = "system_error"


class TravelTypeValues(str, Enum):
    """String enum mirroring :class:`models.TravelType`."""

    DOMESTIC = TravelType.DOMESTIC.value
    INTERNATIONAL = TravelType.INTERNATIONAL.value


class TRFStatusValues(str, Enum):
    """String enum mirroring :class:`models.TRFStatus`."""

    DRAFT = TRFStatus.DRAFT.value
    PENDING_IRM = TRFStatus.PENDING_IRM.value
    PENDING_SRM = TRFStatus.PENDING_SRM.value
    PENDING_BUH = TRFStatus.PENDING_BUH.value
    PENDING_SSUH = TRFStatus.PENDING_SSUH.value
    PENDING_BGH = TRFStatus.PENDING_BGH.value
    PENDING_SSGH = TRFStatus.PENDING_SSGH.value
    PENDING_CFO = TRFStatus.PENDING_CFO.value
    PENDING_TRAVEL_DESK = TRFStatus.PENDING_TRAVEL_DESK.value
    APPROVED = TRFStatus.APPROVED.value
    REJECTED = TRFStatus.REJECTED.value
    PROCESSING = TRFStatus.PROCESSING.value
    COMPLETED = TRFStatus.COMPLETED.value





class CabinClassValues(str, Enum):
    """String enum mirroring :class:`models.CabinClass`."""

    ECONOMY = CabinClass.ECONOMY.value
    PREMIUM_ECONOMY = CabinClass.PREMIUM_ECONOMY.value
    BUSINESS = CabinClass.BUSINESS.value
    FIRST = CabinClass.FIRST.value


# ============================================================================
# BASE MODELS
# ============================================================================


class BaseToolInput(BaseModel):
    """Common configuration shared by tool input schemas."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True, str_strip_whitespace=True)


class BaseToolOutput(BaseModel):
    """Common envelope returned by every tool."""

    model_config = ConfigDict(extra="allow")

    success: bool = Field(..., description="True when the tool completed successfully.")
    message: str = Field(..., description="Human-readable summary of the outcome.")
    error: Optional[ErrorCodes] = Field(
        None,
        description="Machine-readable error code to help LLMs reason about failures.",
    )
    error_details: Optional[str] = Field(
        None,
        description="Diagnostic information or exception text to aid troubleshooting.",
    )
    suggestions: Optional[List[str]] = Field(
        None,
        description="Optional remediation tips an agent can present to the user.",
    )
    data: Optional[Dict[str, Any]] = Field(
        None,
        description="Structured payload for programmatic consumption.",
    )


# ============================================================================
# FLIGHT SEARCH SCHEMAS
# ============================================================================


class FlightSearchInput(BaseToolInput):
    origin_city: str = Field(..., description="City name or airport city for departure.")
    destination_city: str = Field(..., description="City name or airport city for arrival.")
    departure_date: str = Field(
        ...,
        description="Departure date in ISO format (YYYY-MM-DD).",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )
    cabin_class: Optional[CabinClassValues] = Field(
        CabinClassValues.ECONOMY,
        description="Preferred cabin class; defaults to economy if omitted.",
    )
    limit: int = Field(
        10,
        description="Maximum number of flight options to return (1-50).",
        ge=1,
        le=50,
    )


class FlightInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    flight_id: int = Field(..., description="Internal identifier of the flight inventory row.")
    flight_number: str = Field(..., description="Airline flight number (e.g., AI101).")
    airline: str = Field(..., description="Full airline name operating the flight.")
    airline_code: str = Field(..., description="IATA airline code (two letters).")
    is_preferred: bool = Field(..., description="Whether the airline is on the preferred list.")
    origin: str = Field(..., description="Origin city along with IATA code in parentheses.")
    destination: str = Field(..., description="Destination city along with IATA code in parentheses.")
    departure_date: str = Field(..., description="Departure date in ISO format.")
    departure_time: str = Field(..., description="Local departure time in 24h HH:MM.")
    arrival_date: str = Field(..., description="Arrival date in ISO format.")
    arrival_time: str = Field(..., description="Local arrival time in 24h HH:MM.")
    duration_minutes: int = Field(..., description="Total travel duration in minutes.")
    duration_formatted: str = Field(..., description="Human-readable duration (e.g., '2h 30m').")
    base_price: float = Field(..., description="Base fare before corporate discounts.")
    corporate_discount_percent: float = Field(..., description="Corporate discount percentage applied.")
    discount_amount: float = Field(..., description="Absolute discount amount in currency units.")
    final_price: float = Field(..., description="Fare after discount rounded to two decimals.")
    cabin_class: str = Field(..., description="Cabin class used for pricing this option.")
    is_direct: bool = Field(..., description="True when the flight is non-stop.")


class FlightSearchParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    origin: str = Field(..., description="Origin city searched.")
    destination: str = Field(..., description="Destination city searched.")
    date: str = Field(..., description="Departure date string used for search.")
    cabin_class: str = Field(..., description="Cabin class preference provided by the user.")


class FlightSearchData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    flights: List[FlightInfo] = Field(..., description="List of matching flight options.")
    search_params: FlightSearchParams = Field(
        ..., description="Echo of the search parameters used to build results."
    )


class FlightSearchOutput(BaseToolOutput):
    data: Optional[FlightSearchData] = Field(
        None,
        description="Structured flight search results when the query succeeds.",
    )


# ============================================================================
# HOTEL SEARCH SCHEMAS
# ============================================================================


class HotelSearchInput(BaseToolInput):
    city: str = Field(..., description="City where accommodation is needed.")
    check_in_date: str = Field(
        ...,
        description="Check-in date in ISO format (YYYY-MM-DD).",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )
    check_out_date: str = Field(
        ...,
        description="Check-out date in ISO format (YYYY-MM-DD).",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )
    room_type: Optional[str] = Field(
        None,
        description="Optional room category filter such as 'Executive Suite'.",
    )
    min_rating: Optional[int] = Field(
        None,
        description="Minimum hotel star rating (1-5).",
        ge=1,
        le=5,
    )
    limit: int = Field(
        10,
        description="Maximum number of hotel options to return (1-50).",
        ge=1,
        le=50,
    )


class RoomTypeInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    room_type: str = Field(..., description="Room category name (e.g., Deluxe King).")
    occupancy: int = Field(..., description="Maximum number of guests allowed in the room.")
    per_night_rate: float = Field(..., description="Discounted corporate rate per night.")
    nights_available: int = Field(..., description="Number of nights with availability in the range.")
    total_cost: float = Field(..., description="Aggregate cost for all available nights in range.")


class HotelInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    hotel_id: int = Field(..., description="Internal identifier for the hotel record.")
    hotel_name: str = Field(..., description="Hotel property name.")
    chain: Optional[str] = Field(None, description="Brand or chain the hotel belongs to.")
    rating: Optional[int] = Field(None, description="Star rating of the property (1-5).")
    city: str = Field(..., description="City where the hotel is located.")
    country: str = Field(..., description="Country where the hotel is located.")
    address: Optional[str] = Field(None, description="Street address for the hotel.")
    amenities: List[str] = Field(default_factory=list, description="Amenities available at the hotel.")
    tags: List[str] = Field(default_factory=list, description="Descriptive tags such as Business or Luxury.")
    corporate_discount_percent: float = Field(..., description="Corporate discount percentage offered.")
    available_rooms: List[RoomTypeInfo] = Field(
        ..., description="Room categories with availability across the requested dates."
    )
    check_in: str = Field(..., description="Requested check-in date in ISO format.")
    check_out: str = Field(..., description="Requested check-out date in ISO format.")
    number_of_nights: int = Field(..., description="Total number of nights between check-in and check-out.")


class HotelSearchData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    hotels: List[HotelInfo] = Field(..., description="List of hotels that meet the criteria.")
    search_params: Dict[str, Any] = Field(
        ..., description="Echo of the search inputs including city and number of nights."
    )


class HotelSearchOutput(BaseToolOutput):
    data: Optional[HotelSearchData] = Field(
        None,
        description="Structured hotel search results when availability exists.",
    )


# ============================================================================
# TRAVEL PLANNING SCHEMAS
# ============================================================================


class TravelPlanEmployee(BaseModel):
    model_config = ConfigDict(extra="forbid")

    employee_id: str = Field(..., description="Unique employee identifier tied to the plan.")
    name: str = Field(..., description="Full name of the traveling employee.")
    role: str = Field(..., description="Employee role or designation used for policy checks.")


class TravelPlanInput(BaseToolInput):
    employee_id: str = Field(..., description="Employee ID for whom the plan is being prepared.")
    employee_name: str = Field(..., description="Full name of the employee.")
    role: str = Field(..., description="Employee role or seniority information.")
    origin_city: str = Field(..., description="City of departure for the journey.")
    destination_city: str = Field(..., description="City where the trip ends or meetings occur.")
    departure_date: str = Field(
        ...,
        description="Departure date in ISO format (YYYY-MM-DD).",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )
    return_date: Optional[str] = Field(
        None,
        description="Optional return date in ISO format if a round trip is needed.",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )
    cabin_class: Optional[CabinClassValues] = Field(
        CabinClassValues.ECONOMY,
        description="Preferred cabin class for flights; defaults to economy.",
    )
    hotel_city: Optional[str] = Field(
        None,
        description="City used for hotel search; defaults to destination city when omitted.",
    )
    check_in_date: Optional[str] = Field(
        None,
        description="Check-in date override in ISO format (YYYY-MM-DD).",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )
    check_out_date: Optional[str] = Field(
        None,
        description="Check-out date override in ISO format (YYYY-MM-DD).",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )
    room_type: Optional[str] = Field(
        None,
        description="Optional room category preference such as 'Suite' or 'Executive'.",
    )
    min_rating: Optional[int] = Field(
        None,
        description="Minimum acceptable hotel rating (1-5).",
        ge=1,
        le=5,
    )
    flight_limit: int = Field(
        5,
        description="Maximum number of flight options to include in the plan (1-20).",
        ge=1,
        le=20,
    )
    hotel_limit: int = Field(
        5,
        description="Maximum number of hotel options to include in the plan (1-20).",
        ge=1,
        le=20,
    )


class TravelPlanData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    employee: TravelPlanEmployee = Field(..., description="Employee context echoed back to the agent.")
    flights: Optional[FlightSearchData] = Field(
        None,
        description="Flight search subset aligned to the requested itinerary.",
    )
    hotels: Optional[HotelSearchData] = Field(
        None,
        description="Hotel search subset aligned to the requested stay window.",
    )
    advisories: List[str] = Field(
        default_factory=list,
        description="Helpful notes, warnings, or follow-ups for the travel planner.",
    )


class TravelPlanOutput(BaseToolOutput):
    data: Optional[TravelPlanData] = Field(
        None,
        description="Combined trip planning payload including flights, hotels, and employee context.",
    )


# ============================================================================
# TRF SCHEMAS
# ============================================================================


class TRFDraftInput(BaseToolInput):
    employee_id: str = Field(..., description="Unique employee identifier initiating the request.")
    employee_name: str = Field(..., description="Full name of the employee travelling.")
    employee_email: str = Field(..., description="Official email address of the employee.")
    travel_type: TravelTypeValues = Field(..., description="Whether the trip is domestic or international.")
    purpose: str = Field(..., description="Business purpose or objective of the trip.")
    origin_city: str = Field(..., description="Departure city for the trip.")
    destination_city: str = Field(..., description="Arrival city for the trip.")
    departure_date: str = Field(
        ...,
        description="Planned departure date in ISO format (YYYY-MM-DD).",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )
    return_date: Optional[str] = Field(
        None,
        description="Optional return date in ISO format if applicable.",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )
    estimated_cost: Optional[float] = Field(
        None,
        description="Estimated end-to-end travel cost in local currency.",
        gt=0,
    )
    employee_phone: Optional[str] = Field(None, description="Contact number of the employee.")
    employee_department: Optional[str] = Field(None, description="Department initiating the request.")
    employee_designation: Optional[str] = Field(None, description="Designation/title of the employee.")
    employee_location: Optional[str] = Field(None, description="Base office location of the employee.")
    irm_name: Optional[str] = Field(None, description="Immediate reporting manager name.")
    irm_email: Optional[str] = Field(None, description="Immediate reporting manager email.")
    srm_name: Optional[str] = Field(None, description="Second reporting manager name if applicable.")
    srm_email: Optional[str] = Field(None, description="Second reporting manager email address.")

    @field_validator("travel_type", mode="before")
    @classmethod
    def normalize_travel_type(cls, value: Any) -> Any:
        if isinstance(value, str):
            return value.lower()
        return value


class TRFDraftData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    trf_number: str = Field(..., description="Temporary draft TRF number assigned.")
    status: TRFStatusValues = Field(..., description="Current workflow state of the TRF.")
    employee_name: str = Field(..., description="Name of the employee for quick reference.")
    travel: str = Field(..., description="Formatted origin to destination string.")
    departure: str = Field(..., description="Scheduled departure date string.")
    next_steps: List[str] = Field(..., description="Suggested follow-up actions for the user.")


class TRFDraftOutput(BaseToolOutput):
    data: Optional[TRFDraftData] = Field(
        None,
        description="Details of the newly created draft TRF when successful.",
    )


class TRFSubmitInput(BaseToolInput):
    trf_number: str = Field(..., description="Draft TRF number that needs to be submitted.")


class TRFSubmitData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    trf_number: str = Field(..., description="Final TRF number after submission.")
    previous_number: str = Field(..., description="Original draft TRF identifier before submission.")
    status: TRFStatusValues = Field(..., description="New workflow status after submission.")
    submitted_at: str = Field(..., description="Timestamp when the draft was submitted.")
    next_steps: List[str] = Field(..., description="Guidance on tracking the submitted TRF.")


class TRFSubmitOutput(BaseToolOutput):
    data: Optional[TRFSubmitData] = Field(
        None,
        description="Submission confirmation payload containing the final TRF.",
    )


class TRFListInput(BaseToolInput):
    employee_id: str = Field(..., description="Employee ID whose drafts should be listed.")


class TRFDraftSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    trf_number: str = Field(..., description="Draft TRF identifier.")
    travel: str = Field(..., description="Origin to destination summary.")
    departure: str = Field(..., description="Draft departure date in ISO format.")
    return_date: Optional[str] = Field(None, description="Draft return date if provided.")
    purpose: str = Field(..., description="Shortened purpose of travel for quick scanning.")
    created: str = Field(..., description="Creation date of the draft (YYYY-MM-DD).")
    last_updated: str = Field(..., description="Last modification date (YYYY-MM-DD).")


class TRFListData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    employee_id: str = Field(..., description="Employee ID whose drafts are summarized.")
    total: int = Field(..., description="Total number of draft TRFs found.")
    drafts: List[TRFDraftSummary] = Field(..., description="Collection of draft summaries.")


class TRFListOutput(BaseToolOutput):
    data: Optional[TRFListData] = Field(
        None,
        description="Draft TRF summaries for the requested employee.",
    )


class TRFStatusInput(BaseToolInput):
    trf_number: str = Field(..., description="TRF number whose status is required.")


class ApprovalInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: str = Field(..., description="Approver role or designation (SRM/BUH/etc.).")
    status: str = Field(..., description="Approval decision such as APPROVED or REJECTED.")
    at: Optional[str] = Field(None, description="Timestamp of the approval action.")
    comments: Optional[str] = Field(None, description="Comments supplied by the approver.")


class TRFStatusData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    trf_number: str = Field(..., description="TRF identifier being looked up.")
    status: str = Field(..., description="Current workflow state of the TRF.")
    employee: str = Field(..., description="Employee name associated with the TRF.")
    travel: str = Field(..., description="Formatted travel route summary.")
    departure: str = Field(..., description="Scheduled departure date in ISO format.")
    approvals: List[ApprovalInfo] = Field(
        default_factory=list,
        description="Approval history with timestamps and comments.",
    )
    rejection_reason: Optional[str] = Field(
        None, description="Reason for rejection if the TRF was rejected."
    )
    created: str = Field(..., description="TRF creation date in ISO format.")
    travel_bookings: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Confirmed travel booking records with hotel/flight confirmations."
    )


class TRFStatusOutput(BaseToolOutput):
    data: Optional[TRFStatusData] = Field(
        None,
        description="Detailed TRF status payload with approval history.",
    )


class EmployeeTRFListInput(BaseToolInput):
    employee_id: str = Field(..., description="Employee ID whose TRFs should be listed.")
    status_filter: Optional[str] = Field(
        None,
        description="Optional status filter such as 'pending', 'approved', or a specific state.",
    )


class EmployeeTRFSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    trf_number: str = Field(..., description="TRF identifier.")
    status: str = Field(..., description="Current status string for the TRF.")
    travel: str = Field(..., description="Origin to destination summary.")
    departure: str = Field(..., description="Departure date in ISO format.")
    purpose: str = Field(..., description="Short purpose statement for the TRF.")
    created: str = Field(..., description="Creation date in ISO format.")


class EmployeeTRFListData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    employee_id: str = Field(..., description="Employee ID tied to the TRF history.")
    total: int = Field(..., description="Total TRFs that match the supplied filter.")
    filter: str = Field(..., description="Filter applied to the TRF list (e.g., pending or all).")
    trfs: List[EmployeeTRFSummary] = Field(..., description="List of TRF summaries for the employee.")


class EmployeeTRFListOutput(BaseToolOutput):
    data: Optional[EmployeeTRFListData] = Field(
        None,
        description="Structured TRF list payload for an employee.",
    )


class TRFApprovalContextInput(BaseToolInput):
    """Fetch TRF details to determine next approval level automatically."""
    trf_number: str = Field(..., description="TRF number to retrieve approval context for.")


class TRFApprovalContextInfo(BaseModel):
    """Context needed before approving - helps LLM determine the right approval level."""
    model_config = ConfigDict(extra="forbid")
    
    trf_number: str = Field(..., description="TRF identifier.")
    current_status: str = Field(..., description="Current TRF status (e.g., PENDING_IRM).")
    next_approval_level: str = Field(
        ..., 
        description="The approval level that should approve next (irm, srm, buh, ssuh, bgh, ssgh, cfo, or travel_desk). Use this to fill the approver_level in approve_trf()."
    )
    employee_name: str = Field(..., description="Employee requesting travel.")
    employee_id: str = Field(..., description="Employee ID.")
    travel_type: Optional[str] = Field(None, description="Travel type (domestic or international).")
    origin_city: str = Field(..., description="Travel origin city.")
    destination_city: str = Field(..., description="Travel destination city.")
    departure_date: str = Field(..., description="Travel departure date (YYYY-MM-DD).")
    return_date: Optional[str] = Field(None, description="Travel return date if applicable.")
    purpose: str = Field(..., description="Purpose of travel.")
    estimated_cost: Optional[float] = Field(None, description="Estimated travel cost.")
    
    # Approval chain so far
    irm_approved: str = Field("No", description="IRM approval status (Yes/No).")
    irm_approved_at: Optional[str] = Field(None, description="When IRM approved.")
    irm_comments: Optional[str] = Field(None, description="IRM comments.")
    
    srm_approved: str = Field("No", description="SRM approval status (Yes/No).")
    srm_approved_at: Optional[str] = Field(None, description="When SRM approved.")
    
    buh_approved: str = Field("No", description="BUH approval status (Yes/No).")
    buh_approved_at: Optional[str] = Field(None, description="When BUH approved.")
    
    ssuh_approved: str = Field("No", description="SSUH approval status (Yes/No).")
    ssuh_approved_at: Optional[str] = Field(None, description="When SSUH approved.")
    
    bgh_approved: str = Field("No", description="BGH approval status (Yes/No).")
    bgh_approved_at: Optional[str] = Field(None, description="When BGH approved.")
    
    ssgh_approved: str = Field("No", description="SSGH approval status (Yes/No).")
    ssgh_approved_at: Optional[str] = Field(None, description="When SSGH approved.")
    
    cfo_approved: str = Field("No", description="CFO approval status (Yes/No).")
    cfo_approved_at: Optional[str] = Field(None, description="When CFO approved.")
    
    travel_desk_approved: str = Field("No", description="Travel Desk approval status (Yes/No).")


class TRFApprovalContextOutput(BaseToolOutput):
    """Response with TRF context and auto-detected approval level."""
    data: Optional[TRFApprovalContextInfo] = Field(
        None,
        description="TRF details with next approval level for the agent to use.",
    )


class TRFApprovalInput(BaseToolInput):
    trf_number: str = Field(..., description="TRF number awaiting approval.")
    approver_level: str = Field(
        ...,
        description="Approval level performing the action (irm, srm, buh, ssuh, bgh, ssgh, cfo, travel_desk). Get this from get_trf_approval_details() first for context awareness.",
        min_length=3,
    )
    comments: Optional[str] = Field(None, description="Optional comments supporting the approval.")
    require_cfo: bool = Field(
        False,
        description="Set to true when BGH approval should route to CFO before completion.",
    )

    @field_validator("approver_level")
    @classmethod
    def normalize_level(cls, value: str) -> str:
        return value.lower()


class TRFApprovalData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    trf_number: str = Field(..., description="TRF identifier that was approved.")
    new_status: str = Field(..., description="Status after the approval action completed.")
    approved_at: str = Field(..., description="Timestamp when the approval was recorded.")
    
    # Application context for awareness
    travel_type: Optional[str] = Field(None, description="Travel type (domestic or international) - helps ensure policy compliance.")
    employee_name: Optional[str] = Field(None, description="Employee requesting travel.")
    origin_city: Optional[str] = Field(None, description="Travel origin city.")
    destination_city: Optional[str] = Field(None, description="Travel destination city.")
    departure_date: Optional[str] = Field(None, description="Travel departure date.")
    purpose: Optional[str] = Field(None, description="Purpose of travel.")
    estimated_cost: Optional[float] = Field(None, description="Estimated travel cost.")


class TRFApprovalOutput(BaseToolOutput):
    data: Optional[TRFApprovalData] = Field(
        None,
        description="Payload describing the approval action that just occurred.",
    )


class TRFRejectionInput(BaseToolInput):
    trf_number: str = Field(..., description="TRF identifier being rejected.")
    approver_level: str = Field(
        ...,
        description="Approval hierarchy level issuing the rejection.",
        min_length=3,
    )
    rejection_reason: str = Field(
        ...,
        description="Detailed reason (>=10 characters) explaining the rejection.",
        min_length=10,
    )

    @field_validator("approver_level")
    @classmethod
    def normalize_rejection_level(cls, value: str) -> str:
        return value.lower()


class TRFRejectionData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    trf_number: str = Field(..., description="TRF identifier that was rejected.")
    status: str = Field(..., description="Current status which should now be REJECTED.")
    reason: str = Field(..., description="Human-readable rejection reason shared with the employee.")
    
    # Application context for awareness
    travel_type: Optional[str] = Field(None, description="Travel type (domestic or international).")
    employee_name: Optional[str] = Field(None, description="Employee requesting travel.")
    origin_city: Optional[str] = Field(None, description="Travel origin city.")
    destination_city: Optional[str] = Field(None, description="Travel destination city.")
    departure_date: Optional[str] = Field(None, description="Travel departure date.")


class TRFRejectionOutput(BaseToolOutput):
    data: Optional[TRFRejectionData] = Field(
        None,
        description="Payload returned when a TRF is rejected.",
    )


# ============================================================================
# PENDING APPLICATIONS OUTPUT SCHEMAS
# ============================================================================

class PendingApplicationInfo(BaseModel):
    """Information about a single pending TRF application."""
    
    model_config = ConfigDict(extra="forbid")
    
    trf_number: str = Field(..., description="TRF identifier.")
    employee_name: str = Field(..., description="Name of employee who submitted the TRF.")
    employee_id: str = Field(..., description="Employee ID.")
    travel: str = Field(..., description="Travel route (origin to destination).")
    departure_date: str = Field(..., description="Travel departure date (YYYY-MM-DD).")
    estimated_cost: Optional[float] = Field(None, description="Estimated cost of travel.")
    purpose: str = Field(..., description="Purpose of travel (truncated).")
    created: str = Field(..., description="When TRF was created (YYYY-MM-DD HH:MM).")
    days_pending: int = Field(..., description="Number of days pending approval.")


class PendingApplicationsData(BaseModel):
    """Container for pending applications list."""
    
    model_config = ConfigDict(extra="allow")
    
    role: str = Field(..., description="Approver role viewing their queue.")
    total_pending: int = Field(..., description="Total count of pending applications.")
    applications: List[Dict[str, Any]] = Field(..., description="List of pending applications.")
    message: str = Field(..., description="Summary message about pending applications.")


class PendingApplicationsOutput(BaseToolOutput):
    """Output for pending applications retrieval."""
    
    data: Optional[PendingApplicationsData] = Field(
        None,
        description="Pending applications data for the role.",
    )


class TravelDeskApplicationInfo(BaseModel):
    """Detailed application info for Travel Desk with complete approval chain."""
    
    model_config = ConfigDict(extra="allow")
    
    trf_number: str = Field(..., description="Travel Requisition Form number.")
    employee_name: str = Field(..., description="Employee requesting travel.")
    employee_id: str = Field(..., description="Employee ID.")
    employee_email: Optional[str] = Field(None, description="Employee email for contact.")
    travel: str = Field(..., description="Travel route (origin to destination).")
    travel_type: Optional[str] = Field(None, description="Type of travel (domestic/international).")
    departure_date: str = Field(..., description="Departure date (YYYY-MM-DD).")
    return_date: Optional[str] = Field(None, description="Return date (YYYY-MM-DD).")
    estimated_cost: Optional[float] = Field(None, description="Estimated travel cost.")
    purpose: str = Field(..., description="Purpose of travel.")
    current_status: str = Field(..., description="Workflow status stored on the TRF record.")
    readiness_state: str = Field(
        ...,
        description="Reason this TRF needs Travel Desk action (pending_travel_desk, legacy_cfo_approved, processing)."
    )
    all_approvals_complete: str = Field("Yes", description="Confirmation all approvals done.")
    cfo_approved: str = Field("Yes", description="CFO approval status.")
    cfo_comments: Optional[str] = Field(None, description="CFO's approval comments.")
    irm_approved: Optional[str] = Field(None, description="IRM approval status.")
    srm_approved: Optional[str] = Field(None, description="SRM approval status.")
    buh_approved: Optional[str] = Field(None, description="BUH approval status.")
    ssuh_approved: Optional[str] = Field(None, description="SSUH approval status.")
    bgh_approved: Optional[str] = Field(None, description="BGH approval status.")
    ssgh_approved: Optional[str] = Field(None, description="SSGH approval status.")
    created: str = Field(..., description="Created date and time.")
    days_pending: int = Field(..., description="Days since TRF was created.")


class TravelDeskPendingData(BaseModel):
    """Container for Travel Desk pending applications with specialized fields."""
    
    model_config = ConfigDict(extra="allow")
    
    role: str = Field("TRAVEL_DESK", description="Role - always TRAVEL_DESK.")
    total_pending: int = Field(..., description="Total count of applications ready for booking.")
    applications: List[TravelDeskApplicationInfo] = Field(
        ..., 
        description="List of applications with all approval details."
    )
    message: str = Field(
        ..., 
        description="Summary message about ready-to-book applications."
    )


class TravelDeskPendingOutput(BaseToolOutput):
    """Output for Travel Desk pending applications retrieval."""
    
    data: Optional[TravelDeskPendingData] = Field(
        None,
        description="Travel Desk pending applications with complete approval chain.",
    )


# ============================================================================
# TRACK ALL APPLICATIONS SCHEMAS (Travel Desk - All non-draft applications)
# ============================================================================

class TrackAllApplicationsInput(BaseToolInput):
    """Input schema for tracking all applications.
    
    Takes no required parameters - retrieves all non-draft applications.
    Optional parameters can be added in future for filtering.
    """
    
    pass  # No additional parameters needed; inherits from BaseToolInput


class TrackAllApplicationsInfo(BaseModel):
    """Detailed information about each TRF application (excluding drafts)."""
    
    model_config = ConfigDict(extra="allow")
    
    trf_number: str = Field(..., description="Travel Requisition Form number.")
    employee_id: str = Field(..., description="Employee ID.")
    employee_name: str = Field(..., description="Employee requesting travel.")
    employee_email: Optional[str] = Field(None, description="Employee email for contact.")
    employee_designation: Optional[str] = Field(None, description="Employee designation/role.")
    employee_department: Optional[str] = Field(None, description="Employee department.")
    
    # Travel Details
    travel: str = Field(..., description="Travel route (origin to destination).")
    travel_type: Optional[str] = Field(None, description="Type of travel (domestic/international).")
    departure_date: str = Field(..., description="Departure date (YYYY-MM-DD).")
    return_date: Optional[str] = Field(None, description="Return date (YYYY-MM-DD).")
    estimated_cost: Optional[float] = Field(None, description="Estimated travel cost.")
    purpose: str = Field(..., description="Purpose of travel.")
    
    # Current Status
    status: str = Field(..., description="Current workflow status.")
    
    # Approval Chain Status
    irm_approved: str = Field(..., description="IRM approval status (Yes/No).")
    irm_approved_at: Optional[str] = Field(None, description="When IRM approved (YYYY-MM-DD HH:MM).")
    irm_comments: Optional[str] = Field(None, description="IRM approval comments.")
    
    srm_approved: str = Field(..., description="SRM approval status (Yes/No).")
    srm_approved_at: Optional[str] = Field(None, description="When SRM approved.")
    srm_comments: Optional[str] = Field(None, description="SRM approval comments.")
    
    buh_approved: str = Field(..., description="BUH approval status (Yes/No).")
    buh_approved_at: Optional[str] = Field(None, description="When BUH approved.")
    buh_comments: Optional[str] = Field(None, description="BUH approval comments.")
    
    ssuh_approved: str = Field(..., description="SSUH approval status (Yes/No).")
    ssuh_approved_at: Optional[str] = Field(None, description="When SSUH approved.")
    ssuh_comments: Optional[str] = Field(None, description="SSUH approval comments.")
    
    bgh_approved: str = Field(..., description="BGH approval status (Yes/No).")
    bgh_approved_at: Optional[str] = Field(None, description="When BGH approved.")
    bgh_comments: Optional[str] = Field(None, description="BGH approval comments.")
    
    ssgh_approved: str = Field(..., description="SSGH approval status (Yes/No).")
    ssgh_approved_at: Optional[str] = Field(None, description="When SSGH approved.")
    ssgh_comments: Optional[str] = Field(None, description="SSGH approval comments.")
    
    cfo_approved: str = Field(..., description="CFO approval status (Yes/No).")
    cfo_approved_at: Optional[str] = Field(None, description="When CFO approved.")
    cfo_comments: Optional[str] = Field(None, description="CFO approval comments.")
    
    travel_desk_approved: str = Field(..., description="Travel Desk approval status (Yes/No).")
    travel_desk_approved_at: Optional[str] = Field(None, description="When Travel Desk approved.")
    travel_desk_comments: Optional[str] = Field(None, description="Travel Desk approval comments.")
    
    # Metadata
    created: str = Field(..., description="Created date and time (YYYY-MM-DD HH:MM).")
    updated: str = Field(..., description="Last updated date and time (YYYY-MM-DD HH:MM).")
    days_old: int = Field(..., description="Number of days since TRF was created.")
    rejection_reason: Optional[str] = Field(None, description="Rejection reason if rejected.")
    rejected_by: Optional[str] = Field(None, description="Role that rejected the TRF.")


class TrackAllApplicationsData(BaseModel):
    """Container for all applications (non-draft) with complete details."""
    
    model_config = ConfigDict(extra="forbid")
    
    total_applications: int = Field(..., description="Total count of non-draft applications.")
    draft_count: int = Field(..., description="Count of draft applications (for reference).")
    
    # Grouped by status
    status_breakdown: Dict[str, int] = Field(
        ...,
        description="Count of applications by current status."
    )
    
    # Approval chain completeness
    fully_approved: int = Field(..., description="Applications with all approvals completed.")
    pending_approval: int = Field(..., description="Applications waiting for some approval.")
    rejected_applications: int = Field(..., description="Applications that were rejected.")
    completed_applications: int = Field(..., description="Completed/processed applications.")
    
    applications: List[TrackAllApplicationsInfo] = Field(
        ...,
        description="Detailed information for each application."
    )
    
    summary_message: str = Field(
        ...,
        description="Human-readable summary of all applications."
    )


class TrackAllApplicationsOutput(BaseToolOutput):
    """Output for tracking all applications (excluding drafts)."""
    
    data: Optional[TrackAllApplicationsData] = Field(
        None,
        description="Complete information about all non-draft TRF applications.",
    )





class ApprovedTRFSummary(BaseModel):
    """Summary of approved TRF ready for Travel Desk booking."""
    model_config = ConfigDict(extra="forbid")
    
    trf_number: str = Field(..., description="TRF identifier")
    employee_id: str = Field(..., description="Employee ID")
    employee_name: str = Field(..., description="Full name of traveling employee")
    employee_email: str = Field(..., description="Employee email address")
    origin_city: str = Field(..., description="Departure city")
    destination_city: str = Field(..., description="Arrival city")
    departure_date: str = Field(..., description="Departure date (YYYY-MM-DD)")
    return_date: Optional[str] = Field(None, description="Return date if round-trip (YYYY-MM-DD)")
    purpose: str = Field(..., description="Business purpose of travel")
    estimated_cost: Optional[float] = Field(None, description="Estimated budget")
    travel_type: str = Field(..., description="domestic or international")


class GetApprovedTRFsInput(BaseToolInput):
    """Input for fetching approved TRFs ready for booking."""
    limit: int = Field(
        20,
        description="Max number of approved TRFs to return (default 20, max 100)",
        ge=1,
        le=100
    )


class ApprovedTRFsData(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    total_approved: int = Field(..., description="Total number of approved TRFs ready for booking")
    trfs: List[ApprovedTRFSummary] = Field(..., description="List of approved TRFs")
    ready_for_booking: int = Field(..., description="Count of TRFs ready for immediate booking")


class GetApprovedTRFsOutput(BaseToolOutput):
    data: Optional[ApprovedTRFsData] = Field(
        None,
        description="List of all approved TRFs ready for Travel Desk booking"
    )


# ============================================================================
# SIMPLIFIED FLIGHT SEARCH & BOOKING SCHEMAS
# ============================================================================

class SearchFlightsInput(BaseToolInput):
    """Search available flights for an approved TRF.
    
    Returns a list of available flights with complete details including flight IDs,
    pricing, airline info, and timing. Use flight_id with confirm_flight_booking().
    """
    trf_number: str = Field(
        ..., 
        description="Approved Travel Requisition Form number (e.g., TRF202500004)",
        examples=["TRF202500004", "TRF202500002"]
    )
    origin_city: str = Field(
        ..., 
        description="Departure city name (e.g., Delhi, Mumbai, Bengaluru)",
        examples=["Delhi", "Mumbai", "Bengaluru"]
    )
    destination_city: str = Field(
        ..., 
        description="Arrival city name",
        examples=["Bengaluru", "Mumbai", "Delhi"]
    )
    departure_date: str = Field(
        ...,
        description="Departure date in ISO 8601 format (YYYY-MM-DD)",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        examples=["2025-12-10"]
    )
    cabin_class: Optional[str] = Field(
        "economy", 
        description="Preferred cabin class: economy, premium_economy, business, first",
        examples=["economy", "business"]
    )
    max_results: int = Field(
        5, 
        description="Maximum number of flight options to return (1-20, default 5)", 
        ge=1, 
        le=20
    )


class ConfirmFlightBookingInput(BaseToolInput):
    """Confirm and book a specific flight from search results.
    
    Takes the flight_id from search_flights response and creates a confirmed booking
    with payment lock, inventory reservation, and PNR generation.
    """
    trf_number: str = Field(
        ..., 
        description="Approved TRF number (must match the search query)",
        examples=["TRF202500004"]
    )
    flight_id: int = Field(
        ..., 
        description="Flight inventory ID from search_flights results (required)",
        examples=[1, 5, 123]
    )
    number_of_passengers: int = Field(
        1, 
        description="Total number of passengers (1-5, usually same as traveler count)",
        ge=1, 
        le=5,
        examples=[1, 2, 3]
    )


class BookedFlightInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    flight_id: int
    flight_number: str
    airline: str
    airline_code: Optional[str] = None
    origin_city: str
    destination_city: str
    departure_date: str
    arrival_date: str
    departure_time: str
    arrival_time: str
    duration: str
    price: float
    cabin_class: str
    is_direct: bool


class BookFlightData(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    trf_number: str
    employee_name: str
    route: str
    available_flights: List[BookedFlightInfo] = Field(
        default_factory=list,
        description="Search results when selection is still required."
    )
    booking_status: str = Field(
        ..., description="available | selection_required | no_flights_available | booked"
    )
    booking_reference: Optional[str] = Field(
        None, description="Travel booking number created when flight is confirmed"
    )
    pnr: Optional[str] = Field(
        None, description="Flight booking record locator"
    )
    flight_number: Optional[str] = Field(
        None, description="Flight number that was booked"
    )
    total_cost: Optional[float] = Field(
        None, description="Final confirmed fare"
    )


class ConfirmFlightBookingOutput(BaseToolOutput):
    """Confirmation of flight booking with PNR and cost details."""
    data: Optional[Dict[str, Any]] = Field(
        None,
        description="Booking confirmation including PNR, flight details, and cost breakdown"
    )


class SearchFlightsOutput(BaseToolOutput):
    """Flight search results with complete options and pricing.
    
    Contains list of available flights with IDs, timing, routing, and per-passenger pricing.
    Use flight_id from any option with confirm_flight_booking() to complete the booking.
    """
    data: Optional[BookFlightData] = Field(
        None,
        description="Search results including available flights list with complete details"
    )


class BookFlightOutput(BaseToolOutput):
    """Unified output for flight booking operations (search or confirm)."""
    data: Optional[BookFlightData] = Field(
        None,
        description="Flight booking data including search results or confirmation details"
    )


class SearchHotelsInput(BaseToolInput):
    """Search available hotels for an approved TRF.
    
    Returns a list of available hotels with complete details including hotel IDs,
    pricing per night, room types, amenities, and ratings. Use hotel_id with confirm_hotel_booking().
    """
    trf_number: str = Field(
        ..., 
        description="Approved Travel Requisition Form number",
        examples=["TRF202500004"]
    )
    city: str = Field(
        ..., 
        description="City where accommodation is needed (e.g., Bengaluru, Mumbai)",
        examples=["Bengaluru", "Mumbai", "Delhi"]
    )
    check_in_date: str = Field(
        ...,
        description="Check-in date in ISO 8601 format (YYYY-MM-DD)",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        examples=["2025-12-10"]
    )
    check_out_date: str = Field(
        ...,
        description="Check-out date in ISO 8601 format (YYYY-MM-DD), must be after check-in",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        examples=["2025-12-15"]
    )
    min_rating: Optional[int] = Field(
        3, 
        description="Minimum hotel star rating filter (1-5 stars, default 3-star and above)",
        ge=1,
        le=5,
        examples=[3, 4, 5]
    )
    max_results: int = Field(
        5, 
        description="Maximum number of hotel options to return (1-20, default 5)", 
        ge=1, 
        le=20
    )


class ConfirmHotelBookingInput(BaseToolInput):
    """Confirm and book a specific hotel from search results.
    
    Takes the hotel_id from search_hotels response and creates a confirmed booking
    with room inventory locking, confirmation number generation, and total cost calculation.
    """
    trf_number: str = Field(
        ..., 
        description="Approved TRF number (must match the search query)",
        examples=["TRF202500004"]
    )
    hotel_id: int = Field(
        ..., 
        description="Hotel ID from search_hotels results (required)",
        examples=[9, 10, 11]
    )
    check_in_date: str = Field(
        ...,
        description="Check-in date (YYYY-MM-DD, must match search dates)",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        examples=["2025-12-10"]
    )
    check_out_date: str = Field(
        ...,
        description="Check-out date (YYYY-MM-DD, must match search dates)",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        examples=["2025-12-15"]
    )
    number_of_guests: int = Field(
        1, 
        description="Number of guests checking in (1-6 people)",
        ge=1, 
        le=6,
        examples=[1, 2, 3]
    )
    special_requests: Optional[str] = Field(
        None, 
        description="Optional special requests (late check-in, early check-out, high floor, etc.)",
        examples=["Late check-in after 10 PM", "High floor preferred", "Crib needed"]
    )


class BookedHotelInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    hotel_id: int
    hotel_name: str
    city: str
    rating: Optional[int]
    room_type: Optional[str] = Field(None, description="Room category represented by this option")
    per_night_rate: float
    total_nights: int
    total_cost: float
    amenities: List[str]
    inventory_ids: List[int] = Field(
        default_factory=list,
        description="Underlying room inventory row IDs used to build this option."
    )


class BookHotelData(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    trf_number: str
    employee_name: str
    available_hotels: List[BookedHotelInfo] = Field(
        default_factory=list,
        description="Search results showing currently available hotel options."
    )
    booking_status: str = Field(
        ..., description="Indicates whether more input is needed or booking is confirmed"
    )
    booking_reference: Optional[str] = Field(
        None, description="Travel booking reference once reservation is stored"
    )
    hotel_confirmation_number: Optional[str] = Field(
        None, description="Hotel confirmation number created in the database"
    )
    hotel_name: Optional[str] = Field(
        None, description="Name of the hotel that was confirmed"
    )
    total_cost: Optional[float] = Field(
        None, description="Total confirmed cost for the hotel stay"
    )


class ConfirmHotelBookingOutput(BaseToolOutput):
    """Confirmation of hotel booking with confirmation number and cost details."""
    data: Optional[Dict[str, Any]] = Field(
        None,
        description="Booking confirmation including confirmation number, room details, and cost breakdown"
    )


class SearchHotelsOutput(BaseToolOutput):
    """Hotel search results with complete options and pricing.
    
    Contains list of available hotels with IDs, room types, nightly rates, and amenities.
    Use hotel_id from any option with confirm_hotel_booking() to complete the booking.
    """
    data: Optional[BookHotelData] = Field(
        None,
        description="Search results including available hotels list with complete details"
    )


class BookHotelOutput(BaseToolOutput):
    """Unified output for hotel booking operations (search or confirm)."""
    data: Optional[BookHotelData] = Field(
        None,
        description="Hotel booking data including search results or confirmation details"
    )


class TravelBookingSummary(BaseModel):
    """Complete travel booking summary."""
    model_config = ConfigDict(extra="forbid")
    
    trf_number: str
    employee_name: str
    origin: str
    destination: str
    departure_date: str
    return_date: Optional[str]
    flights_booked: Optional[str] = Field(None, description="Flight booking reference if booked")
    hotels_booked: Optional[str] = Field(None, description="Hotel booking reference if booked")
    total_estimated_cost: float
    booking_status: str


class CompleteTravelPlanInput(BaseToolInput):
    """Input for complete travel planning and booking."""
    trf_number: str = Field(..., description="TRF number to plan travel for")
    include_hotels: bool = Field(True, description="Whether to include hotel booking")
    cabin_class: Optional[str] = Field("economy", description="Preferred cabin class")


class CompleteTravelPlanData(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    booking_summary: TravelBookingSummary
    flights: Optional[List[BookedFlightInfo]]
    hotels: Optional[List[BookedHotelInfo]]
    total_cost: float
    next_steps: List[str]


class CompleteTravelPlanOutput(BaseToolOutput):
    data: Optional[CompleteTravelPlanData] = Field(
        None,
        description="Complete travel booking plan with flights and hotels"
    )

