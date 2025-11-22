# File: /models.py
# Location: Root directory
# Description: SQLAlchemy database models for the corporate travel management system

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean, 
    ForeignKey, Text, Date, Time, Enum as SQLEnum, JSON
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


# ============================================================================
# ENUMS
# ============================================================================

class TravelType(enum.Enum):
    DOMESTIC = "domestic"
    INTERNATIONAL = "international"


class TRFStatus(enum.Enum):
    DRAFT = "draft"
    PENDING_IRM = "pending_irm"
    PENDING_SRM = "pending_srm"
    PENDING_BUH = "pending_buh"
    PENDING_SSUH = "pending_ssuh"
    PENDING_BGH = "pending_bgh"
    PENDING_SSGH = "pending_ssgh"
    PENDING_CFO = "pending_cfo"
    PENDING_TRAVEL_DESK = "pending_travel_desk"
    APPROVED = "approved"
    REJECTED = "rejected"
    PROCESSING = "processing"  # Travel Desk processing
    COMPLETED = "completed"


class BookingStatus(enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class CabinClass(enum.Enum):
    ECONOMY = "economy"
    PREMIUM_ECONOMY = "premium_economy"
    BUSINESS = "business"
    FIRST = "first"


# ============================================================================
# TRAVEL REQUISITION FORM (TRF) - Independent Table
# ============================================================================

class TravelRequisitionForm(Base):
    __tablename__ = "travel_requisition_forms"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    trf_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Employee Information (Embedded - No Foreign Key)
    employee_id = Column(String(50), nullable=False, index=True)
    employee_name = Column(String(200), nullable=False)
    employee_email = Column(String(200), nullable=False)
    employee_phone = Column(String(20))
    employee_department = Column(String(100))
    employee_designation = Column(String(100))
    employee_location = Column(String(100))
    
    # Manager Information (Embedded - No Foreign Key)
    irm_name = Column(String(200))
    irm_email = Column(String(200))
    srm_name = Column(String(200))
    srm_email = Column(String(200))
    
    # Travel Details
    travel_type = Column(SQLEnum(TravelType), nullable=False)
    purpose = Column(Text, nullable=False)
    origin_city = Column(String(100), nullable=False)
    destination_city = Column(String(100), nullable=False)
    departure_date = Column(Date, nullable=False)
    return_date = Column(Date)
    estimated_cost = Column(Float)
    
    # Document Upload
    trf_document_path = Column(String(500))  # Path to uploaded TRF document
    
    # Workflow Status
    status = Column(SQLEnum(TRFStatus), default=TRFStatus.DRAFT, nullable=False)
    
    # IRM Approval
    irm_approved_at = Column(DateTime)
    irm_comments = Column(Text)
    
    # SRM Approval
    srm_approved_at = Column(DateTime)
    srm_comments = Column(Text)
    
    # BUH Approval
    buh_approved_at = Column(DateTime)
    buh_comments = Column(Text)
    
    # SSUH Approval
    ssuh_approved_at = Column(DateTime)
    ssuh_comments = Column(Text)
    
    # BGH Approval
    bgh_approved_at = Column(DateTime)
    bgh_comments = Column(Text)
    
    # SSGH Approval
    ssgh_approved_at = Column(DateTime)
    ssgh_comments = Column(Text)
    
    # CFO Approval
    cfo_approved_at = Column(DateTime)
    cfo_comments = Column(Text)
    
    # Travel Desk Approval
    travel_desk_approved_at = Column(DateTime)
    travel_desk_comments = Column(Text)
    
    # Final Approval
    final_approved_at = Column(DateTime)
    rejection_reason = Column(Text)
    rejected_by = Column(String(50))  # Track which role rejected
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    travel_bookings = relationship("TravelBooking", back_populates="trf")



# ============================================================================
# AIRLINES & FLIGHT INVENTORY
# ============================================================================

class Airline(Base):
    __tablename__ = "airlines"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(10), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    country = Column(String(100))
    is_preferred = Column(Boolean, default=False)
    corporate_discount = Column(Float, default=0.0)  # Percentage
    
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    flights = relationship("FlightInventory", back_populates="airline")


class FlightInventory(Base):
    __tablename__ = "flight_inventory"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Flight Details
    airline_id = Column(Integer, ForeignKey("airlines.id"), nullable=False)
    flight_number = Column(String(20), nullable=False, index=True)
    
    # Route
    origin_code = Column(String(10), nullable=False, index=True)
    destination_code = Column(String(10), nullable=False, index=True)
    origin_city = Column(String(100), nullable=False)
    destination_city = Column(String(100), nullable=False)
    
    # Schedule
    departure_date = Column(Date, nullable=False, index=True)
    departure_time = Column(Time, nullable=False)
    arrival_date = Column(Date, nullable=False)
    arrival_time = Column(Time, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    
    # Pricing by Cabin Class
    economy_price = Column(Float, nullable=False)
    premium_economy_price = Column(Float)
    business_price = Column(Float)
    first_price = Column(Float)
    
    # Additional Info
    is_direct = Column(Boolean, default=True)
    layover_city = Column(String(100))
    layover_duration_minutes = Column(Integer)
    
    # Availability (simplified - just showing it's bookable)
    is_available = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    airline = relationship("Airline", back_populates="flights")
    flight_bookings = relationship("FlightBooking", back_populates="flight")


# ============================================================================
# HOTELS & HOTEL INVENTORY
# ============================================================================

class Hotel(Base):
    __tablename__ = "hotels"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Hotel Details
    name = Column(String(200), nullable=False)
    chain = Column(String(100))  # Grand Hyatt, Marriott, etc.
    rating = Column(Integer)  # 3, 4, 5 stars
    
    # Location
    city = Column(String(100), nullable=False, index=True)
    country = Column(String(100), nullable=False)
    address = Column(Text)
    
    # Pricing Info
    city_tier_multiplier = Column(Float, default=1.0)
    corporate_discount = Column(Float, default=0.0)  # Percentage
    
    # Amenities
    amenities = Column(JSON)  # ["Free WiFi", "Pool", "Gym", etc.]
    tags = Column(JSON)  # ["Luxury", "Business", "Budget"]
    
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    room_inventory = relationship("HotelRoomInventory", back_populates="hotel")


class HotelRoomInventory(Base):
    __tablename__ = "hotel_room_inventory"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Hotel Reference
    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=False)
    
    # Room Details
    room_type = Column(String(100), nullable=False)  # Standard King, Executive Suite, etc.
    occupancy = Column(Integer, default=2)
    
    # Date and Pricing
    date = Column(Date, nullable=False, index=True)
    base_price = Column(Float, nullable=False)
    discounted_price = Column(Float, nullable=False)
    
    # Availability
    is_available = Column(Boolean, default=True)
    
    # Additional amenities for specific room type
    room_amenities = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    hotel = relationship("Hotel", back_populates="room_inventory")
    hotel_bookings = relationship("HotelBooking", back_populates="room")


# ============================================================================
# TRAVEL BOOKINGS
# ============================================================================

class TravelBooking(Base):
    __tablename__ = "travel_bookings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    booking_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # TRF Reference
    trf_id = Column(Integer, ForeignKey("travel_requisition_forms.id"), nullable=False)
    
    # Traveler Info (from booking)
    traveler_name = Column(String(200), nullable=False)
    traveler_email = Column(String(200), nullable=False)
    traveler_phone = Column(String(20))
    traveler_employee_id = Column(String(50))
    
    # Travel Desk Agent (Embedded - No Foreign Key)
    travel_desk_agent_name = Column(String(200))
    travel_desk_agent_email = Column(String(200))
    
    # Booking Status
    status = Column(SQLEnum(BookingStatus), default=BookingStatus.PENDING, nullable=False)
    
    # Cost Summary
    total_flight_cost = Column(Float, default=0.0)
    total_hotel_cost = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)
    
    booking_date = Column(DateTime, default=datetime.utcnow)
    confirmation_date = Column(DateTime)
    
    notes = Column(Text)
    
    # Relationships
    trf = relationship("TravelRequisitionForm", back_populates="travel_bookings")
    flight_bookings = relationship("FlightBooking", back_populates="travel_booking")
    hotel_bookings = relationship("HotelBooking", back_populates="travel_booking")


class FlightBooking(Base):
    __tablename__ = "flight_bookings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    pnr = Column(String(20), unique=True, nullable=False, index=True)
    
    # References
    travel_booking_id = Column(Integer, ForeignKey("travel_bookings.id"), nullable=False)
    flight_id = Column(Integer, ForeignKey("flight_inventory.id"), nullable=False)
    
    # Booking Details
    cabin_class = Column(SQLEnum(CabinClass), nullable=False)
    passenger_name = Column(String(200), nullable=False)
    seat_number = Column(String(10))
    
    # Pricing
    base_fare = Column(Float, nullable=False)
    taxes = Column(Float, default=0.0)
    discount_applied = Column(Float, default=0.0)
    final_fare = Column(Float, nullable=False)
    
    # Status
    status = Column(SQLEnum(BookingStatus), default=BookingStatus.CONFIRMED, nullable=False)
    
    booked_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    travel_booking = relationship("TravelBooking", back_populates="flight_bookings")
    flight = relationship("FlightInventory", back_populates="flight_bookings")


class HotelBooking(Base):
    __tablename__ = "hotel_bookings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    confirmation_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # References
    travel_booking_id = Column(Integer, ForeignKey("travel_bookings.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("hotel_room_inventory.id"), nullable=False)
    
    # Booking Details
    guest_name = Column(String(200), nullable=False)
    check_in_date = Column(Date, nullable=False)
    check_out_date = Column(Date, nullable=False)
    number_of_nights = Column(Integer, nullable=False)
    number_of_guests = Column(Integer, default=1)
    
    # Pricing
    per_night_rate = Column(Float, nullable=False)
    total_room_cost = Column(Float, nullable=False)
    discount_applied = Column(Float, default=0.0)
    taxes = Column(Float, default=0.0)
    final_cost = Column(Float, nullable=False)
    
    # Status
    status = Column(SQLEnum(BookingStatus), default=BookingStatus.CONFIRMED, nullable=False)
    
    special_requests = Column(Text)
    booked_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    travel_booking = relationship("TravelBooking", back_populates="hotel_bookings")
    room = relationship("HotelRoomInventory", back_populates="hotel_bookings")


# ============================================================================
# CITY REFERENCE DATA
# ============================================================================

class City(Base):
    __tablename__ = "cities"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    city = Column(String(100), nullable=False, unique=True, index=True)
    country = Column(String(100), nullable=False)
    currency = Column(String(10), nullable=False)
    tier_multiplier = Column(Float, default=1.0)  # Cost multiplier for the city
    
    created_at = Column(DateTime, default=datetime.utcnow)


class Airport(Base):
    __tablename__ = "airports"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(10), unique=True, nullable=False, index=True)
    city = Column(String(100), nullable=False, index=True)
    country = Column(String(100), nullable=False)
    timezone = Column(String(50))
    
    created_at = Column(DateTime, default=datetime.utcnow)