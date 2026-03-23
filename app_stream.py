import streamlit as st
import os
import shutil
import numpy as np
from PIL import Image
from tensorflow.keras.models import load_model

from rayosx import MODEL_PATH, class_names, IMG_FOLDER_PATH, entrenar_modelo

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="IA Diagnóstico de Rayos X",
    page_icon="🦴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS PERSONALIZADO ---
st.markdown("""
<style>
    .reportview-container {
        background: #f0f4f8;
    }
    .stDeployButton {
        display: none !important;
    }
    .status-widget {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .success-status { background-color: #d1fae5; border-left: 4px solid #10b981; }
    .warning-status { background-color: #fef3c7; border-left: 4px solid #f59e0b; }
    .stButton>button { width: 100%; border-radius: 20px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- CARGA DE MODELO (CACHED) ---
@st.cache_resource
def get_model():
    if os.path.exists(MODEL_PATH):
        return load_model(MODEL_PATH)
    return None

model = get_model()

# --- SIDEBAR ---
with st.sidebar:
    st.image("imagen/logo_ray.png", width=100)
    st.title("Panel de Control")
    st.markdown("---")
    st.markdown("### ⚙️ Estado del Sistema")
    if model:
        st.success("✅ Modelo cargado correctamente")
    else:
        st.error("❌ Modelo no encontrado")
        
    st.markdown("---")
    st.markdown("### 🧠 Aprendizaje Activo")
    st.info("El sistema guarda las imágenes validadas para mejorar en el futuro.")
    
    if st.button("🔄 Forzar Re-entrenamiento", type="primary"):
        st.warning("Iniciando re-entrenamiento... Esto puede tardar varios minutos.")
        with st.spinner('Entrenando el modelo con los nuevos datos...'):
            try:
                # Llamada directa a tu función de rayosx.py
                entrenar_modelo()
                st.success("¡Entrenamiento completado! Refresque la app para cargar el nuevo modelo.")
            except Exception as e:
                st.error(f"Error durante el entrenamiento: {e}")
                
    st.markdown("---")
    st.markdown("<p style='text-align: center; color: gray; font-size: 0.8rem;'>Desarrollado con el apoyo de:</p>", unsafe_allow_html=True)
    st.image("imagen/ticmega.png", use_container_width=True)

# --- MAIN APP ---
st.title("🦴 Asistente Médico IA - Diagnóstico de Fracturas")
st.markdown("Sube una o varias radiografías para analizarlas mediante Inteligencia Artificial.")

if not model:
    st.stop()

# --- UPLOAD MULTIPLE FILES ---
uploaded_files = st.file_uploader(
    "Selecciona radiografías (JPG, PNG)", 
    type=["jpg", "jpeg", "png"], 
    accept_multiple_files=True
)

# Función para predecir
def predecir_imagen(img):
    img_resized = img.resize((224, 224)).convert("RGB")
    img_array = np.array(img_resized)
    img_array = np.expand_dims(img_array, axis=0) / 255.0
    probas = model.predict(img_array, verbose=0)[0]
    return probas

# Diccionario de traducción para mostrar al usuario (si hay nombres en inglés)
diccionario_esp = {
    "Avulsion fracture": "Fractura por Avulsión",
    "Comminuted fracture": "Fractura Conminuta",
    "Fracture Dislocation": "Fractura por Luxación",
    "Greenstick fracture": "Fractura en Tallo Verde",
    "Hairline Fracture": "Fisura (Hairline)",
    "Impacted fracture": "Fractura Impactada",
    "Longitudinal fracture": "Fractura Longitudinal",
    "Oblique fracture": "Fractura Oblicua",
    "Pathological fracture": "Fractura Patológica",
    "Spiral Fracture": "Fractura Espiral"
}

def traducir(clase_ingles):
    return diccionario_esp.get(clase_ingles, clase_ingles.replace(" fracture", " fractura").title())

# Carpeta base para Active Learning
DATASET_PATH = os.path.join(os.getcwd(), "YOLO_Fracturas", "archive", "Bone Break Classification")

if uploaded_files:
    st.markdown("### 📊 Resultados del Análisis")
    
    for i, uploaded_file in enumerate(uploaded_files):
        with st.container():
            col1, col2 = st.columns([1, 2])
            
            # Cargar imagen
            img = Image.open(uploaded_file)
            probas = predecir_imagen(img)
            idx_max = np.argmax(probas)
            confianza = probas[idx_max] * 100
            prediccion_clase_ingles = class_names[idx_max]
            prediccion_clase_esp = traducir(prediccion_clase_ingles)
            
            with col1:
                st.image(img, caption=f"Archivo: {uploaded_file.name}", use_container_width=True)
                
            with col2:
                st.markdown(f"#### Diagnóstico Principal: **{prediccion_clase_esp.upper()}**")
                
                # Barras de progreso para Top 3
                top_indices = np.argsort(probas)[::-1][:3]
                for idx in top_indices:
                    clase_ingles = class_names[idx]
                    clase_esp = traducir(clase_ingles)
                    prob_val = probas[idx]
                    st.progress(float(prob_val), text=f"{clase_esp} ({prob_val*100:.1f}%)")
                
                if confianza < 70:
                    st.warning("⚠️ Confianza baja. Requiere revisión médica exhaustiva.")
                else:
                    st.success("✅ Diagnóstico con alta confianza.")
                    
                st.markdown("---")
                st.markdown("**Validación Humana (Active Learning)**")
                st.markdown("¿El diagnóstico es correcto? Si no es así, seleccione la clase real para que el modelo aprenda.")
                
                # Nombres en español para el selectbox
                opciones_selectbox = [traducir(c) for c in class_names]
                
                # Formulario de validación
                with st.form(key=f"form_{i}_{uploaded_file.name}"):
                    clase_seleccionada_esp = st.selectbox(
                        "Seleccione el diagnóstico real:",
                        options=opciones_selectbox,
                        index=int(idx_max)
                    )
                    submit_button = st.form_submit_button(label="Guardar Imagen para Re-entrenamiento")
                    
                    if submit_button:
                        # Buscar el nombre en inglés original para la carpeta
                        idx_ingles = opciones_selectbox.index(clase_seleccionada_esp)
                        clase_correcta_ingles = class_names[idx_ingles]
                        
                        # ACTIVE LEARNING: Guardar imagen en la carpeta correcta
                        destino = os.path.join(DATASET_PATH, clase_correcta_ingles, f"val_{uploaded_file.name}")
                        # Asegurarse que el directorio exista
                        os.makedirs(os.path.join(DATASET_PATH, clase_correcta_ingles), exist_ok=True)
                        
                        # Guardar archivo original
                        img.save(destino)
                        st.success(f"✔️ Imagen guardada en '{clase_seleccionada_esp}' para el próximo entrenamiento.")

            st.markdown("---")
