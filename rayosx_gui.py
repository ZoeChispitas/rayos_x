# -*- coding: utf-8 -*-
"""
Interfaz gráfica para diagnóstico de fracturas en radiografías.
Requiere: ejecutar con el entorno virtual (venv) activado.
"""
import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np

# Importar la lógica del proyecto
from rayosx import (
    load_model, load_img, img_to_array,
    MODEL_PATH, class_names, IMG_FOLDER_PATH
)

# Tamaño para previsualización
PREVIEW_SIZE = (300, 300)
INPUT_SIZE = (224, 224)


def diagnosticar_imagen(ruta_imagen, modelo):
    """Predice el tipo de fractura para una imagen."""
    img = load_img(ruta_imagen, target_size=INPUT_SIZE)
    img_array = img_to_array(img)
    img_array = np.expand_dims(img_array / 255.0, axis=0)
    probas = modelo.predict(img_array, verbose=0)[0]
    idx = np.argmax(probas)
    confianza = probas[idx] * 100
    clase = class_names[idx]
    return clase, confianza, probas


class AppDiagnostico(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Diagnóstico de fracturas - Radiografías")
        self.geometry("700x550")
        self.modelo = None
        self.imagen_actual = None
        self._cargar_modelo()
        self._crear_ui()

    def _cargar_modelo(self):
        if not os.path.exists(MODEL_PATH):
            messagebox.showerror(
                "Modelo no encontrado",
                f"No se encontró el modelo en:\n{MODEL_PATH}\n\nEntrena primero con rayosx.py"
            )
            return
        try:
            self.modelo = load_model(MODEL_PATH)
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar el modelo:\n{e}")

    def _crear_ui(self):
        # Marco superior: selección de archivo
        frame_archivo = ttk.LabelFrame(self, text="Imagen", padding=10)
        frame_archivo.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(frame_archivo, text="Seleccionar radiografía...", command=self._elegir_imagen).pack(side=tk.LEFT, padx=5)
        self.label_ruta = ttk.Label(frame_archivo, text="Ninguna imagen seleccionada", foreground="gray")
        self.label_ruta.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # Vista previa
        frame_preview = ttk.Frame(self, padding=10)
        frame_preview.pack(fill=tk.BOTH, expand=True)
        self.canvas_placeholder = ttk.Label(frame_preview, text="Vista previa de la imagen", relief=tk.SUNKEN)
        self.canvas_placeholder.pack(fill=tk.BOTH, expand=True)

        # Botón diagnosticar
        ttk.Button(self, text="Diagnosticar", command=self._diagnosticar).pack(pady=10)

        # Resultado
        self.frame_resultado = ttk.LabelFrame(self, text="Resultado", padding=10)
        self.frame_resultado.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.label_diagnostico = ttk.Label(self.frame_resultado, text="—", font=("", 12, "bold"))
        self.label_diagnostico.pack(anchor=tk.W)
        self.label_confianza = ttk.Label(self.frame_resultado, text="", foreground="gray")
        self.label_confianza.pack(anchor=tk.W)
        self.text_detalle = tk.Text(self.frame_resultado, height=6, wrap=tk.WORD, state=tk.DISABLED)
        self.text_detalle.pack(fill=tk.BOTH, expand=True, pady=5)

    def _elegir_imagen(self):
        path = filedialog.askopenfilename(
            title="Seleccionar radiografía",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg"), ("Todos", "*.*")]
        )
        if not path:
            return
        self.ruta_imagen = path
        self.label_ruta.config(text=os.path.basename(path), foreground="black")
        try:
            img = Image.open(path).convert("RGB")
            img.thumbnail(PREVIEW_SIZE, Image.Resampling.LANCZOS)
            self.foto = ImageTk.PhotoImage(img)
            self.canvas_placeholder.config(image=self.foto, text="")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la imagen:\n{e}")

    def _diagnosticar(self):
        if not hasattr(self, "ruta_imagen") or not self.ruta_imagen:
            messagebox.showwarning("Aviso", "Selecciona primero una radiografía.")
            return
        if self.modelo is None:
            messagebox.showerror("Error", "El modelo no está cargado.")
            return
        try:
            clase, confianza, probas = diagnosticar_imagen(self.ruta_imagen, self.modelo)
            self.label_diagnostico.config(text=f"Diagnóstico: {clase}")
            self.label_confianza.config(text=f"Confianza: {confianza:.1f}%")
            if confianza < 70:
                self.label_confianza.config(foreground="orange")
            else:
                self.label_confianza.config(foreground="gray")

            # Detalle por clase
            orden = np.argsort(probas)[::-1]
            lineas = ["Top predicciones:\n"]
            for i in orden[:5]:
                lineas.append(f"  {class_names[i]}: {probas[i]*100:.1f}%\n")
            self.text_detalle.config(state=tk.NORMAL)
            self.text_detalle.delete("1.0", tk.END)
            self.text_detalle.insert(tk.END, "".join(lineas))
            self.text_detalle.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Error", f"Error al diagnosticar:\n{e}")


def main():
    app = AppDiagnostico()
    app.mainloop()


if __name__ == "__main__":
    main()
