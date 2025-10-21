from fastapi import APIRouter
from backend.db import SessionLocal
from backend.models import KBEntry

router = APIRouter()

@router.get("/kb")
def list_kb():
    db = SessionLocal()
    try:
        rows = db.query(KBEntry).order_by(KBEntry.created_at.desc()).all()
        result = []
        for r in rows:
            result.append({
                "id": r.id,
                "question_snippet": r.question_snippet,
                "answer_text": r.answer_text,
                "source_request_id": r.source_request_id,
                "created_by": r.created_by,
                "created_at": r.created_at.isoformat() if r.created_at else None
            })
        return result
    finally:
        db.close()
