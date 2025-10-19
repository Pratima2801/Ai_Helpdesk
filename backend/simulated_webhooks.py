import json

def send_ack_to_caller(caller_id: str, request_id: str):
    """Simulate sending an acknowledgment message to the caller."""
    message = {
        "caller_id": caller_id,
        "request_id": request_id,
        "message": "Thanks — I'm escalating this to a human. Someone will get back to you shortly."
    }
    print("[TO CALLER]:", json.dumps(message, indent=2))
