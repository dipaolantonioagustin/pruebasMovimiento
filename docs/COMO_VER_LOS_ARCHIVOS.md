# Cómo ver y abrir los archivos del proyecto

Si no te aparecen los archivos, usa este flujo rápido.

## 1) Verifica que abriste la carpeta correcta
En PyCharm: **File → Open...** y elegí la carpeta `pruebasMovimiento` (la raíz del repo).

## 2) Refresca el panel de archivos
En el panel izquierdo (Project), clic derecho sobre el proyecto y usa **Synchronize**.

## 3) Archivo único para arrancar (más simple)
Abrí `app.py`.
Ese archivo contiene todo: captura webcam + MediaPipe + mapeo + envío OSC a REAPER.

## 4) Ejecutar desde terminal
```bash
pip install -r requirements.txt
python app.py --osc-host 127.0.0.1 --osc-port 9000 --camera 0 --fps 30
```

## 5) Si prefieres versión modular
También puedes usar:
```bash
python -m src.main --osc-host 127.0.0.1 --osc-port 9000 --camera 0 --fps 30
```

## 6) Lista de archivos que deberías ver
- `app.py`
- `requirements.txt`
- `docs/COMO_VER_LOS_ARCHIVOS.md`
- `src/main.py`
- `src/capture.py`
- `src/features.py`
- `src/mapping.py`
- `src/osc_out.py`
- `presets/mapping_default.json`
