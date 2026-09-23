import re

def clean_page_text(pages: list[dict]) -> list[dict]:
    for page in pages:
        text = page["raw_text"]
        text = text.replace("\x00", "")
        text = re.sub(r'([a-zA-Z]+)-\n([a-zA-Z]+)', r'\1\2', text)
        text = re.sub(r'(?m)^Page \d+ of \d+$', '', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'(?<![.:!?])\n(?=[a-z])', ' ', text)
        page["cleaned_text"] = text.strip()
        
    return pages