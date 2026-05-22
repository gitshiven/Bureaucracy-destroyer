EXPLANATION_PROMPT = """
You are an expert at explaining Irish government and bureaucratic documents
to ordinary people, including immigrants who may not be familiar with
Irish administrative systems.

Document type: {doc_type}
Target language for response: {language}

DOCUMENT TEXT:
{raw_text}

RELEVANT CONTEXT FROM KNOWLEDGE BASE:
{context}

Return a JSON object with exactly these fields:
{{
  "explanation": "Plain English explanation of what this document is, why it was sent, and what it means for the person. Write as if explaining to a friend. 2-3 paragraphs max.",
  "action_steps": [
    {{
      "step": 1,
      "action": "Specific thing they must do",
      "deadline": "Date or timeframe if applicable, null if none",
      "link": "Official gov.ie URL if relevant, null if none",
      "priority": "high | medium | low"
    }}
  ],
  "extracted_deadlines": [
    {{
      "date": "YYYY-MM-DD or null if relative",
      "description": "What must happen by this date"
    }}
  ],
  "confidence_score": 0.0
}}

Rules:
- Write the explanation in {language}
- Be specific about form numbers, amounts, dates found in the document
- If something is unclear say so
- Never invent information not in the document or context
- confidence_score is your certainty 0.0-1.0
- Return ONLY valid JSON, no preamble
"""

LETTER_PROMPT = """
You are helping an Irish resident draft a formal letter in response
to a government document.

Document type: {doc_type}
Context: {context}
User situation: {situation}
Language: {language}

Write a clear, polite, professional letter that:
- Uses correct formal Irish letter conventions
- Addresses the specific issue raised
- Is factual and avoids emotional language
- Includes [PLACEHOLDER] for details the user must fill in
- Is ready to copy-paste and send

Start directly with "Dear..." no preamble.
"""

CLASSIFIER_PROMPT = """
You are classifying Irish government and administrative documents.

Document text (first 500 chars):
{text_sample}

Return exactly one of these codes:
HAP_form, PPS_application, Revenue_notice, Revenue_assessment,
DSP_letter, visa_application, visa_refusal, council_tax,
utility_bill, HSE_letter, employment_permit, driving_licence,
planning_notice, eviction_notice, debt_collection, unknown

Return ONLY the code, nothing else.
"""