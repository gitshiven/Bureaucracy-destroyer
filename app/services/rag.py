import openai
from sqlalchemy import text
from app.database import get_db
from app.config import settings

openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

def get_embedding(query: str) -> list:
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=query[:8000]
    )
    return response.data[0].embedding

def retrieve_context(query: str, form_type: str, top_k: int = 4) -> list:
    """
    Semantic search over knowledge_base.
    Tries form-type filtered first, falls back to general search.
    Returns list of relevant text chunks.
    """
    embedding = get_embedding(query)
    embedding_str = f"[{','.join(map(str, embedding))}]"

    db = next(get_db())

    # Try form-specific first
    result = db.execute(text("""
        SELECT raw_content,
               1 - (embedding <=> cast(:emb as vector)) AS similarity
        FROM knowledge_base
        WHERE form_type = :form_type
          AND expires_at > NOW()
        ORDER BY embedding <=> cast(:emb as vector)
        LIMIT :k
    """), {"emb": embedding_str, "form_type": form_type, "k": top_k})

    rows = result.fetchall()

    # Fall back to general search if not enough results
    if len(rows) < 2:
        result = db.execute(text("""
            SELECT raw_content,
                   1 - (embedding <=> cast(:emb as vector)) AS similarity
            FROM knowledge_base
            WHERE expires_at > NOW()
            ORDER BY embedding <=> cast(:emb as vector)
            LIMIT :k
        """), {"emb": embedding_str, "k": top_k})
        rows = result.fetchall()

    return [row[0] for row in rows if row[1] > 0.3]