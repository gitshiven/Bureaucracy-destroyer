from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.ocr import extract_text
from app.services.llm import classify_document
from app.services.language_detector import detect_language
from app.database import get_db
from sqlalchemy import text
import uuid

router = APIRouter()

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document (PDF or image).
    Returns document_id + extracted text + detected doc type + detected language.
    """
    # Read file
    file_bytes = await file.read()
    filename = file.filename

    # Validate file type
    allowed = [".pdf", ".jpg", ".jpeg", ".png", ".tiff", ".bmp"]
    if not any(filename.lower().endswith(ext) for ext in allowed):
        raise HTTPException(status_code=400, detail="File type not supported")

    # Extract text
    raw_text, ocr_source = extract_text(file_bytes, filename)

    if not raw_text:
        raise HTTPException(status_code=422, detail="Could not extract text from document")

    # Classify document type
    doc_type = classify_document(raw_text)

    # Auto detect language
    detected_language = detect_language(raw_text)

    # Save to database
    document_id = str(uuid.uuid4())
    db = next(get_db())
    db.execute(text("""
        INSERT INTO documents (
            id, doc_type, raw_text, ocr_source, 
            original_filename, detected_language
        )
        VALUES (
            :id, :doc_type, :raw_text, :ocr_source, 
            :filename, :language
        )
    """), {
        "id": document_id,
        "doc_type": doc_type,
        "raw_text": raw_text,
        "ocr_source": ocr_source,
        "filename": filename,
        "language": detected_language
    })
    db.commit()

    return {
        "document_id": document_id,
        "doc_type": doc_type,
        "ocr_source": ocr_source,
        "detected_language": detected_language,
        "text_preview": raw_text[:200],
        "status": "uploaded"
    }