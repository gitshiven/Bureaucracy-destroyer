from sqlalchemy import text
from app.database import get_db
import uuid
import json

def log_evaluation(
    analysis_id: str,
    doc_type: str,
    confidence_score: float,
    context_chunks_count: int,
    used_web_search: bool = False,
    letter_drafted: bool = False,
    language: str = "en",
    processing_time_ms: int = 0
):
    """Log quality signals for every agent run."""
    db = next(get_db())
    try:
        grounding_signal = "high" if context_chunks_count >= 3 else \
                          "medium" if context_chunks_count >= 1 else "low"

        confidence_band = "high" if confidence_score >= 0.8 else \
                         "medium" if confidence_score >= 0.5 else "low"

        db.execute(text("""
            INSERT INTO evaluations (
                id, analysis_id, doc_type, confidence_score,
                confidence_band, rag_chunks_retrieved,
                grounding_signal, letter_drafted,
                language, processing_time_ms, created_at
            )
            VALUES (
                :id, :analysis_id, :doc_type, :confidence,
                :confidence_band, :chunks,
                :grounding, :letter_drafted,
                :language, :processing_time, NOW()
            )
        """), {
            "id": str(uuid.uuid4()),
            "analysis_id": analysis_id,
            "doc_type": doc_type,
            "confidence": confidence_score,
            "confidence_band": confidence_band,
            "chunks": context_chunks_count,
            "grounding": grounding_signal,
            "letter_drafted": letter_drafted,
            "language": language,
            "processing_time": processing_time_ms
        })
        db.commit()
        print(f"📊 Eval logged — confidence: {confidence_band}, RAG: {grounding_signal}, chunks: {context_chunks_count}")
    except Exception as e:
        print(f"⚠️ Eval logging failed: {e}")
        db.rollback()