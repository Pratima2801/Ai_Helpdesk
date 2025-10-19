import uuid
from backend.models import HelpRequest, RequestStatus
from backend.db import SessionLocal
from datetime import datetime
from sqlalchemy import update

def create_help_request(caller_id: str, caller_phone: str, transcript: str, question_text: str):
    """Create a new help request in DB with status 'pending'."""
    db = SessionLocal()
    try:
        req_id = f"hr_{uuid.uuid4().hex[:8]}"
        new_request = HelpRequest(
            id=req_id,
            caller_id=caller_id,
            caller_phone=caller_phone,
            transcript=transcript,
            question_text=question_text,
            status=RequestStatus.pending,
        )
        db.add(new_request)
        db.commit()
        db.refresh(new_request)
        return new_request
    finally:
        db.close()

def list_help_requests(status: str = "pending"):
    """Return list of HelpRequest objects filtered by status name"""
    db = SessionLocal()
    try:
        try:
            enum_status = RequestStatus[status]
        except Exception:
            enum_status = RequestStatus.pending
        return db.query(HelpRequest).filter(HelpRequest.status == enum_status).all()
    finally:
        db.close()

def atomic_accept(request_id: str, supervisor_id: str):
    """
    Atomically accept a help request.
    Only succeeds if current status is 'pending'.
    Returns True if accepted, False otherwise.
    """
    db = SessionLocal()
    try:
        # Try updating only if it's still pending
        result = db.query(HelpRequest).filter(
            HelpRequest.id == request_id,
            HelpRequest.status == RequestStatus.pending
        ).update(
            {
                HelpRequest.status: RequestStatus.accepted,
                HelpRequest.accepted_by: supervisor_id,
                HelpRequest.accepted_at: datetime.utcnow()
            },
            synchronize_session=False
        )
        db.commit()
        return result > 0  
    finally:
        db.close()        
