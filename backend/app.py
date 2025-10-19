from fastapi import FastAPI
from .db import init_db

app = FastAPI(title="AI Helpdesk (backend)")

@app.on_event("startup")
def on_startup():
    # create tables if they don't exist
    init_db()

@app.get("/")
def root():
    return {"status": "ok", "message": "AI Helpdesk backend running"}
