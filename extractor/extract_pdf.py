import os
import re
import pandas as pd
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import sys

if getattr(sys, 'frozen', False):
    # La app está empaquetada con pyinstaller
    base_path = sys._MEIPASS  # Carpeta temporal donde pyinstaller extrae archivos
else:
    # En modo desarrollo (local)
    base_path = os.path.dirname(__file__)

tesseract_path = os.path.join(base_path, "Tesseract-OCR", "tesseract.exe")
pytesseract.pytesseract.tesseract_cmd = tesseract_path
os.environ['TESSDATA_PREFIX'] = os.path.dirname(tesseract_path)

def extract_data_from_pdf(pdf_path):
    # Convertir PDF completo a texto
    images = convert_from_path(pdf_path)
    text = ""
    for img in images:
        text += pytesseract.image_to_string(img, lang='spa') + "\n"

    # Datos generales de la factura
    factura = {
        "FECHA": extract_with_regex(text, r"Fecha:\s*(\d{2}/\d{2}/\d{4})", "Fecha"),
        "CLIENTE": extract_with_regex(text, r"Cliente:\s*(.+?)\s+NIT", "Cliente"),
        "NIT CLIENTE": extract_with_regex(text, r"Cliente:\s*.+?\s+NIT:\s*([\d\s\-]+)", "NIT Cliente"),
        "ASESOR": extract_with_regex(text, r"Vendedor:\s*(.+)", "Vendedor"),
        "FORMA DE PAGO": extract_with_regex(text, r"Forma de Pago:\s*(\w+)", "Forma de pago"),
        "TOTAL": extract_with_regex(text, r"TOTAL DOCUMENTO\s*\$\s*([\d.,]+)", "Total"),
        "NUMERO FACTURA": extract_factura_num_from_header(pdf_path),
        "archivo_origen": os.path.basename(pdf_path)
    }

    # Extraer ítems de producto
    items = extract_items(text)

    rows = []
    for item in items:
        row = factura.copy()
        row.update(item)
        rows.append(row)

    df = pd.DataFrame(rows)

    # Convertir valores numéricos
    for col in ["VALOR TOTAL", "IVA 19%"]:
        df[col] = df[col].astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False).astype(float)

    # Calcular totales
    subtotal_sin_iva = df["VALOR TOTAL"].sum()
    iva_total = df["IVA 19%"].sum()

    df["SUBTOTAL SIN IVA"] = round(subtotal_sin_iva, 2)
    df["IVA TOTAL"] = round(iva_total, 2)

    return df

# Utilidad para extraer campos
def extract_with_regex(text, pattern, field_name=""):
    matches = re.findall(pattern, text, re.IGNORECASE)
    if matches:
        return matches[0].strip()
    else:
        print(f"[WARN] No se encontró '{field_name}' con patrón: {pattern}")
        return ""

# ✅ Nueva versión: extrae número de factura del encabezado (imagen recortada)
def extract_factura_num_from_header(pdf_path):
    from PIL import ImageOps

    try:
        image = convert_from_path(pdf_path, dpi=300, first_page=1, last_page=1)[0]
        
        # ⬆️ Aumentar zona de recorte vertical para capturar mejor el encabezado
        width, height = image.size
        cropped = image.crop((0, 0, width, int(height * 0.4)))  # 40% superior

        # 🧼 Mejorar visibilidad para OCR (blanco y negro)
        gray = ImageOps.grayscale(cropped)
        bw = gray.point(lambda x: 0 if x < 180 else 255, '1')  # Umbral binarización

        header_text = pytesseract.image_to_string(bw, lang="spa")
        print("\n[DEBUG HEADER OCR]\n", header_text)

        # Buscar MCFE o número de factura
        match = re.search(r"MCFE\s*[-:]?\s*(\d{3,6})", header_text)
        if match:
            return match.group(1)

        # Alternativa: "Factura Electrónica No. 1234" o similar
        match_alt = re.search(r"Factura.*?No\.?\s*(\d{3,6})", header_text, re.IGNORECASE)
        if match_alt:
            return match_alt.group(1)

        print("[WARN] No se encontró número de factura en encabezado.")
        return ""

    except Exception as e:
        print(f"[ERROR] No se pudo extraer número de factura del encabezado: {e}")
        return ""


# Extracción de ítems por línea
def extract_items(text):
    lines = text.splitlines()
    product_lines = [line for line in lines if re.search(r"\d{1,2}\s+[A-Z0-9]{5}", line)]

    items = []
    for line in product_lines:
        match = re.search(r"""
            (?P<codigo>[A-Z0-9]{5})\s+
            (?P<descripcion>[A-ZÁÉÍÓÚÑa-z0-9 /-]+?)\s+
            (?P<unidad>und|kg|g|lb|ml|lts|unidad)\s+
            (?P<cantidad>[\d.,]+)\s+
            (?P<valor_unitario>[\d.,]+)\s+
            (?P<descuento>[\d.,]+)\s+
            \d{2}\s+                            # %
            (?P<iva_valor>[\d.,]+)\s+
            (?P<total>[\d.,]+)
        """, line, re.VERBOSE)

        if match:
            item = {
                "PRODUCTO": match.group("descripcion").strip(),
                "UNIDAD": match.group("unidad"),
                "CANT. KLS": match.group("cantidad"),
                "VALOR X KL": match.group("valor_unitario"),
                "VALOR TOTAL": match.group("total"),
                "IVA 19%": match.group("iva_valor"),
            }
            items.append(item)

    return items
