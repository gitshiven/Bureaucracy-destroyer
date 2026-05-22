import anthropic
import json
from app.config import settings
from app.utils.prompts import EXPLANATION_PROMPT, LETTER_PROMPT, CLASSIFIER_PROMPT

client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)


def clean_json_response(raw: str) -> str:
    """Strip markdown code blocks from LLM response."""
    clean = raw.strip()
    if clean.startswith("```"):
        parts = clean.split("```")
        if len(parts) >= 3:
            clean = parts[1]
        elif len(parts) == 2:
            clean = parts[1]
        if clean.startswith("json"):
            clean = clean[4:]
    return clean.strip()


def classify_document(raw_text: str) -> str:
    """Use Claude to classify the document type."""
    prompt = CLASSIFIER_PROMPT.format(text_sample=raw_text[:500])

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=50,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()


def explain_document(
    raw_text: str,
    doc_type: str,
    context_chunks: list,
    target_language: str = "en"
) -> dict:
    """Main analysis — returns structured explanation."""
    context = "\n\n".join(context_chunks) if context_chunks else "No context available."

    prompt = EXPLANATION_PROMPT.format(
        doc_type=doc_type,
        raw_text=raw_text,
        context=context,
        language=target_language
    )

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.content[0].text
    try:
        clean = clean_json_response(raw)
        return json.loads(clean)
    except json.JSONDecodeError:
        return {
            "explanation": raw,
            "action_steps": [],
            "extracted_deadlines": [],
            "confidence_score": 0.5
        }


def draft_letter(
    doc_type: str,
    context: str,
    user_situation: str,
    language: str = "en"
) -> str:
    """Draft a formal response letter."""
    prompt = LETTER_PROMPT.format(
        doc_type=doc_type,
        context=context,
        situation=user_situation,
        language=language
    )
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text