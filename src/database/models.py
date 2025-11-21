from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.sql import func
from src.database.connection import Base

class Ticket(Base):
    __tablename__ = "tickets"
    
    ticket_id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    priority = Column(String, nullable=False)
    assigned_team = Column(String, nullable=False)
    suggested_solution = Column(Text)
    status = Column(String, default="pending_confirmation")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
