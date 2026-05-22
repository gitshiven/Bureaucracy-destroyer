import boto3
import io
from app.config import settings

def get_textract_client():
    return boto3.client(
        'textract',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )

def extract_text_from_bytes(file_bytes: bytes) -> str:
    """Extract text using AWS Textract."""
    client = get_textract_client()
    
    response = client.detect_document_text(
        Document={'Bytes': file_bytes}
    )
    
    blocks = response.get('Blocks', [])
    lines = [
        block['Text'] 
        for block in blocks 
        if block['BlockType'] == 'LINE'
    ]
    return '\n'.join(lines)

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract text from PDF using PyMuPDF first (free), Textract as fallback."""
    try:
        import fitz
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        if text.strip():
            return text.strip()
        # If no text extracted (scanned PDF), fall back to Textract
        return extract_text_from_bytes(pdf_bytes)
    except Exception:
        return extract_text_from_bytes(pdf_bytes)

def extract_text(file_bytes: bytes, filename: str) -> tuple[str, str]:
    """
    Route to correct extractor based on file type.
    Returns (text, ocr_source)
    """
    filename_lower = filename.lower()

    if filename_lower.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes), "pymupdf+textract"
    elif filename_lower.endswith((".jpg", ".jpeg", ".png", ".tiff", ".bmp")):
        return extract_text_from_bytes(file_bytes), "textract"
    else:
        return "", "unknown"