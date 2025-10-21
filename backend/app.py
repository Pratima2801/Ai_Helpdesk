from fastapi import FastAPI
from .db import init_db
from backend.routes import incoming, help_requests, kb

app = FastAPI(title="AI Helpdesk (backend)")

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(incoming.router)
app.include_router(help_requests.router)
app.include_router(kb.router)

@app.get("/")
def root():
    return {"status": "ok", "message": "AI Helpdesk backend running"}
