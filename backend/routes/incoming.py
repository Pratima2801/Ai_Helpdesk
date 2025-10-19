from fastapi import APIRouter
from backend.crud import create_help_request
from backend.simulated_webhooks import send_ack_to_caller
from backend.services.livekit_stub import create_room_and_join_agent

router = APIRouter()

@router.post("/incoming-call")
def incoming_call(payload: dict):
    """
    Simulate a caller contacting the AI agent.
    Creates help request if AI doesn't know answer.
    """
    caller_id = payload.get("caller_id", "unknown")
    caller_phone = payload.get("caller_phone", "N/A")
    transcript = payload.get("transcript", "")
    question_text = payload.get("question_text", "")

    # Simulate connecting via LiveKit
    room_id = create_room_and_join_agent(caller_id)

    # Create help request
    new_request = create_help_request(caller_id, caller_phone, transcript, question_text)

    # Send immediate acknowledgment to caller (simulated)
    send_ack_to_caller(caller_id, new_request.id)

    return {
        "status": "pending",
        "request_id": new_request.id,
        "room_id": room_id,
        "message": "Help request created and caller acknowledged."
    }
