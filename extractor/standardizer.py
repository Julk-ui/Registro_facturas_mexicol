import pandas as pd

def load_sales_template(template_path, hoja="ventas"):
    """
    Carga nombres de columnas desde una plantilla de Excel (hoja 'ventas'),
    eliminando espacios y valores nulos.
    """
    df_template = pd.read_excel(template_path, sheet_name=hoja, nrows=1)
    columnas = df_template.columns
    columnas_limpias = [
        str(col).strip() for col in columnas
        if pd.notna(col) and isinstance(col, (str, int, float))
    ]
    return columnas_limpias

def standardize_to_template(dataframe, template_columns):
    """
    Reestructura el DataFrame a la forma esperada por el template:
    - Mapea columnas por nombre limpio (sin espacios, mayúsculas)
    - Rellena columnas faltantes con vacío
    - Agrega columnas adicionales que no estén en el template
    """
    # Normalizar nombres del DataFrame de entrada
    df_cols_clean = {
        str(col).strip().upper(): col
        for col in dataframe.columns if pd.notna(col)
    }

    # Limpiar nombres de la plantilla
    template_cleaned = [
        str(col).strip().upper()
        for col in template_columns if pd.notna(col)
    ]

    standardized = pd.DataFrame()

    # Asignar columnas que existen en plantilla
    for clean_col in template_cleaned:
        original_col = df_cols_clean.get(clean_col, None)
        if original_col and original_col in dataframe.columns:
            standardized[clean_col] = dataframe[original_col]
        else:
            standardized[clean_col] = ""

    # Agregar columnas extras del OCR u otras fuentes
    extra_cols = [
        col for col in df_cols_clean
        if col not in template_cleaned
    ]
    for col in extra_cols:
        original_col = df_cols_clean[col]
        standardized[col] = dataframe[original_col]

    return standardized
