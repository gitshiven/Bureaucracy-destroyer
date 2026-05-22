<p align="center">
  <img src="frontend/public/logo.png" alt="Bureaucracy Destroyer" width="80" />
</p>

<h1 align="center">🇮🇪 Bureaucracy Destroyer</h1>

> **Stop fearing official letters. We explain them.**

An agentic AI system that helps immigrants and residents in Ireland understand government documents — instantly, in their language, with action steps and a drafted response letter ready to send.

**Live:** [bureaucracy-destroyer.vercel.app](https://bureaucracy-destroyer.vercel.app) &nbsp;|&nbsp; **API:** [Railway](https://bureaucracy-destroyer-production-4c92.up.railway.app/docs)

---

## What it does

Upload any Irish government document — a photo or PDF — and the system:

1. **OCRs it** using AWS Textract (images) + PyMuPDF (PDFs, including encrypted ones)
2. **Classifies it** across 27+ document types — Revenue notice, HAP form, eviction notice, payslip, eFlow toll receipt, and more
3. **Explains it** in plain English, grounded in live citizensinformation.ie guidance via RAG
4. **Extracts deadlines** as structured calendar-ready dates
5. **Generates prioritised action steps** with official gov.ie links
6. **Drafts a formal response letter** personalised to the user's situation
7. **Translates everything** into any of 23 languages including Irish (Gaeilge)
8. **Logs evaluation signals** — RAG grounding, confidence score, processing time — on every run

---

## Architecture

```
User uploads PDF or photo
        ↓
AWS Textract (images) / PyMuPDF (PDFs)
        ↓
Claude claude-sonnet-4-5 — classify document type
        ↓
OpenAI text-embedding-3-small → pgvector cosine search
        ↓
RAG retrieval from citizensinformation.ie knowledge base
        ↓
Claude — explain + extract deadlines + action steps + draft letter
        ↓
Auto-detect language → translate if needed
        ↓
Eval logging → evaluations table (confidence, RAG grounding, time)
```

---

## Tech stack

| Layer | Tech |
|---|---|
| **LLM** | Claude claude-sonnet-4-5 (Anthropic) |
| **OCR** | AWS Textract + PyMuPDF |
| **Embeddings** | OpenAI text-embedding-3-small |
| **Vector search** | pgvector (cosine similarity) |
| **Backend** | FastAPI (Python 3.12) |
| **Database** | PostgreSQL + pgvector on Railway |
| **Frontend** | React + Vite (no component library) |
| **Deployment** | Railway (backend) + Vercel (frontend) |
| **Automation** | n8n (self-hosted Docker) |
| **Language detection** | langdetect (23 languages) |

---

## Document types supported

```
Revenue notices · Revenue assessments · HAP forms · PPS applications
DSP letters · Visa applications · Visa refusals · Employment permits
Eviction notices · Council tax · Utility bills · Rent bills
Payslips · Job offer letters · Toll payments (eFlow M50)
Grocery receipts · Shopping receipts · Lottery tickets
Bank letters · Debt collection · Medical cards · Driving licences
Motor tax · OPW forms · HSE letters · Immigration documents
```

---

## Key design decisions

**Why RAG instead of pure LLM?**
Irish government guidance changes — rent caps, DSP payment rates, visa rules. RAG grounds every answer in weekly-refreshed citizensinformation.ie content rather than LLM training data. The eval layer tracks RAG grounding on every run.

**Why Textract + PyMuPDF?**
PyMuPDF handles digital PDFs (including encrypted ones with blank passwords) instantly and free. Textract handles photos taken on phones — the primary real-world use case for immigrants. The pipeline routes intelligently between them.

**Why eval logging?**
Every analysis run logs confidence band (high/medium/low), RAG chunks retrieved, grounding signal, letter drafted, language, and processing time to a Postgres `evaluations` table. This makes output quality measurable, not just observable.

---

## Local setup

**Prerequisites:** Docker Desktop, Python 3.12, Node 18+, API keys for Anthropic + OpenAI + AWS

```bash
# Clone
git clone https://github.com/gitshiven/Bureaucracy-destroyer.git
cd Bureaucracy-destroyer

# Start Docker stack (Postgres + pgvector, Redis, n8n)
docker compose up -d

# Backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env      # fill in your API keys

# Run schema
docker exec -it bureaucracy-destroyer-db-1 psql -U postgres -d bureaucracy_destroyer < schema.sql

# Seed knowledge base
python scripts/seed_knowledge_base.py

# Start backend
uvicorn app.main:app --reload
# → http://localhost:8000/docs

# Frontend (new terminal)
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

---

## Environment variables

```env
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=eu-west-1
USE_TEXTRACT=true
PGVECTOR_ENABLED=true
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/bureaucracy_destroyer
ENVIRONMENT=development
SECRET_KEY=
```

---

## API endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/upload` | OCR + classify + language detect |
| `POST` | `/analyse` | RAG + Claude explanation + letter |
| `POST` | `/translate` | Translate existing analysis |
| `GET` | `/languages` | List supported languages |
| `GET` | `/` | Health check |

Full interactive docs at `/docs` (Swagger UI).

---

## Database schema

```
users           — phone, preferred language, country of origin
documents       — raw text, doc type, OCR source, detected language
analyses        — explanation, action steps (JSONB), deadlines, letter, confidence
reminders       — deadline date, delivery channel, send_at, sent
knowledge_base  — citizensinformation.ie chunks, vector(1536) embeddings
evaluations     — confidence band, RAG grounding, processing time per run
```

---

## Knowledge base

Seeded from citizensinformation.ie covering:

- Government & tax (Revenue, DSP, HAP, PPS, LPT)
- Immigration & visas (IRP, employment permits, residence)
- Housing (eviction, rent, RTB)
- Employment (payslips, PAYE, PRSI, USC, job offers)
- Health (medical cards, HSE, GP visit cards)
- Transport (M50 toll, motor tax, driving licence)
- Finance (banking, debt, MABS)
- Shopping & utilities (ESB, Gas Networks, water)

~200+ chunks, refreshable via `python scripts/seed_knowledge_base.py`.

---

## Interview answer

> *"The LLM is just the reasoning layer. The value is in the pipeline — OCR routing, RAG grounding on real Irish law, structured deadline extraction, 23-language detection, and an eval layer that measures whether answers are grounded in retrieved context or generated from prior knowledge."*

---

## Roadmap

- [ ] Twilio WhatsApp reminders (7/3/1 days before extracted deadlines)
- [ ] n8n cron workflow for automated reminder firing
- [ ] Document history page
- [ ] Weekly knowledge base refresh via n8n
- [ ] Confidence score visualisation on results screen
- [ ] Multi-turn conversational follow-up agent

---

## Built with

- [Anthropic Claude](https://anthropic.com) — document understanding and letter drafting
- [AWS Textract](https://aws.amazon.com/textract/) — OCR for photos and scanned documents
- [citizensinformation.ie](https://www.citizensinformation.ie) — Irish government guidance (RAG source)
- [Railway](https://railway.app) — backend + Postgres hosting
- [Vercel](https://vercel.com) — frontend hosting

---

*Built for immigrants navigating Irish bureaucracy. Because nobody should fear a letter from Revenue.*
