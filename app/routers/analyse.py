from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.llm import explain_document, draft_letter
from app.services.rag import retrieve_context
from app.services.evaluator import log_evaluation
from app.database import get_db
from sqlalchemy import text
import uuid
import json
import time

router = APIRouter()

class AnalyseRequest(BaseModel):
    document_id: str
    target_language: str = "auto"
    user_situation: str = ""

@router.post("/analyse")
def analyse_document(request: AnalyseRequest):
    db = next(get_db())

    result = db.execute(text("""
        SELECT id, doc_type, raw_text, detected_language
        FROM documents WHERE id = :id
    """), {"id": request.document_id}).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="Document not found")

    doc_id, doc_type, raw_text, detected_language = result

    language = detected_language if request.target_language == "auto" else request.target_language

    start_time = time.time()

    # RAG retrieval
    context_chunks = retrieve_context(raw_text[:500], doc_type)
    print(f"RAG retrieved {len(context_chunks)} chunks for {doc_type}")

    # Claude analysis
    analysis = explain_document(
        raw_text=raw_text,
        doc_type=doc_type,
        context_chunks=context_chunks,
        target_language=language
    )

    # Draft letter if situation provided
    letter = ""
    if request.user_situation:
        letter = draft_letter(
            doc_type=doc_type,
            context=analysis.get("explanation", ""),
            user_situation=request.user_situation,
            language=language
        )

    processing_time = int((time.time() - start_time) * 1000)

    analysis_id = str(uuid.uuid4())
    action_steps = analysis.get("action_steps", [])
    deadlines = analysis.get("extracted_deadlines", [])

    # Save analysis
    db.execute(text("""
        INSERT INTO analyses (
            id, document_id, plain_english_explanation,
            action_steps, extracted_deadlines,
            drafted_letter, llm_model_used, confidence_score
        )
        VALUES (
            :id, :doc_id, :explanation,
            cast(:action_steps as jsonb), cast(:deadlines as jsonb),
            :letter, :model, :confidence
        )
    """), {
        "id": analysis_id,
        "doc_id": str(doc_id),
        "explanation": analysis.get("explanation", ""),
        "action_steps": json.dumps(action_steps),
        "deadlines": json.dumps(deadlines),
        "letter": letter,
        "model": "claude-sonnet-4-5",
        "confidence": analysis.get("confidence_score", 0.5)
    })
    db.commit()

    # Log eval
    log_evaluation(
        analysis_id=analysis_id,
        doc_type=doc_type,
        confidence_score=analysis.get("confidence_score", 0.5),
        context_chunks_count=len(context_chunks),
        letter_drafted=bool(letter),
        language=language,
        processing_time_ms=processing_time
    )

    return {
        "analysis_id": analysis_id,
        "doc_type": doc_type,
        "detected_language": language,
        "explanation": analysis.get("explanation"),
        "action_steps": action_steps,
        "extracted_deadlines": deadlines,
        "drafted_letter": letter,
        "confidence_score": analysis.get("confidence_score"),
        "rag_chunks_used": len(context_chunks),
        "processing_time_ms": processing_time
    }