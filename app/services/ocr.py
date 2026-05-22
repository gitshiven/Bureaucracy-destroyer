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


def extract_text_from_bytes(image_bytes: bytes) -> str:
    try:
        client = get_textract_client()
        response = client.detect_document_text(
            Document={'Bytes': image_bytes}
        )
        blocks = response.get('Blocks', [])
        lines = [b['Text'] for b in blocks if b['BlockType'] == 'LINE']
        return '\n'.join(lines)
    except Exception as e:
        print(f"Textract failed: {e}")
        return ""


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    try:
        import fitz
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        if doc.is_encrypted:
            doc.authenticate("")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        if text.strip():
            return text.strip()
        return extract_text_from_bytes(pdf_bytes)
    except Exception as e:
        print(f"PyMuPDF failed: {e}, trying Textract")
        return extract_text_from_bytes(pdf_bytes)


def extract_text(file_bytes: bytes, filename: str) -> tuple:
    filename_lower = filename.lower()
    if filename_lower.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes), "pymupdf+textract"
    elif filename_lower.endswith((".jpg", ".jpeg", ".png", ".tiff", ".bmp")):
        return extract_text_from_bytes(file_bytes), "textract"
    else:
        return "", "unknown"