# 📖 Manual de Usuario - Asistente IA de Rayos X

Bienvenido al sistema automatizado de diagnóstico de fracturas óseas. Este manual le guiará en la instalación y uso de la interfaz gráfica del asistente.

## 1. Requisitos Previos

El programa ha sido configurado para ser lo más autónomo posible. Sin embargo, necesita tener instalados:
*   **Python 3.11** (El sistema fue probado para funcionar con esta versión).
*   Las imágenes de las radiografías deben estar en formato **JPG** o **PNG**.

## 2. Primera Ejecución (Instalación)

Si es la primera vez que abre el proyecto en su computadora, siga estos pasos:

1. Abra una terminal (PowerShell o Comando de Windows) en la carpeta principal del proyecto `proyecto_rayos_x`.
2. Cree y active el entorno virtual (si no lo ha hecho ya):
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. Instale todas las dependencias requeridas (esto puede tardar unos minutos ya que descargará TensorFlow):
   ```powershell
   pip install -r requirements.txt
   pip install gradio
   ```

## 3. Uso del Asistente (Modo Interfaz Web)

La forma recomendada de usar el sistema es a través de su interfaz gráfica estilo chat.

1. **Abra su terminal** en la carpeta del proyecto.
2. **Ejecute el comando de inicio:**
   ```powershell
   .\venv\Scripts\python.exe rayosx_gradio.py
   ```
3. Espere unos segundos. **Se abrirá automáticamente una pestaña en su navegador web** (Chrome, Edge, Firefox, etc.) en la dirección `http://127.0.0.1:7860`.
   *   *Si la pestaña no se abre sola, copie esa dirección y péguela en su navegador.*

### 📸 Cómo realizar un diagnóstico

Una vez que la interfaz web cargue, verá un Asistente en formato de Chat.

1. Haga clic en el **botón con forma de clip (📎)** o el signo **(+)** situado en la parte inferior de la caja de chat.
2. Seleccione la radiografía (JPG o PNG) desde su computadora.
3. Presione el botón de **Enviar** (o la tecla Enter).
4. La Inteligencia Artificial procesará la imagen (tarda 1-3 segundos).
5. **Lea el reporte:** El asistente responderá con el diagnóstico principal, su nivel de confianza y un top 3 de posibilidades alternativas.

## 4. Uso Masivo (Modo Consola Silencioso)

Opcionalmente, si tiene cientos de radiografías y quiere diagnosticarlas sin interfaz gráfica:

1. Coloque todas las radiografías en la carpeta `Radiografias_A_Diagnosticar`.
2. Ejecute este comando en la terminal:
   ```powershell
   .\venv\Scripts\python.exe rayosx.py
   ```
3. El programa imprimirá el diagnóstico de cada radiografía directamente en la terminal.

---

> ⚠️ **Aviso Importante:** Este software es una herramienta de asistencia y validación desarrollada con fines educativos y de investigación. Los diagnósticos emitidos poseen un margen de error y **nunca deben reemplazar el juicio clínico de un médico especialista**.

