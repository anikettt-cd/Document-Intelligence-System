import traceback
from app.db.repositories import SessionLocal, supabase
from app.db.models import Document, Page, Section, Chunk

# Updated imports to match your architecture
from app.documents.parser import extract_pdf_pages
from app.documents.cleaner import clean_page_text
from app.documents.structure import detect_document_sections
from app.services.chunking_service import create_chunks

def process_document(document_id: str, storage_key: str):
    db = SessionLocal()
    try:
        response = supabase.storage.from_("documents").download(storage_key)
        
        raw_pages = extract_pdf_pages(response)
        cleaned_pages = clean_page_text(raw_pages)
        sections_data = detect_document_sections(cleaned_pages)
        chunks_data = create_chunks(cleaned_pages, document_id)
        
        doc = db.query(Document).filter(Document.id == document_id).first()
        doc.page_count = len(cleaned_pages)
        
        db_pages = [Page(
            document_id=document_id,
            page_number=p["page_number"],
            raw_text=p["raw_text"],
            cleaned_text=p["cleaned_text"]
        ) for p in cleaned_pages]
        db.bulk_save_objects(db_pages)
        db.commit()
        
        page_map = {p.page_number: p.id for p in db.query(Page).filter_by(document_id=document_id).all()}
        
        db_sections = []
        for s in sections_data:
            page_id = page_map.get(s["temp_page_number"])
            db_sections.append(Section(
                document_id=document_id,
                page_id=page_id,
                title=s["title"],
                level=s["level"],
                section_path=s["section_path"]
            ))
        db.bulk_save_objects(db_sections)
        db.commit()
        
        section_map = {s.title: s.id for s in db.query(Section).filter_by(document_id=document_id).all()}
        
        db_chunks = []
        for c in chunks_data:
            page_id = page_map.get(c["page_number"])
            section_id = section_map.get(c["section_title"])
            db_chunks.append(Chunk(
                document_id=document_id,
                page_id=page_id,
                section_id=section_id,
                chunk_index=c["chunk_index"],
                content=c["content"],
                token_count=c["token_count"]
            ))
        db.bulk_save_objects(db_chunks)
        
        doc.status = "READY"
        db.commit()
        
    except Exception as e:
        db.rollback()
        error_msg = str(e)
        print(f"Ingestion Error: {error_msg}\n{traceback.format_exc()}")
        
        doc = db.query(Document).filter(Document.id == document_id).first()
        if doc:
            doc.status = "FAILED"
            doc.error_message = error_msg[:500]
            db.commit()
    finally:
        db.close()