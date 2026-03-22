# -*- coding: utf-8 -*-
import os
import shutil
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator, load_img, img_to_array
from tensorflow.keras.applications import DenseNet121
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint

# --- CONFIGURACIÓN DE RUTAS LOCALES ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_ROOT = os.path.join(BASE_DIR, 'YOLO_Fracturas', 'archive', 'Bone Break Classification')
CONSOLIDATED_PATH = os.path.join(BASE_DIR, 'consolidated_data')
MODEL_FILENAME = 'mejor_modelo_fracturas_densenet.h5'
MODEL_PATH = os.path.join(BASE_DIR, MODEL_FILENAME)

# Carpetas para imágenes nuevas a diagnosticar (ajusta esto si es necesario)
IMG_FOLDER_PATH = os.path.join(BASE_DIR, 'Radiografias_A_Diagnosticar')

class_names = [
    'Avulsion fracture', 'Comminuted fracture', 'Fracture Dislocation', 
    'Greenstick fracture', 'Hairline Fracture', 'Impacted fracture', 
    'Longitudinal fracture', 'Oblique fracture', 'Pathological fracture', 
    'Spiral Fracture'
]
NUM_CLASES = len(class_names)

def consolidar_datos():
    """Organiza las imágenes en carpetas train/valid compatibles con Keras."""
    train_dest = os.path.join(CONSOLIDATED_PATH, 'train')
    valid_dest = os.path.join(CONSOLIDATED_PATH, 'valid')
    
    os.makedirs(train_dest, exist_ok=True)
    os.makedirs(valid_dest, exist_ok=True)

    print(f"Buscando clases en: {DATA_ROOT}")
    if not os.path.exists(DATA_ROOT):
        print(f"🚨 ERROR: No se encontró la carpeta de datos en {DATA_ROOT}")
        return

    fracture_types = [name for name in os.listdir(DATA_ROOT) 
                     if os.path.isdir(os.path.join(DATA_ROOT, name))]

    for class_name in fracture_types:
        print(f"Procesando clase: {class_name}")
        
        # Rutas de origen según la estructura detectada
        source_train = os.path.join(DATA_ROOT, class_name, 'Train')
        source_test = os.path.join(DATA_ROOT, class_name, 'Test')

        # Destinos
        dest_train = os.path.join(train_dest, class_name)
        dest_valid = os.path.join(valid_dest, class_name)

        os.makedirs(dest_train, exist_ok=True)
        os.makedirs(dest_valid, exist_ok=True)

        # Copiar archivos (usamos copy en lugar de move para no alterar el dataset original)
        if os.path.exists(source_train):
            for img_name in os.listdir(source_train):
                shutil.copy(os.path.join(source_train, img_name), os.path.join(dest_train, img_name))
        
        if os.path.exists(source_test):
            for img_name in os.listdir(source_test):
                shutil.copy(os.path.join(source_test, img_name), os.path.join(dest_valid, img_name))

    print("\n✅ Consolidación de datos completada.")

def entrenar_modelo():
    """Configura y entrena el modelo DenseNet121."""
    train_path = os.path.join(CONSOLIDATED_PATH, 'train')
    val_path = os.path.join(CONSOLIDATED_PATH, 'valid')

    if not os.path.exists(train_path) or not os.path.exists(val_path):
        print("🚨 ERROR: No se han consolidado los datos. Ejecuta consolidar_datos() primero.")
        return

    # Generadores
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=15,
        zoom_range=0.1,
        horizontal_flip=True
    )
    val_datagen = ImageDataGenerator(rescale=1./255)

    train_generator = train_datagen.flow_from_directory(
        train_path,
        target_size=(224, 224),
        batch_size=32,
        class_mode='categorical'
    )

    val_generator = val_datagen.flow_from_directory(
        val_path,
        target_size=(224, 224),
        batch_size=32,
        class_mode='categorical'
    )

    # Transfer Learning
    base_model = DenseNet121(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
    for layer in base_model.layers:
        layer.trainable = False

    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(512, activation='relu')(x)
    predictions = Dense(NUM_CLASES, activation='softmax')(x)

    model = Model(inputs=base_model.input, outputs=predictions)

    model.compile(optimizer=Adam(learning_rate=0.0001),
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])

    checkpoint = ModelCheckpoint(
        filepath=MODEL_PATH,
        monitor='val_accuracy',
        save_best_only=True,
        mode='max',
        verbose=1
    )

    print("Iniciando entrenamiento...")
    model.fit(
        train_generator,
        steps_per_epoch=train_generator.samples // train_generator.batch_size,
        epochs=10, 
        validation_data=val_generator,
        callbacks=[checkpoint]
    )

def realizar_diagnostico():
    """Usa el modelo guardado para diagnosticar imágenes en IMG_FOLDER_PATH."""
    if not os.path.exists(MODEL_PATH):
        print(f"🚨 ERROR: No se encontró el modelo en {MODEL_PATH}")
        return

    print(f"Cargando modelo desde {MODEL_PATH}...")
    model = load_model(MODEL_PATH)
    print(f"✅ Modelo cargado correctamente.")

    if not os.path.exists(IMG_FOLDER_PATH):
        os.makedirs(IMG_FOLDER_PATH)
        print(f"Carpeta '{IMG_FOLDER_PATH}' creada. Sube tus radiografías ahí.")
        return

    archivos = [f for f in os.listdir(IMG_FOLDER_PATH) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not archivos:
        print(f"No hay imágenes en {IMG_FOLDER_PATH}")
        return

    print("\n--- INICIANDO DIAGNÓSTICO ---")
    for filename in archivos:
        full_img_path = os.path.join(IMG_FOLDER_PATH, filename)
        try:
            img = load_img(full_img_path, target_size=(224, 224))
            img_array = img_to_array(img)
            img_array = np.expand_dims(img_array / 255.0, axis=0)

            probabilities = model.predict(img_array, verbose=0)[0]
            predicted_index = np.argmax(probabilities)
            confidence = probabilities[predicted_index] * 100
            predicted_class = class_names[predicted_index]

            print(f"\nReporte: {filename}")
            print(f"DIAGNÓSTICO: {predicted_class.upper()}")
            print(f"Confianza: {confidence:.2f}%")
            
            if confidence < 70:
                print("⚠️ Revisión humana recomendada.")

        except Exception as e:
            print(f"Error procesando {filename}: {e}")

if __name__ == "__main__":
    # --- FLUJO DE TRABAJO ---
    
    # 1. Preparar datos (Si es la primera vez que lo corres localmente)
    # consolidar_datos()
    
    # 2. Entrenar (Solo si quieres re-entrenar, de lo contrario usa el modelo .h5 que ya tienes)
    # entrenar_modelo()
    
    # 3. Diagnosticar (Asegúrate de poner imágenes en 'Radiografias_A_Diagnosticar')
    realizar_diagnostico()