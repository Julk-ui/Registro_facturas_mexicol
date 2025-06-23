import os
os.environ['TESSDATA_PREFIX'] = r"C:\Program Files\Tesseract-OCR"

import pytesseract
from PIL import Image
import re
import pandas as pd


pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_data_from_image(image_path):
    # Cargar la imagen y aplicar OCR
    text = pytesseract.image_to_string(Image.open(image_path), lang='spa')

    # Procesar el texto como en extract_pdf
    data = {
        "Numero_Factura": extract_with_regex(text, r"MCFE\s+(\d+)"),
        "Fecha": extract_with_regex(text, r"Fecha:\s*(\d{2}/\d{2}/\d{4})"),
        "Cliente": extract_with_regex(text, r"Cliente:\s*(.+?)\s+NIT"),
        "NIT_Cliente": extract_with_regex(text, r"NIT:\s*(\d+\s*-\s*\d)"),
        "Vendedor": extract_with_regex(text, r"Vendedor:\s*(.+)"),
        "Subtotal": extract_with_regex(text, r"SUBTOTAL\s*\$?([\d.,]+)"),
        "IVA": extract_with_regex(text, r"IVA\s*\$?([\d.,]+)"),
        "Total": extract_with_regex(text, r"TOTAL DOCUMENTO\s*\$?([\d.,]+)"),
        "archivo_origen": os.path.basename(image_path)
    }

    return pd.DataFrame([data])

def extract_with_regex(text, pattern):
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).strip() if match else ""
