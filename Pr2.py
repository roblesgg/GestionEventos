import tkinter as tk
from tkinter import filedialog

def seleccionar_archivo():
    root = tk.Tk()
    root.withdraw()
    
    root.update()
    
    ruta_archivo = filedialog.askopenfilename(
        title="Selecciona un archivo",
        filetypes=[("Todos los archivos", "*.*")]
    )
    
    root.destroy()
    
    return ruta_archivo

if __name__ == "__main__":
    ruta = seleccionar_archivo()
    if ruta:
        print("Archivo seleccionado:", ruta)
    else:
        print("No se seleccionó ningún archivo.")