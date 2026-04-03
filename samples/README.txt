What questions can I ask after OCR extraction?
  - Who is the invoice billed to?
  - What is the total amount due?
  - What is the invoice number?
  - What is the due date?
  - What services were provided?
  - What is the company name?
  - What is the contact email?

Run: pip install Pillow numpy && python generate_samples.py
Output: 4 PNG images simulating scanned documents

Files:
  sample_invoice.png  - Invoice with line items, totals, contact info
  sample_letter.png   - Business letter with named entities (person, org, date, money)
  sample_receipt.png  - Retail receipt with items and prices
  sample_report.png   - Annual report page with financial metrics

Expected NER entities:
  sample_letter.png:
    PERSON: Sarah Williams, Mr. Johnson
    ORG:    TechCorp Ltd.
    DATE:   15 January 2024, 10 January 2024
    MONEY:  £45,000
