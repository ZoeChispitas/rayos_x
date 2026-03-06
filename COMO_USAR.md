# Cómo usar el proyecto de rayos X (fracturas)

## 1. Activar el entorno virtual (env / venv)

En **Windows** (PowerShell o CMD en la carpeta del proyecto):

```powershell
# Opción A: desde PowerShell
.\venv\Scripts\Activate.ps1

# Opción B: desde CMD o .bat
venv\Scripts\activate.bat
```

Si PowerShell da error de permisos, ejecuta una vez:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

En **Linux/Mac**:
```bash
source venv/bin/activate
```

Cuando el entorno está activo verás `(venv)` al inicio de la línea del terminal.

---

## 2. Instalar dependencias (solo la primera vez)

Con el venv activado:

```bash
pip install -r requirements.txt
```

---

## 3. Interfaz gráfica

- **Opción rápida (Windows):** doble clic en `ejecutar_gui.bat`.  
  Eso activa el venv y abre la GUI.

- **Desde terminal (con venv activado):**
  ```bash
  python rayosx_gui.py
  ```

En la interfaz puedes:
1. Pulsar **"Seleccionar radiografía..."** y elegir una imagen (PNG/JPG).
2. Pulsar **"Diagnosticar"** para ver el tipo de fractura y la confianza.

---

## 4. Uso por línea de comandos (rayosx.py)

Con el venv activado:

```bash
# Diagnosticar imágenes que estén en la carpeta Radiografias_A_Diagnosticar
python rayosx.py
```

Para consolidar datos o entrenar, edita el bloque `if __name__ == "__main__":` en `rayosx.py` y descomenta las líneas que necesites.
