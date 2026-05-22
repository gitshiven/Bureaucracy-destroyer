import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from bs4 import BeautifulSoup
import tiktoken
import openai
from sqlalchemy import text
from app.database import get_db
from app.config import settings
import time

openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

IRISH_KNOWLEDGE = [
    # --- GOVERNMENT & IMMIGRATION ---
    {
        "form_type": "HAP_form",
        "urls": [
            "https://www.citizensinformation.ie/en/housing/renting-a-home/help-with-renting/housing-assistance-payment/",
        ]
    },
    {
        "form_type": "PPS_application",
        "urls": [
            "https://www.citizensinformation.ie/en/social-welfare/irish-social-welfare-system/personal-public-service-number/",
        ]
    },
    {
        "form_type": "Revenue_notice",
        "urls": [
            "https://www.citizensinformation.ie/en/money-and-tax/tax/income-tax/how-your-tax-is-calculated/",
            "https://www.citizensinformation.ie/en/money-and-tax/tax/income-tax/tax-return-non-paye-income/",
        ]
    },
    {
        "form_type": "DSP_letter",
        "urls": [
            "https://www.citizensinformation.ie/en/social-welfare/social-welfare-payments/unemployed-people/jobseekers-allowance/",
        ]
    },
    {
        "form_type": "visa_application",
        "urls": [
            "https://www.citizensinformation.ie/en/moving-country/visas-for-ireland/visa-requirements-for-entering-ireland/",
            "https://www.citizensinformation.ie/en/moving-country/moving-to-ireland/coming-to-live-in-ireland/",
        ]
    },
    {
        "form_type": "HSE_letter",
        "urls": [
            "https://www.citizensinformation.ie/en/health/health-services/gp-and-hospital-services/gp-services-to-medical-card-holders/",
            "https://www.citizensinformation.ie/en/health/medical-cards-and-gp-visit-cards/medical-card/",
        ]
    },
    {
        "form_type": "employment_permit",
        "urls": [
            "https://www.citizensinformation.ie/en/moving-country/working-in-ireland/employment-permits/overview-employment-permits/",
            "https://www.citizensinformation.ie/en/moving-country/working-in-ireland/employment-permits/work-permits/",
        ]
    },
    {
        "form_type": "eviction_notice",
        "urls": [
            "https://www.citizensinformation.ie/en/housing/renting-a-home/tenants-rights-and-responsibilities/if-your-landlord-wants-you-to-leave/",
            "https://www.citizensinformation.ie/en/housing/renting-a-home/tenants-rights-and-responsibilities/tenants-rights-and-obligations/",
        ]
    },
    {
        "form_type": "council_tax",
        "urls": [
            "https://www.citizensinformation.ie/en/money-and-tax/tax/housing-taxes-and-reliefs/local-property-tax/",
        ]
    },
    {
        "form_type": "opw_form",
        "urls": [
            "https://www.citizensinformation.ie/en/government-in-ireland/ireland-and-the-uk/",
            "https://www.citizensinformation.ie/en/government-in-ireland/how-government-works/standards-and-accountability/",
        ]
    },

    # --- EMPLOYMENT & PAYSLIP ---
    {
        "form_type": "payslip",
        "urls": [
            "https://www.citizensinformation.ie/en/employment/employment-rights-and-conditions/pay-and-employment/pay-slip/",
            "https://www.citizensinformation.ie/en/money-and-tax/tax/income-tax/understanding-your-paye-tax/",
            "https://www.citizensinformation.ie/en/social-welfare/irish-social-welfare-system/social-insurance-prsi/social-insurance/",
        ]
    },
    {
        "form_type": "job_offer_letter",
        "urls": [
            "https://www.citizensinformation.ie/en/employment/employment-rights-and-conditions/contracts-of-employment/contract-of-employment/",
            "https://www.citizensinformation.ie/en/employment/employment-rights-and-conditions/pay-and-employment/minimum-wage/",
            "https://www.citizensinformation.ie/en/employment/starting-work-and-changing-job/starting-work/tax-and-starting-work/",
        ]
    },

    # --- UTILITIES & BILLS ---
    {
        "form_type": "utility_bill",
        "urls": [
            "https://www.citizensinformation.ie/en/consumer/utilities/electricity-services/",
            "https://www.citizensinformation.ie/en/consumer/utilities/gas-services/",
            "https://www.citizensinformation.ie/en/consumer/utilities/water-charges/",
        ]
    },
    {
        "form_type": "rent_bill",
        "urls": [
            "https://www.citizensinformation.ie/en/housing/renting-a-home/tenants-rights-and-responsibilities/tenants-rights-and-obligations/",
            "https://www.citizensinformation.ie/en/housing/renting-a-home/help-with-renting/rent-supplement/",
            "https://www.citizensinformation.ie/en/housing/renting-a-home/tenants-rights-and-responsibilities/rent-increases-in-private-rented-housing/",
        ]
    },

    # --- TRANSPORT & TOLLS ---
    {
        "form_type": "toll_payment",
        "urls": [
            "https://www.citizensinformation.ie/en/travel-and-recreation/roads-and-motorways/tolls-on-motorways-and-national-roads/",
            "https://www.citizensinformation.ie/en/travel-and-recreation/public-transport/public-transport-in-ireland/",
        ]
    },

    # --- SHOPPING & RECEIPTS ---
    {
        "form_type": "grocery_bill",
        "urls": [
            "https://www.citizensinformation.ie/en/consumer/shopping/consumer-rights-and-shopping/",
            "https://www.citizensinformation.ie/en/consumer/shopping/rights-when-buying-in-a-shop/",
            "https://www.citizensinformation.ie/en/money-and-tax/tax/tax-on-goods-and-services/vat-and-your-consumer-rights/",
        ]
    },
    {
        "form_type": "shopping_receipt",
        "urls": [
            "https://www.citizensinformation.ie/en/consumer/shopping/rights-when-buying-in-a-shop/",
            "https://www.citizensinformation.ie/en/consumer/shopping/consumer-rights-and-shopping/",
        ]
    },

    # --- GAMBLING & LOTTERY ---
    {
        "form_type": "lottery_ticket",
        "urls": [
            "https://www.citizensinformation.ie/en/money-and-tax/tax/income-tax/taxation-of-income-from-lottery-and-gambling/",
            "https://www.citizensinformation.ie/en/consumer/financial-products/gambling/",
        ]
    },

    # --- IMMIGRATION SPECIFIC ---
    {
        "form_type": "immigration_document",
        "urls": [
            "https://www.citizensinformation.ie/en/moving-country/moving-to-ireland/rights-of-residence-in-ireland/",
            "https://www.citizensinformation.ie/en/moving-country/moving-to-ireland/coming-to-live-in-ireland/",
            "https://www.citizensinformation.ie/en/moving-country/irish-citizenship/becoming-an-irish-citizen-through-naturalisation/",
        ]
    },
    {
        "form_type": "visa_refusal",
        "urls": [
            "https://www.citizensinformation.ie/en/moving-country/visas-for-ireland/visa-requirements-for-entering-ireland/",
            "https://www.citizensinformation.ie/en/moving-country/moving-to-ireland/rights-of-residence-in-ireland/",
        ]
    },

    # --- BANKING & FINANCE ---
    {
        "form_type": "bank_letter",
        "urls": [
            "https://www.citizensinformation.ie/en/money-and-tax/personal-finance/banking/opening-a-bank-account/",
            "https://www.citizensinformation.ie/en/consumer/financial-products/bank-accounts/",
        ]
    },
    {
        "form_type": "debt_collection",
        "urls": [
            "https://www.citizensinformation.ie/en/money-and-tax/personal-finance/debt/dealing-with-debt/",
            "https://www.citizensinformation.ie/en/money-and-tax/personal-finance/debt/mabs-debt-advice/",
        ]
    },

    # --- HEALTH ---
    {
        "form_type": "medical_card",
        "urls": [
            "https://www.citizensinformation.ie/en/health/medical-cards-and-gp-visit-cards/medical-card/",
            "https://www.citizensinformation.ie/en/health/medical-cards-and-gp-visit-cards/gp-visit-cards/",
        ]
    },

    # --- DRIVING ---
    {
        "form_type": "driving_licence",
        "urls": [
            "https://www.citizensinformation.ie/en/travel-and-recreation/motoring/driver-licensing/full-driving-licence/",
            "https://www.citizensinformation.ie/en/travel-and-recreation/motoring/driver-licensing/exchanging-foreign-driving-permit/",
        ]
    },
    {
        "form_type": "motor_tax",
        "urls": [
            "https://www.citizensinformation.ie/en/travel-and-recreation/motoring/motor-tax-and-insurance/motor-tax-rates/",
        ]
    },
]


def scrape_page(url: str) -> str:
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; BureaucracyDestroyer/1.0)"}
        res = requests.get(url, headers=headers, timeout=15)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        for tag in soup(["nav", "footer", "script", "style", "header", "aside"]):
            tag.decompose()
        main = soup.find("main") or soup.find("article") or soup.find("body")
        raw = main.get_text(separator="\n", strip=True) if main else ""
        lines = [l.strip() for l in raw.splitlines() if l.strip()]
        return "\n".join(lines)
    except Exception as e:
        print(f"  ✗ Failed to scrape {url}: {e}")
        return ""


def chunk_text(text: str, max_tokens: int = 400) -> list:
    enc = tiktoken.get_encoding("cl100k_base")
    words = text.split("\n")
    chunks = []
    current = []
    current_tokens = 0
    for word in words:
        word_tokens = len(enc.encode(word))
        if current_tokens + word_tokens > max_tokens and current:
            chunks.append("\n".join(current))
            current = [word]
            current_tokens = word_tokens
        else:
            current.append(word)
            current_tokens += word_tokens
    if current:
        chunks.append("\n".join(current))
    return [c for c in chunks if len(c.strip()) > 50]


def get_embedding(text: str) -> list:
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=text[:8000]
    )
    return response.data[0].embedding


def seed():
    print("🌱 Starting expanded knowledge base seed...\n")
    db = next(get_db())
    total_chunks = 0

    for form in IRISH_KNOWLEDGE:
        form_type = form["form_type"]
        print(f"📄 Processing {form_type}...")

        for url in form["urls"]:
            print(f"  → Scraping {url}")
            raw_text = scrape_page(url)
            if not raw_text:
                continue
            chunks = chunk_text(raw_text)
            print(f"  → {len(chunks)} chunks extracted")

            for i, chunk in enumerate(chunks):
                try:
                    embedding = get_embedding(chunk)
                    embedding_str = f"[{','.join(map(str, embedding))}]"
                    db.execute(text("""
                        INSERT INTO knowledge_base (form_type, source_url, raw_content, embedding)
                        VALUES (:form_type, :url, :content, cast(:embedding as vector))
                    """), {
                        "form_type": form_type,
                        "url": url,
                        "content": chunk,
                        "embedding": embedding_str
                    })
                    db.commit()
                    total_chunks += 1
                    print(f"  ✓ Chunk {i+1}/{len(chunks)} embedded")
                    time.sleep(0.1)
                except Exception as e:
                    print(f"  ✗ Error on chunk {i+1}: {e}")
                    db.rollback()
        print()

    print(f"✅ Done — {total_chunks} chunks seeded into knowledge base\n")


if __name__ == "__main__":
    seed()