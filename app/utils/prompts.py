CLASSIFIER_PROMPT = """
You are an expert at classifying Irish government, administrative, and everyday documents.

Your task: read the document text and return the single most accurate classification code.

Document text (first 500 chars):
{text_sample}

CLASSIFICATION CODES:

Government & Tax:
- HAP_form — Housing Assistance Payment form or letter
- PPS_application — Personal Public Service number application
- Revenue_notice — Revenue Commissioners tax notice, underpayment, refund
- Revenue_assessment — Revenue tax assessment or P21 balancing statement
- DSP_letter — Department of Social Protection, welfare payment letter
- council_tax — Local Property Tax (LPT) notice

Immigration & Visas:
- visa_application — Irish visa application form or acknowledgement
- visa_refusal — visa refusal or rejection letter
- immigration_document — IRP card, GNIB card, residence permit, stamp
- employment_permit — Critical Skills, General or Intra-Company work permit

Housing:
- eviction_notice — notice of termination, notice to quit, RTB letter
- rent_bill — rent receipt, landlord rent invoice, rental statement
- HAP_form — HAP tenant or landlord form

Health:
- HSE_letter — HSE appointment, treatment, or health service letter
- medical_card — medical card approval, renewal, or GP visit card

Employment:
- payslip — wage slip, salary advice, pay stub, PAYE payslip
- job_offer_letter — employment contract, job offer, terms and conditions of employment

Transport:
- toll_payment — eFlow M50 toll receipt, motorway toll payment
- driving_licence — driver licence application, renewal, or exchange
- motor_tax — motor tax renewal, VRT, vehicle registration

Utilities & Bills:
- utility_bill — ESB, Electric Ireland, Gas Networks, Bord Gáis, water, broadband bill
- rent_bill — rent receipt or landlord invoice

Shopping & Receipts:
- grocery_bill — Tesco, Lidl, Aldi, Supervalu, Dunnes Stores, Mini India, supermarket receipt
- shopping_receipt — any retail shop receipt, pharmacy, clothing store

Finance:
- bank_letter — bank statement, bank notice, mortgage letter, credit union
- debt_collection — debt collection letter, solicitor demand, CCJ notice

Other:
- lottery_ticket — National Lottery, Lotto, EuroMillions, scratch card, sports bet slip
- opw_form — OPW form, Government Publications Office, ISBN/barcode application
- planning_notice — planning permission, An Bord Pleanála, development notice
- unknown — cannot be classified with confidence

Rules:
- Return ONLY the code, nothing else
- No punctuation, no explanation, no preamble
- If unsure between two categories, pick the more specific one
- A payslip is NOT a Revenue_notice — they are different documents
- A grocery receipt is NOT a utility_bill
- When in doubt, prefer unknown over a wrong classification
"""