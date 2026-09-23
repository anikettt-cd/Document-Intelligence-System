import uuid
from fastapi import APIRouter, UploadFile, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.repositories import supabase, get_db
from app.db.models import Document

# Import from the correct service module
from app.services.ingestion_service import process_document

router = APIRouter()

@router.post("/api/v1/documents")
async def upload_document(
    file: UploadFile, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDFs are supported")
        
    doc_id = uuid.uuid4()
    storage_key = f"{doc_id}/original.pdf"
    
    file_bytes = await file.read()
    file_size = len(file_bytes)
    
    if file_size > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File exceeds 10MB limit")
    
    try:
        supabase.storage.from_("documents").upload(
            path=storage_key,
            file=file_bytes,
            file_options={"content-type": "application/pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Storage upload failed: {str(e)}")
    
    new_doc = Document(
        id=doc_id,
        filename=file.filename,
        storage_key=storage_key,
        mime_type=file.content_type,
        file_size=file_size,
        status="PROCESSING"
    )
    
    db.add(new_doc)
    db.commit()
    
    # Trigger background task
    background_tasks.add_task(process_document, str(doc_id), storage_key)
    
    return {
        "id": str(doc_id), 
        "filename": file.filename, 
        "status": "PROCESSING"
    }