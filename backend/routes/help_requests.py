from fastapi import APIRouter, Query
from backend.crud import list_help_requests
from fastapi import HTTPException
from backend.crud import atomic_accept
from typing import List

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
