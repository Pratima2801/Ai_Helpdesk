from fastapi import APIRouter, Query, HTTPException
from backend.crud import list_help_requests, atomic_accept, resolve_help_request
from backend.simulated_webhooks import send_followup_to_caller

router = APIRouter()

def serialize_request(r):
    return {
        "id": r.id,
        "caller_id": r.caller_id,
        "caller_phone": r.caller_phone,
        "transcript": r.transcript,
        "question_text": r.question_text,
        "status": r.status.value if hasattr(r.status, "value") else str(r.status),
        "created_at": r.created_at.isoformat() if r.created_at else None,
        "accepted_by": r.accepted_by,
        "accepted_at": r.accepted_at.isoformat() if r.accepted_at else None,
        "resolution_text": r.resolution_text,
        "resolved_at": r.resolved_at.isoformat() if r.resolved_at else None,
        "room_id": r.room_id
    }

@router.get("/help-requests")
def get_help_requests(status: str = Query("pending", description="pending|accepted|resolved")):
    """Return help requests filtered by statusall pending help requests."""
    rows = list_help_requests(status=status)
    return [serialize_request(r) for r in rows]

@router.post("/help-requests/{request_id}/accept")
def accept_help_request(request_id: str, payload: dict):
    """
    Supervisor accepts (claims) a help request.
    Body must include 'user_id' (supervisor ID).
    """
    supervisor_id = payload.get("user_id")
    if not supervisor_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    success = atomic_accept(request_id, supervisor_id)

    if success:
        print(f"[SUPERVISOR]: Request {request_id} accepted by {supervisor_id}")
        return {"status": "accepted", "request_id": request_id, "accepted_by": supervisor_id}
    else:
        raise HTTPException(status_code=409, detail="Request already accepted or not found")    

@router.post("/help-requests/{request_id}/resolve")
def resolve_help_request_endpoint(request_id: str, payload: dict):
    """
    Supervisor resolves a help request.
    Body must include: { "user_id": "...", "resolution_text": "..." }
    This will create a KB entry, mark request resolved, and send follow-up to caller.
    """
    supervisor_id = payload.get("user_id")
    resolution_text = payload.get("resolution_text")
    if not supervisor_id or not resolution_text:
        raise HTTPException(status_code=400, detail="user_id and resolution_text required")

    try:
        kb = resolve_help_request(request_id, supervisor_id, resolution_text)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print("resolve_help_request error:", str(e))
        raise HTTPException(status_code=500, detail="Failed to resolve request")

    # Fetch caller_id to send follow-up (small separate session)
    from backend.db import SessionLocal as _Session
    from backend.models import HelpRequest as _HelpRequest
    s = _Session()
    try:
        req = s.query(_HelpRequest).filter(_HelpRequest.id == request_id).first()
        caller_id = req.caller_id if req else None
    finally:
        s.close()

    
    if caller_id:
        sent = send_followup_to_caller(caller_id, request_id, resolution_text)
        if not sent:
            print(f"[FOLLOWUP FAILED] request={request_id} caller={caller_id}")
    else:
        print(f"[FOLLOWUP SKIPPED] caller not found for request {request_id}")

    return {
        "status": "resolved",
        "request_id": request_id,
        "kb_id": kb.get("id"),
        "kb_question_snippet": kb.get("question_snippet"),
        "kb_answer_text": kb.get("answer_text")
    }