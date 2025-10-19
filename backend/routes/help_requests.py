from fastapi import APIRouter
from backend.crud import list_help_requests

router = APIRouter()

@router.get("/help-requests")
def get_help_requests():
    """Return all pending help requests."""
    requests = list_help_requests()
    return requests
