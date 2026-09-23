import re

def detect_document_sections(pages: list[dict]) -> list[dict]:
    sections = []
    current_section = {
        "title": "Document Start",
        "level": 1,
        "section_path": "Document Start",
        "temp_page_number": 1
    }
    
    heading_pattern = re.compile(r'^(\d+(?:\.\d+)*)\s+([A-Z].+)$', re.MULTILINE)
    
    for page in pages:
        text = page["cleaned_text"]
        for match in heading_pattern.finditer(text):
            numbering = match.group(1)
            title = match.group(2).strip()
            
            if len(title) > 120:
                continue
                
            level = len(numbering.split('.'))
            path = title if level == 1 else f"{current_section['title']} > {title}"
                
            current_section = {
                "title": f"{numbering} {title}",
                "level": level,
                "section_path": path,
                "temp_page_number": page["page_number"]
            }
            sections.append(current_section)
            
        page["section_path"] = current_section["section_path"]
        page["section_title"] = current_section["title"]
        
    if not sections:
        sections.append(current_section)
        
    return sections