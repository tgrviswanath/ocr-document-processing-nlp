"""
Generate sample images for project-17 OCR Document Processing.
Run: pip install Pillow && python generate_samples.py
Output: 4 images simulating scanned documents with text.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, random

OUT = os.path.dirname(__file__)


def make_font(size):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        return ImageFont.load_default()


def save(img, name):
    img.save(os.path.join(OUT, name))
    print(f"  created: {name}")


def add_scan_noise(img):
    """Add slight noise and blur to simulate a scanned document."""
    import numpy as np
    arr = np.array(img).astype(int)
    noise = np.random.randint(-8, 8, arr.shape)
    arr = (arr + noise).clip(0, 255).astype("uint8")
    return Image.fromarray(arr).filter(ImageFilter.GaussianBlur(0.4))


def invoice_image():
    W, H = 700, 900
    img = Image.new("RGB", (W, H), (252, 252, 248))
    d = ImageDraw.Draw(img)
    f_lg = make_font(28)
    f_md = make_font(18)
    f_sm = make_font(14)

    d.rectangle([0, 0, W, 70], fill=(30, 80, 160))
    d.text((20, 18), "INVOICE", fill=(255, 255, 255), font=f_lg)
    d.text((450, 20), "INV-2024-0042", fill=(255, 255, 255), font=f_md)

    d.text((20, 90), "Bill To:", fill=(60, 60, 60), font=f_md)
    d.text((20, 115), "John Smith", fill=(20, 20, 20), font=f_md)
    d.text((20, 138), "123 Main Street, London, UK", fill=(20, 20, 20), font=f_sm)
    d.text((20, 158), "john.smith@email.com", fill=(20, 20, 20), font=f_sm)
    d.text((420, 90), "Date: 15 Jan 2024", fill=(60, 60, 60), font=f_sm)
    d.text((420, 110), "Due:  30 Jan 2024", fill=(60, 60, 60), font=f_sm)

    d.rectangle([20, 200, 680, 230], fill=(220, 230, 245))
    for x, label in [(25, "Description"), (400, "Qty"), (490, "Unit Price"), (590, "Total")]:
        d.text((x, 208), label, fill=(20, 20, 20), font=f_md)

    items = [
        ("Web Development Service", "1", "1,200.00", "1,200.00"),
        ("UI/UX Design", "3", "350.00", "1,050.00"),
        ("Server Setup & Config", "1", "400.00", "400.00"),
        ("Monthly Maintenance", "2", "150.00", "300.00"),
    ]
    y = 245
    for desc, qty, unit, total in items:
        d.text((25, y), desc, fill=(20, 20, 20), font=f_sm)
        d.text((400, y), qty, fill=(20, 20, 20), font=f_sm)
        d.text((490, y), f"£{unit}", fill=(20, 20, 20), font=f_sm)
        d.text((590, y), f"£{total}", fill=(20, 20, 20), font=f_sm)
        d.line([20, y + 22, 680, y + 22], fill=(220, 220, 220), width=1)
        y += 38

    d.rectangle([450, y + 10, 680, y + 38], fill=(240, 245, 255))
    d.text((455, y + 16), "TOTAL:  £2,950.00", fill=(30, 80, 160), font=f_md)
    d.text((20, 820), "Payment: Bank Transfer  |  IBAN: GB29 NWBK 6016 1331 9268 19", fill=(100, 100, 100), font=f_sm)
    d.text((20, 840), "Thank you for your business!", fill=(100, 100, 100), font=f_sm)
    return add_scan_noise(img)


def business_letter():
    W, H = 700, 950
    img = Image.new("RGB", (W, H), (252, 252, 248))
    d = ImageDraw.Draw(img)
    f_lg = make_font(22)
    f_md = make_font(16)
    f_sm = make_font(13)

    d.text((20, 30), "TechCorp Ltd.", fill=(20, 20, 20), font=f_lg)
    d.text((20, 58), "45 Innovation Park, Manchester, M1 2AB", fill=(80, 80, 80), font=f_sm)
    d.text((20, 76), "Tel: +44 161 555 0100  |  info@techcorp.co.uk", fill=(80, 80, 80), font=f_sm)
    d.line([20, 100, 680, 100], fill=(180, 180, 180), width=1)
    d.text((20, 120), "15 January 2024", fill=(60, 60, 60), font=f_sm)
    d.text((20, 160), "Dear Mr. Johnson,", fill=(20, 20, 20), font=f_md)

    lines = [
        "Re: Project Proposal — AI Integration Platform",
        "",
        "We are pleased to submit our proposal for the development of an",
        "AI-powered integration platform as discussed in our meeting on",
        "10 January 2024.",
        "",
        "Our team has extensive experience delivering enterprise-grade",
        "machine learning solutions. The proposed timeline is 12 weeks",
        "with a total budget of £45,000 including all deliverables.",
        "",
        "The platform will include the following components:",
        "  - Natural language processing pipeline",
        "  - Real-time data ingestion and processing",
        "  - REST API with authentication and rate limiting",
        "  - React dashboard with analytics",
        "",
        "Please find the detailed specification document attached.",
        "We look forward to your feedback.",
        "",
        "Yours sincerely,",
        "",
        "Sarah Williams",
        "Head of Business Development",
        "TechCorp Ltd.",
    ]
    y = 200
    for line in lines:
        d.text((20, y), line, fill=(20, 20, 20), font=f_sm)
        y += 22
    return add_scan_noise(img)


def receipt_image():
    W, H = 420, 680
    img = Image.new("RGB", (W, H), (252, 252, 248))
    d = ImageDraw.Draw(img)
    f_lg = make_font(22)
    f_md = make_font(16)
    f_sm = make_font(13)

    d.text((110, 20), "SUPERMART", fill=(20, 20, 20), font=f_lg)
    d.text((90, 50), "123 High Street, London", fill=(80, 80, 80), font=f_sm)
    d.text((120, 68), "Tel: 020 7946 0958", fill=(80, 80, 80), font=f_sm)
    d.line([20, 90, 400, 90], fill=(180, 180, 180), width=1)
    d.text((20, 100), "Date: 15/01/2024  Time: 14:32", fill=(60, 60, 60), font=f_sm)
    d.text((20, 118), "Receipt #: 00847291", fill=(60, 60, 60), font=f_sm)
    d.line([20, 138, 400, 138], fill=(180, 180, 180), width=1)

    items = [
        ("Organic Milk 2L", "£1.89"),
        ("Sourdough Bread", "£2.45"),
        ("Free Range Eggs x12", "£3.20"),
        ("Cheddar Cheese 400g", "£4.10"),
        ("Orange Juice 1L", "£2.30"),
        ("Pasta 500g", "£1.15"),
        ("Tomato Sauce", "£1.80"),
    ]
    y = 150
    for item, price in items:
        d.text((20, y), item, fill=(20, 20, 20), font=f_sm)
        d.text((330, y), price, fill=(20, 20, 20), font=f_sm)
        y += 30

    d.line([20, y + 5, 400, y + 5], fill=(180, 180, 180), width=1)
    d.text((20, y + 15), "Subtotal:", fill=(60, 60, 60), font=f_md)
    d.text((310, y + 15), "£16.89", fill=(20, 20, 20), font=f_md)
    d.text((20, y + 38), "VAT (20%):", fill=(60, 60, 60), font=f_sm)
    d.text((320, y + 38), "£3.38", fill=(20, 20, 20), font=f_sm)
    d.text((20, y + 58), "TOTAL:", fill=(20, 20, 20), font=f_lg)
    d.text((290, y + 58), "£20.27", fill=(20, 20, 20), font=f_lg)
    d.text((90, y + 100), "Thank you for shopping!", fill=(100, 100, 100), font=f_sm)
    return add_scan_noise(img)


def report_page():
    W, H = 700, 950
    img = Image.new("RGB", (W, H), (252, 252, 248))
    d = ImageDraw.Draw(img)
    f_lg = make_font(24)
    f_md = make_font(16)
    f_sm = make_font(13)

    d.rectangle([0, 0, W, 60], fill=(50, 100, 180))
    d.text((20, 15), "Annual Performance Report 2023", fill=(255, 255, 255), font=f_lg)

    sections = [
        ("Executive Summary", [
            "This report presents the annual performance metrics for FY2023.",
            "Total revenue reached £12.4 million, representing 23% growth YoY.",
            "Net profit margin improved to 18.5%, up from 14.2% in FY2022.",
            "Customer base expanded to 8,500 active accounts across 32 countries.",
        ]),
        ("Key Metrics", [
            "Revenue:          £12,400,000  (+23% YoY)",
            "Operating Costs:  £10,108,000  (+15% YoY)",
            "Net Profit:       £2,292,000   (+51% YoY)",
            "Employees:        142          (+18 headcount)",
            "Customer NPS:     72           (+8 points)",
        ]),
        ("Regional Performance", [
            "United Kingdom:   £5.2M  (42% of total revenue)",
            "Europe:           £3.8M  (31% of total revenue)",
            "North America:    £2.1M  (17% of total revenue)",
            "Asia Pacific:     £1.3M  (10% of total revenue)",
        ]),
        ("Outlook for 2024", [
            "Management targets 20% revenue growth for FY2024.",
            "Key investments planned in AI infrastructure and talent acquisition.",
            "New product launches scheduled for Q2 and Q4 2024.",
            "Expansion into the Middle East market planned for H2 2024.",
        ]),
    ]

    y = 80
    for title, lines in sections:
        d.text((20, y), title, fill=(30, 80, 160), font=f_md)
        d.line([20, y + 22, 680, y + 22], fill=(200, 210, 230), width=1)
        y += 32
        for line in lines:
            d.text((30, y), line, fill=(20, 20, 20), font=f_sm)
            y += 22
        y += 15

    d.text((20, H - 30), "CONFIDENTIAL — TechCorp Ltd. — Page 1 of 8", fill=(150, 150, 150), font=f_sm)
    return add_scan_noise(img)


if __name__ == "__main__":
    print("Generating project-17 OCR samples...")
    save(invoice_image(), "sample_invoice.png")
    save(business_letter(), "sample_letter.png")
    save(receipt_image(), "sample_receipt.png")
    save(report_page(), "sample_report.png")
    print("Done — 4 images in samples/")
    print("Upload any image to the OCR Document Processing UI.")
