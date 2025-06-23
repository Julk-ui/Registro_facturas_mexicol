import os
import sys

# Asegurarse de que los módulos se encuentren aunque se ejecute desde otra carpeta
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

TEMPLATE_PATH = os.path.join("templates", "estructura_ventas.xlsx")

def validar_estructura():
    if not os.path.exists(TEMPLATE_PATH):
        print(f"[ERROR] No se encontró la plantilla esperada en: {TEMPLATE_PATH}")
        print("Asegúrate de que exista la carpeta 'templates' y que contenga 'estructura_ventas.xlsx'.")
        return False
    return True

if __name__ == "__main__":
    if validar_estructura():
        try:
            from ui.app import run_app
            run_app()
        except Exception as e:
            print("[ERROR] No se pudo iniciar la aplicación:")
            print(e)
