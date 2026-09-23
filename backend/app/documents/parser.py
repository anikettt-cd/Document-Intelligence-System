import pymupdf as fitz

def extract_pdf_pages(file_bytes: bytes) -> list[dict]:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    extracted_pages = []
    
    for page_num, page in enumerate(doc, start=1):
        extracted_pages.append({
            "page_number": page_num,
            "raw_text": page.get_text("text")
        })
        
    doc.close()
    return extracted_pages