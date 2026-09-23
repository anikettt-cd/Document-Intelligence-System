# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import documents
from app.db.repositories import engine
from app.db import models

# Ensure tables exist (Alembic is better, but this works for rapid MVP dev)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Enterprise Document Intelligence API")

# Allow the React frontend to communicate with this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with your Vercel/Localhost URL later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}