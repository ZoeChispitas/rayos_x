# -*- coding: utf-8 -*-
"""
Interfaz web estilo Chat para diagnóstico de fracturas.
"""
import os
import numpy as np
from tensorflow.keras.models import load_model
from PIL import Image

try:
    import gradio as gr
except ImportError:
    print("Error: Gradio no está instalado.")
    import sys
    sys.exit(1)

from rayosx import MODEL_PATH, class_names

print("Cargando modelo de IA...")
try:
    model = load_model(MODEL_PATH)
    print("Modelo cargado y listo.")
except Exception as e:
    print(f"Error critico al cargar el modelo: {e}")
    import sys
    sys.exit(1)

def diagnosticar_chat(message, history):
    """
    Función para el ChatInterface multimodal.
    message es un diccionario provisto por Gradio: {"text": "...", "files": ["ruta", ...]}
    """
    archivos = message.get("files", [])
    
    if not archivos:
        return "👋 ¡Hola! Soy tu asistente médico de IA. Por favor, adjunta la imagen de una radiografía usando el botón del clip (📎) y la analizaré de inmediato."
    
    ruta_imagen = archivos[0]
    
    # Gradio pasa los archivos como diccionarios en las versiones nuevas
    if isinstance(ruta_imagen, dict):
        ruta_imagen = ruta_imagen.get("path") or ruta_imagen.get("name")
        
    try:
        # Cargar y procesar imagen
        imagen = Image.open(ruta_imagen).convert("RGB")
        img_resized = imagen.resize((224, 224))
        img_array = np.array(img_resized)
        img_array = np.expand_dims(img_array, axis=0) / 255.0

        # Predecir
        predicciones = model.predict(img_array, verbose=0)[0]
        
        # Obtener Top 3
        top_indices = np.argsort(predicciones)[::-1][:3]
        
        # Construir respuesta
        clase_principal = class_names[top_indices[0]]
        confianza_principal = predicciones[top_indices[0]] * 100
        
        respuesta = f"### 🦴 Resultado del Análisis\n\n"
        respuesta += f"**Diagnóstico Principal:** `{clase_principal.upper()}`\n"
        respuesta += f"**Nivel de Confianza:** {confianza_principal:.1f}%\n\n"
        
        if confianza_principal < 70:
            respuesta += "> ⚠️ **Advertencia:** La confianza del modelo es baja. Se recomienda encarecidamente la revisión por parte de un especialista.\n\n"
            
        respuesta += "--- \n**Otras posibilidades detectadas:**\n"
        for i in range(1, 3):
            idx = top_indices[i]
            clase = class_names[idx].replace(" fracture", " fractura").replace("Avulsion", "Avulsión").replace("Comminuted", "Conminuta").replace("Pathological", "Patológica")
            prob = predicciones[idx] * 100
            respuesta += f"- {clase}: {prob:.1f}%\n"
            
        return respuesta

    except Exception as e:
        return f"Ocurrió un error al procesar la imagen: {str(e)}"

# CSS para ocultar TODO el pie de página de Gradio 
custom_css = """
footer {display: none !important;}
#component-0 { height: 100vh; }

/* Fondo general moderno */
body, .gradio-container {
    background: linear-gradient(135deg, #f0f4f8 0%, #d9e2ec 100%) !important;
}

/* Estilos de las burbujas */
.message-wrap .message {
    border-radius: 12px !important;
    padding: 14px !important;
    font-size: 15px !important;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06) !important;
    border: none !important;
}

/* Burbuja asistente */
.bot {
    background-color: #ffffff !important;
    border-left: 4px solid #3b82f6 !important;
}

/* Burbuja usuario */
.user {
    background-color: #e0f2fe !important;
}

/* Caja de entrada de texto */
.textbox-wrap {
    border-radius: 20px !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05) !important;
    border: 1px solid #cbd5e1 !important;
}
"""

# Tema visual moderno
theme = gr.themes.Soft(
    primary_hue="blue",
    neutral_hue="slate",
    font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui", "sans-serif"],
)

demo = gr.ChatInterface(
    fn=diagnosticar_chat,
    multimodal=True,
    title="✨ Inteligencia Artificial - Diagnóstico Óseo",
    description="Sube la radiografía usando el botón de adjuntar (📎) y evaluaré el tipo de fractura al instante.",
)

if __name__ == "__main__":
    print("\nIniciando el servidor web de Gradio (Modo Chat)...")
    demo.launch(inbrowser=True, css=custom_css, theme=theme)
