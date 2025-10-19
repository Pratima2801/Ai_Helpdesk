import uuid
from backend.models import HelpRequest, RequestStatus
from backend.db import SessionLocal

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

def list_help_requests(status=RequestStatus.pending):
    """Fetch all help requests by status (default 'pending')."""
    db = SessionLocal()
    try:
        return db.query(HelpRequest).filter(HelpRequest.status == status).all()
    finally:
        db.close()
