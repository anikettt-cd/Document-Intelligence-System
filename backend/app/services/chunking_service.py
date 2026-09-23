import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter

tokenizer = tiktoken.get_encoding("cl100k_base")

def tiktoken_len(text: str) -> int:
    return len(tokenizer.encode(text, disallowed_special=()))

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=75,
    length_function=tiktoken_len,
    separators=["\n\n", "\n", ".", " ", ""]
)

def create_chunks(pages: list[dict], document_id: str) -> list[dict]:
    chunks = []
    chunk_index = 0
    
    for page in pages:
        text = page.get("cleaned_text", "")
        if not text:
            continue
            
        page_chunks = text_splitter.split_text(text)
        
        for content in page_chunks:
            chunks.append({
                "document_id": document_id,
                "page_number": page.get("page_number"),
                "section_title": page.get("section_title"),
                "chunk_index": chunk_index,
                "content": content,
                "token_count": tiktoken_len(content)
            })
            chunk_index += 1
            
    return chunks