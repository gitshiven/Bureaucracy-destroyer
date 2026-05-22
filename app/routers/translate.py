from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.database import get_db
from app.services.llm import explain_document
from sqlalchemy import text

router = APIRouter()

AVAILABLE_LANGUAGES = {
    "en": "English", "ga": "Irish (Gaeilge)", "pl": "Polish",
    "ro": "Romanian", "pt": "Portuguese", "es": "Spanish",
    "fr": "French", "de": "German", "it": "Italian",
    "ar": "Arabic", "hi": "Hindi", "ur": "Urdu",
    "zh": "Chinese", "fil": "Filipino", "lt": "Lithuanian",
    "lv": "Latvian", "uk": "Ukrainian", "ru": "Russian",
    "cs": "Czech", "sk": "Slovak", "hu": "Hungarian",
    "bg": "Bulgarian", "hr": "Croatian"
}

class TranslateRequest(BaseModel):
    analysis_id: str
    target_language: str

@router.get("/languages")
def get_languages():
    return {"languages": AVAILABLE_LANGUAGES}

@router.post("/translate")
def translate_analysis(request: TranslateRequest):
    if request.target_language not in AVAILABLE_LANGUAGES:
        raise HTTPException(status_code=400, detail="Language not supported")

    db = next(get_db())
    result = db.execute(text("""
        SELECT a.plain_english_explanation, d.raw_text, d.doc_type
        FROM analyses a
        JOIN documents d ON d.id = a.document_id
        WHERE a.id = :id
    """), {"id": request.analysis_id}).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="Analysis not found")

    explanation, raw_text, doc_type = result

    analysis = explain_document(
        raw_text=raw_text,
        doc_type=doc_type,
        context_chunks=[],
        target_language=request.target_language
    )

    return {
        "analysis_id": request.analysis_id,
        "target_language": request.target_language,
        "language_name": AVAILABLE_LANGUAGES[request.target_language],
        "explanation": analysis.get("explanation"),
        "action_steps": analysis.get("action_steps"),
        "extracted_deadlines": analysis.get("extracted_deadlines"),
        "confidence_score": analysis.get("confidence_score")
    }