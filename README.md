# Registro de Facturas Mexicol

Este proyecto automatiza el proceso de extracción y consolidación de datos desde facturas en formato PDF, imagen o Excel, estandarizando los resultados en un archivo Excel con la estructura esperada por la hoja `ventas`.

## 📦 Requisitos

- Python 3.8+
- Tesseract OCR instalado en: `C:\Program Files\Tesseract-OCR`
- `spa.traineddata` disponible en `tessdata`
- Dependencias Python:

```bash
pip install -r requirements.txt
🧠 Funcionalidades
Carga múltiple de archivos PDF, imagen o Excel.

OCR y extracción inteligente de datos clave.

Procesamiento línea a línea de ítems/productos.

Mapeo a plantilla de Excel + columnas adicionales si se detectan más datos.

▶️ Ejecución
Desde la raíz del proyecto:

bash
Copiar
Editar
python main.py
✨ Campos extraídos
Fecha, Cliente, Asesor

Ítems (producto, unidad, cantidad, valor unitario, total, IVA)

Subtotal sin IVA, IVA total, Total general

Número de factura

Archivo origen

📁 Estructura esperada
css
Copiar
Editar
Registro_facturas_mexicol/
├── extractor/
│   ├── extract_pdf.py
│   ├── extract_excel.py
│   ├── extract_image.py
│   └── standardizer.py
├── ui/
│   └── app.py
├── templates/
│   └── estructura_ventas.xlsx
├── main.py
└── README.md