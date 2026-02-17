# Plan de acción: proyecto Python + PyCharm + GitHub

## 1) Crear el proyecto en PyCharm
1. Abre PyCharm → **New Project**.
2. Selecciona carpeta del repo: `pruebasMovimiento`.
3. Crea/selecciona un entorno virtual (`.venv`).
4. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## 2) Conectar PyCharm con tu cuenta GitHub
1. PyCharm → **Settings** → **Version Control** → **GitHub**.
2. **Add account** (token o login web).
3. Verifica que Git detecte el repo local.
4. Haz un commit de prueba desde la pestaña **Git**.

## 3) Estructura de archivos propuesta (ya creada)
```text
pruebasMovimiento/
  src/
    __init__.py
    capture.py
    features.py
    mapping.py
    osc_out.py
    main.py
  presets/
    mapping_default.json
  docs/
    SETUP_PYCHARM_GIT.md
  GUIA_PROYECTO_BRAZO_SONORO.md
  requirements.txt
```

## 4) Ejecutar primera prueba local
```bash
python -m src.main --osc-host 127.0.0.1 --osc-port 9000 --camera 0 --fps 30
```

## 5) Checklist mínimo para hoy
- [ ] Proyecto abierto en PyCharm.
- [ ] Cuenta GitHub conectada en PyCharm.
- [ ] Dependencias instaladas en `.venv`.
- [ ] Script `src.main` corriendo sin errores de importación.
- [ ] REAPER recibiendo `/arm/cutoff`, `/arm/resonance`, `/arm/texture_drive`.
