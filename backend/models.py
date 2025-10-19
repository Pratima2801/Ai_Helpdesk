from sqlalchemy import Column, String, Text, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import enum

Base = declarative_base()

class RequestStatus(enum.Enum):
    pending = "pending"
    accepted = "accepted"
    in_progress = "in_progress"
    resolved = "resolved"
    cancelled = "cancelled"

class HelpRequest(Base):
    __tablename__ = "help_requests"
    id = Column(String, primary_key=True, index=True)
    caller_id = Column(String, nullable=True)
    caller_phone = Column(String, nullable=True)
    transcript = Column(Text, nullable=True)
    question_text = Column(Text, nullable=True)
    status = Column(Enum(RequestStatus), default=RequestStatus.pending)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    accepted_by = Column(String, nullable=True)
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    resolution_text = Column(Text, nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    room_id = Column(String, nullable=True)

class KBEntry(Base):
    __tablename__ = "kb_entries"
    id = Column(String, primary_key=True, index=True)
    question_snippet = Column(Text, nullable=True)
    answer_text = Column(Text, nullable=False)
    source_request_id = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(String, primary_key=True, index=True)
    request_id = Column(String, nullable=True)
    event_type = Column(String, nullable=False)
    payload = Column(Text, nullable=True)
    user_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class BusinessInfo(Base):
    __tablename__ = "business_info"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    hours = Column(String, nullable=True)
    services = Column(Text, nullable=True)
    phone = Column(String, nullable=True)
    note = Column(Text, nullable=True)

class Supervisor(Base):
    __tablename__ = "supervisors"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
