# Informe Sala 2 — Hito 2 (8/08/2026 – 11/08/2026)

## 1. Objetivo asignado

Construir el módulo que prepara la imagen de consulta del usuario **antes** de
enviarla al buscador: detectar la región de interés (la camiseta), eliminar la
información irrelevante (fondo, persona, marco, texto), recortar y normalizar la
imagen para que el sistema encuentre el diseño aunque la consulta no sea idéntica
a la imagen del banco.

> Complementa a Sala 1: Sala 1 limpia el BANCO; Sala 2 limpia la CONSULTA.

## 2. Qué implementaron

| Entregable | Dónde |
|---|---|
| Módulo de preparación de consultas | `webScraping-v2/preprocesar_consulta.py` |
| Integración con la API | `webScraping-v2/api/main.py` → `POST /search/image` (modos `auto`, `procesada`, `original`, `legacy`) |
| Guardado de ambas versiones | `webScraping-v2/data/queries_original/` y `queries_procesadas/` (la API las guarda con un `query_id`) |
| Integración con la interfaz | `webScraping-v2/app.py` (muestra consulta original y preparada, permite comparar el ranking Hito 1 vs Hito 2 y guardar la evaluación) |
| Conjunto de 50 consultas | `evaluation/hito2/consultas/` + `consultas.csv` (10 diseños × 5 versiones) |
| Evaluación Hito 1 vs Hito 2 | `evaluation/hito2/evaluar_hito2.py` → `resultados_hito2.csv`, `resumen_hito2.txt` |
| Evidencia antes/después | `evaluation/hito2/montajes/*.png`, `evidencia_coherencia.txt` |

**Pipeline del módulo** (`preprocesar_consulta.py`):

```
imagen del usuario
  -> recorte de bordes casi uniformes (opcional)
  -> remoción de fondo (U2-Net vía rembg; fallback GrabCut de OpenCV)
  -> bounding box del primer plano
  -> recorte a la región del diseño
  -> centrado sobre lienzo cuadrado
  -> redimension a 320x320
  -> imagen lista para generar embedding
```

Cobertura de casos pedidos: camiseta limpia, sin marco, con fondo, mockup,
persona usando la camiseta, recortada, parte del frente, color modificado,
ligeramente girada y baja calidad (resize de la imagen consultada).

## 3. Qué integrante hizo cada parte

_(Completar con los nombres del equipo.)_

| Parte | Integrante |
|---|---|
| Módulo de preprocesamiento (rembg + recorte + normalización) | **[Nombre 1]** |
| Integración con la API y guardado de ambas versiones | **[Nombre 2]** |
| Interfaz Streamlit (antes/después, comparación de rankings) | **[Nombre 3]** |
| Generación de las 50 consultas de prueba | **[Nombre 1] / [Nombre 4]** |
| Evaluación, métricas y evidencia | **[Nombre 2] / [Nombre 4]** |

## 4. Qué pruebas realizaron

- **Análisis del banco** (Sala 2): 100 imágenes muestreadas de
  `images_final`. 82% son 700×560; el "marco" es un borde fino (~15–24 px);
  el contenido ocupa ~94% del alto y ~93% del ancho. No hay cabecera ni pie
  grandes: la limpieza de la consulta se hace por remoción de fondo y recorte,
  no por recortes fijos.
- **Pruebas unitarias del módulo**: consulta limpia, con fondo, recortada,
  recoloreada, persona y no-camiseta. Se verificó que el recorte conserva el
  patrón (no-camiseta queda casi vacía; fotos de producto conservan todo).
- **Prueba integrada común (50 consultas)**: 10 diseños del banco × 5 versiones
  (exacta, sin_marco, recoloreada, recortada, persona). Cada consulta tiene su
  diseño correcto identificado (`correcto_id`).
- **API en vivo**: `POST /search/image` con `modo=auto` sobre consultas persona,
  variante y recortada; verificación de que guarda `queries_original/` y
  `queries_procesadas/`.
- **Interfaz**: flujo subir → ver antes/después → comparar rankings → guardar
  evaluación en `data/evaluation.csv`.

## 5. Resultados numéricos

### Top 1 y Top 5 (50 consultas comunes, mismo índice CLIP)

| Regla | Top 1 | Top 5 |
|---|---|---|
| Hito 1 (consulta original) | 8/50 (16%) | 28/50 (56%) |
| Hito 2 (consulta preparada) | 10/50 (20%) | 35/50 (70%) |

### Por categoría (Top 5, Hito 1 → Hito 2)

| Categoría | n | Top5 Hito 1 | Top5 Hito 2 | Cambio |
|---|---|---|---|---|
| exacta | 10 | 90% | 70% | −20 pp |
| sin_marco | 10 | 70% | 70% | 0 |
| recoloreada | 10 | 40% | **100%** | **+60 pp** |
| recortada | 10 | 30% | 60% | +30 pp |
| persona | 10 | 50% | 50% | 0 |

### Tiempos (batch, modelo caliente)

- Búsqueda con consulta original: **0.21 s** promedio.
- Búsqueda con consulta preparada: **1.42 s** promedio.
- Preprocesamiento: **1.21 s** promedio.
- Total de las 50 consultas: **71.1 s**.

### Coherencia del Top 5 (misma familia de diseño AIM-PXXX)

- Hito 1: **12%** de los resultados comparten familia con el correcto.
- Hito 2: **15%**.
- La coherencia del Top 2–5 sigue siendo el punto débil (terreno de Sala 3:
  recuperación amplia + reranking).

## 6. Evidencia visual antes/después

Montajes en `evaluation/hito2/montajes/` (consulta | preparada | mejor resultado
Hito 2):

- `c01_recoloreada.png` — recoloreada que en Hito 1 no aparecía y en Hito 2
  encuentra el diseño en Top 5 (categoría recoloreada pasó de 40% a 100%).
- `c04_recortada.png` — recortada que en Hito 1 fallaba y en Hito 2 llega a Top 1.
- `c03_sin_marco.png` — sin marco, estable en ambos.
- `c01_persona.png` — mockup de persona que se recupera en Top 1 en ambos.
- `c07_recoloreada.png` — recoloreada recuperada solo con la versión preparada.

Además, la API guarda por cada consulta la versión original y la preparada en
`webScraping-v2/data/queries_original/` y `queries_procesadas/`.

## 7. Qué funcionó

- **Recoloreadas: 40% → 100% Top 5.** El recorte + normalización cuadrada hace
  que CLIP deje de confundir la consulta recoloreada con diseños de color
  parecido y recupere el diseño correcto.
- **Recortadas: 30% → 60% Top 5.** El centrado/redimensionado del fragmento
  recupera más diseños (c04, c07, c09 llegan al Top 5).
- **Top 5 global 56% → 70%** y **Top 1 16% → 20%** con las mismas 50 consultas.
- **Remoción de fondo U2-Net**: funciona bien en mockups de persona (c01, c06)
  y en fondos planos (camisetas generadas).
- **Integración completa**: la API devuelve ambos rankings (original y
  preparada), el preprocesamiento y el `modelo`; la interfaz permite comparar y
  guardar ambas versiones.

## 8. Qué falló

- **Persona: 5/10 sin mejora** (c02, c03, c04, c05, c07). Cuando el mockup es
  muy distinto (patrón pequeño, ropa/brazos dominando el recorte), CLIP no
  recupera el diseño. Coincide con el alcance declarado del Hito 2 (no se exige
  resolver personas difíciles).
- **Exacta con la imagen preparada baja de 90% a 70%** (c01, c05): redimensionar
  una foto de producto ya limpia puede perjudicar la coincidencia exacta. En la
  interfaz el usuario puede volver al ranking original (Hito 1) para este caso.
- **Sin marco: sin cambio (70%).** El "sin marco" del banco ya es casi todo
  contenido, así que el preprocesado no agrega ganancia.
- **Dato de banco desalineado**: `c02_exacta` (AIM-P001-010) no se recupera a sí
  mismo ni con original ni con preparada — el embedding/ID de ese diseño no
  corresponde a la imagen actual (problema de Sala 1/Sala 4, no del preprocesado).
- **Score no calibrado entre pipelines**: el score de un embedding de 700×560 no
  es comparable con el de 320×320, por eso no usamos "mayor score" como regla
  automática y buscamos siempre con la preparada (mejor Top 5 global).

## 9. Qué mejorarían

- **Fusión de consultas**: combinar el embedding original y el preparado
  (normalizados) y buscar con el promedio — podría mantener el 90% de exacta y
  el 100% de recoloreada a la vez.
- **Mejor modelo de segmentación/detección** (YOLO/SAM de camisetas o persona)
  para los casos de persona difíciles, en lugar de fondo U2-Net genérico.
- **Normalización cuadrada sin introducir bandas blancas** (padding por espejo o
  por borde) para no degradar las consultas ya limpias.
- **Semblanza de scores** entre tamaños (re-calibrar) para habilitar reglas
  automáticas más finas.
- **Calidad Top 5 humana pendiente**: clasificar Muy similar / Similar / Poco
  similar / No relacionado por consulta (tarea manual del equipo sobre la
  interfaz; las 50 consultas ya están preparadas).

## 10. Qué código puede explicar individualmente cada integrante

- `webScraping-v2/preprocesar_consulta.py` — pipeline de limpieza completo
  (recorte de bordes, rembg, bbox, centrado, resize).
- `webScraping-v2/api/main.py` → `search_image` — modos de búsqueda, guardado de
  ambas versiones y respuesta enriquecida.
- `webScraping-v2/app.py` — interfaz de comparación y registro de evaluación.
- `evaluation/hito2/generar_consultas_hito2.py` — cómo se construyeron las 50
  consultas con su diseño correcto conocido.
- `evaluation/hito2/evaluar_hito2.py` — métricas Top 1 / Top 5 y tiempos.

---

## Cómo reproducir

```bash
# 1. Generar las 50 consultas (si no existen)
python evaluation/hito2/generar_consultas_hito2.py

# 2. Evaluar Hito 1 vs Hito 2 (desde webScraping-v2/, venv activa)
python evaluation/hito2/evaluar_hito2.py

# 3. Evidencia (montajes + coherencia)
python evaluation/hito2/evidencia_hito2.py

# 4. Levantar API y verificar
python -m uvicorn api.main:app --port 8000     # desde webScraping-v2/

# 5. Interfaz
streamlit run app.py                            # desde webScraping-v2/
```

Dependencias nuevas: `rembg`, `onnxruntime`, `opencv-python-headless`
(`pip install rembg onnxruntime opencv-python-headless`).
