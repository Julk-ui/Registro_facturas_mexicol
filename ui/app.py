import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import pandas as pd
import sys
import os
from PIL import Image, ImageTk 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from extractor.extract_pdf import extract_data_from_pdf
from extractor.extract_image import extract_data_from_image
from extractor.extract_excel import extract_data_from_excel
from extractor.standardizer import load_sales_template, standardize_to_template

TEMPLATE_PATH = os.path.join("templates", "estructura_ventas.xlsx")

def run_app():
    app = tk.Tk()
    app.title("Registro de Facturas - Mexicol")
    app.geometry("900x500")

    # (1) Cargar logo visual (se muestra en la GUI arriba)
    try:
        logo_path = os.path.join(os.path.dirname(__file__), "logo_mexicol.jpg")
        img = Image.open(logo_path)
        img = img.resize((100, 50))  # Tamaño personalizado
        logo_img = ImageTk.PhotoImage(img)

        logo_label = tk.Label(app, image=logo_img)
        logo_label.image = logo_img  # ← mantiene referencia
        logo_label.pack(pady=5)
    except Exception as e:
        print("[ERROR] No se pudo cargar el logo visual:", e)

    # (2) Cargar ícono de ventana (solo .ico, opcional)
    try:
        icon_path = os.path.join(os.path.dirname(__file__), "logo_mexicol.ico")
        app.iconbitmap(icon_path)
    except Exception as e:
        print("[WARN] No se pudo asignar ícono de ventana (usa .ico):", e)

    data_accumulated = []

    tree = ttk.Treeview(app)
    tree["columns"] = []
    tree.pack(fill="both", expand=True)

    def cargar_archivos():
        archivos = filedialog.askopenfilenames(title="Selecciona archivos de facturas", filetypes=[
            ("Archivos válidos", "*.pdf *.jpg *.jpeg *.png *.xlsx"),
            ("Todos los archivos", "*.*")
        ])

        template_cols = load_sales_template(TEMPLATE_PATH)

        # Validación defensiva
        template_cols = [
            str(col).strip()
            for col in template_cols
            if pd.notna(col) and isinstance(col, str) and col.strip().upper() != "NAN"
        ]

        # Eliminar duplicados si los hubiera
        template_cols = list(dict.fromkeys(template_cols))
        print("[COLUMNS PLANTILLA VALIDADAS]:", template_cols)

        for archivo in archivos:
            ext = os.path.splitext(archivo)[1].lower()
            df = pd.DataFrame()

            if ext == ".pdf":
                df = extract_data_from_pdf(archivo)
            elif ext in [".jpg", ".jpeg", ".png"]:
                df = extract_data_from_image(archivo)
            elif ext == ".xlsx":
                df = extract_data_from_excel(archivo)

            if not df.empty:
                df_std = standardize_to_template(df, template_cols)
                data_accumulated.append(df_std)

        if data_accumulated:
            mostrar_datos(pd.concat(data_accumulated, ignore_index=True))
        else:
            messagebox.showwarning("Advertencia", "No se pudo extraer información de los archivos seleccionados.")

    def mostrar_datos(df):
        tree.delete(*tree.get_children())
        tree["columns"] = list(df.columns)
        tree["show"] = "headings"

        for col in df.columns:
            tree.heading(col, text=col)
            tree.column(col, width=150, anchor="w")

        for _, row in df.iterrows():
            tree.insert("", "end", values=list(row))

    def guardar_excel():
        if not data_accumulated:
            messagebox.showinfo("Sin datos", "No hay datos para guardar.")
            return

        df_final = pd.concat(data_accumulated, ignore_index=True)

        archivo_salida = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                       filetypes=[("Archivos Excel", "*.xlsx")],
                                                       title="Guardar archivo consolidado")

        if archivo_salida:
            df_final.to_excel(archivo_salida, index=False)
            messagebox.showinfo("Éxito", f"Archivo guardado en:\n{archivo_salida}")

    btn_cargar = tk.Button(app, text="Cargar Facturas", command=cargar_archivos)
    btn_cargar.pack(pady=10)

    btn_guardar = tk.Button(app, text="Guardar Excel", command=guardar_excel)
    btn_guardar.pack(pady=5)

    app.mainloop()

def get_resource_path(relative_path):
    """
    Retorna la ruta absoluta del recurso, considerando si se ejecuta con PyInstaller o no.
    """
    if getattr(sys, 'frozen', False):
        # En ejecución como .exe
        base_path = sys._MEIPASS
    else:
        # En modo desarrollo
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)