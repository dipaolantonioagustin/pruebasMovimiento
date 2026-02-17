# Guía inicial: Brazo en el espacio → Textura sonora (PyCharm + MediaPipe + REAPER)

## 1) Objetivo artístico
Transformar el movimiento de un brazo (posición, velocidad y gesto) en parámetros de sonido en tiempo real, para controlar texturas sonoras en REAPER.

---

## 2) Arquitectura recomendada

### A. Captura y análisis de movimiento (Python + MediaPipe)
- Usar MediaPipe Pose (o Hands si necesitas más detalle de muñeca/mano).
- Extraer landmarks clave del brazo: hombro, codo, muñeca.
- Calcular variables derivadas:
  - Posición normalizada (X, Y, Z).
  - Velocidad de la muñeca.
  - Ángulo codo-hombro-muñeca.
  - Energía de movimiento (aceleración o suma de deltas).

### B. Mapeo sonoro (capa intermedia)
Convertir variables de movimiento en controles musicales:
- Altura del brazo (Y) → filtro (cutoff).
- Apertura/ángulo del codo → resonancia o mezcla dry/wet.
- Velocidad → densidad/granularidad o drive/saturación.
- Proximidad a cámara (Z) → volumen/reverb size.

### C. Envío a REAPER
Opciones prácticas:
1. **OSC (recomendado):** Python envía mensajes OSC, REAPER recibe y mapea a parámetros.
2. **MIDI CC:** Python envía CC virtuales a REAPER.

Para prototipado artístico rápido, OSC suele ser más flexible y legible.

---

## 3) Rol de Google Colab vs PyCharm

### Cuándo usar Colab
- Experimentación rápida con modelos y visualización.
- Pruebas offline con videos grabados.
- Ajuste de features y limpieza de señal.

### Cuándo usar PyCharm (local)
- Performance en tiempo real con webcam.
- Comunicación estable con REAPER (OSC/MIDI local).
- Organización del proyecto en módulos y control de versiones.

> Recomendación: usa Colab para I+D y valida el pipeline final en PyCharm local.

---

## 4) Pipeline mínimo viable (MVP)

1. Captura webcam en Python.
2. Detecta landmarks del brazo con MediaPipe.
3. Suaviza señal (filtro EMA simple).
4. Mapea 2-3 variables a 2-3 parámetros sonoros.
5. Envía OSC a REAPER.
6. Graba improvisaciones y ajusta mapeo artístico.

---

## 5) Propuesta de estructura de carpetas

```text
brazo-sonoro/
  src/
    capture.py          # webcam + mediapipe
    features.py         # angulos, velocidad, energia
    mapping.py          # reglas movimiento -> sonido
    osc_out.py          # cliente OSC
    main.py             # bucle principal
  presets/
    mapping_default.json
  docs/
    sesiones.md         # notas artisticas por sesion
  requirements.txt
```

---

## 6) Mapeo artístico (punto de partida)

- `wrist_y` (altura muñeca):
  - arriba → más brillo (cutoff alto)
  - abajo → más oscuro (cutoff bajo)

- `wrist_speed` (velocidad):
  - lenta → textura estable
  - rápida → mayor modulación/caos

- `elbow_angle` (ángulo):
  - cerrado → más resonancia
  - abierto → más aire/espacio

Añade histéresis o zonas muertas para evitar “nerviosismo” sonoro.

---

## 7) Calibración y estabilidad

Antes de cada sesión:
1. Toma 10-20 segundos de postura neutra.
2. Calcula mínimos/máximos aproximados por variable.
3. Normaliza a rango [0, 1].
4. Aplica suavizado (EMA) y límites de tasa de cambio.

Esto mejora muchísimo el control expresivo.

---

## 8) Siguiente sprint (concreto)

- Día 1:
  - levantar captura + landmarks de brazo
  - imprimir variables crudas en consola
- Día 2:
  - implementar suavizado + normalización
  - testear estabilidad de señal
- Día 3:
  - enviar 3 controles por OSC a REAPER
  - mapear a 1 instrumento y 2 FX
- Día 4:
  - sesión artística grabada de 20 minutos
  - documentar qué mapeos “musicales” funcionaron mejor

---

## 9) Riesgos comunes y cómo evitarlos

- **Latencia alta:** bajar resolución de cámara y simplificar features.
- **Señal inestable:** más suavizado y zonas muertas.
- **Mapeo poco musical:** limitar rangos y usar curvas no lineales.
- **Fatiga performativa:** diseñar “macro-gestos” cómodos, no microgestos.

---

## 10) Próximo paso recomendado

Si quieres, en el siguiente paso te puedo preparar:
1. un `requirements.txt` mínimo,
2. un `main.py` funcional con MediaPipe + OSC,
3. y una plantilla de mapeo para REAPER.

Con eso arrancas una primera prueba performática el mismo día.
