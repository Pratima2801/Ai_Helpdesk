import uuid
from backend.models import HelpRequest, RequestStatus, KBEntry, AuditLog
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

def resolve_help_request(request_id: str, supervisor_id: str, resolution_text: str):
    """
    Transactionally:
      - create KB entry linked to request_id
      - update help_request -> status = resolved, resolution_text, resolved_at
      - insert an audit log entry
    Returns: KBEntry object on success, raises Exception on failure.
    """
    db = SessionLocal()
    try:
        with db.begin(): 
            
            req = db.query(HelpRequest).filter(HelpRequest.id == request_id).with_for_update().first()
            if not req:
                raise ValueError("help_request not found")

            
            kb_id = f"kb_{uuid.uuid4().hex[:8]}"
            kb = KBEntry(
                id=kb_id,
                question_snippet=(req.question_text or (req.transcript or ""))[:250],
                answer_text=resolution_text,
                source_request_id=request_id,
                created_by=supervisor_id,
                created_at=datetime.utcnow()
            )
            db.add(kb)

            
            req.status = RequestStatus.resolved
            req.resolution_text = resolution_text
            req.resolved_at = datetime.utcnow()

            
            audit = AuditLog(
                id=f"audit_{uuid.uuid4().hex[:8]}",
                request_id=request_id,
                event_type="help_request.resolved",
                payload=f"resolved_by={supervisor_id}",
                user_id=supervisor_id,
                created_at=datetime.utcnow()
            )
            db.add(audit)

            db.flush()
            kb_dict = {
                "id": kb.id,
                "question_snippet": kb.question_snippet,
                "answer_text": kb.answer_text,
                "source_request_id": kb.source_request_id,
                "created_by": kb.created_by,
                "created_at": kb.created_at.isoformat() if kb.created_at else None
            }
            db.refresh(kb)

        return kb_dict
    finally:
        db.close()        
