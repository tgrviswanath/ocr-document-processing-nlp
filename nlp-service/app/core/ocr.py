"""
OCR engine: extracts text from images and PDFs.
- Images: Tesseract via pytesseract (with OpenCV preprocessing)
- PDFs: PyMuPDF (native text first, fallback to Tesseract per page)
"""
import io
import pytesseract
import fitz  # PyMuPDF
import numpy as np
import cv2
from PIL import Image


def _preprocess_image(img: np.ndarray) -> np.ndarray:
    """Denoise + deskew + threshold for better OCR accuracy."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
    denoised = cv2.fastNlMeansDenoising(gray, h=10)
    _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh


def extract_from_image(image_bytes: bytes) -> dict:
    """Extract text from image bytes (PNG, JPG, TIFF, BMP)."""
    img_array = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    if img is None:
        pil_img = Image.open(io.BytesIO(image_bytes))
        img = np.array(pil_img.convert("RGB"))
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    processed = _preprocess_image(img)
    text = pytesseract.image_to_string(processed, config="--psm 6")
    data = pytesseract.image_to_data(processed, output_type=pytesseract.Output.DICT)
    confidences = [int(c) for c in data["conf"] if str(c).isdigit() and int(c) > 0]
    avg_conf = round(sum(confidences) / len(confidences), 1) if confidences else 0.0

    return {
        "text": text.strip(),
        "pages": 1,
        "avg_confidence": avg_conf,
        "source": "tesseract",
    }


def extract_from_pdf(pdf_bytes: bytes) -> dict:
    """Extract text from PDF — native text first, OCR fallback per page."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages_text = []
    source = "pymupdf"

    for page in doc:
        native_text = page.get_text().strip()
        if native_text:
            pages_text.append(native_text)
        else:
            # Scanned page — render and OCR
            source = "tesseract"
            pix = page.get_pixmap(dpi=200)
            img_bytes = pix.tobytes("png")
            result = extract_from_image(img_bytes)
            pages_text.append(result["text"])

    full_text = "\n\n".join(pages_text)
    return {
        "text": full_text.strip(),
        "pages": len(doc),
        "avg_confidence": 100.0 if source == "pymupdf" else 0.0,
        "source": source,
    }
