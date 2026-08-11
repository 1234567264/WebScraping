# AI_LOG.md - Registro de prompts de IA

> Requisito del supervisor: registrar cada prompt de IA usado en el proyecto.

## Fecha: 2026-08-07 (rama sala-2-v2)

### Prompt 1 - Interfaz como cliente puro de API
**Propósito:** Reemplazar la interfaz que hacía búsqueda local por un cliente
que SOLO consume la API de Sala 3.
**Resultado:** `frontend/app.py` — sube la imagen, hace `POST /search/image`,
muestra Top 5 (imagen, ID, nombre, proveedor, URL, score), permite clasificar cada
resultado (Correcto / Útil / Incorrecto) y guarda la evaluación en
`data/evaluation.csv`. Sin embeddings ni búsqueda local.

### Prompt 2 - Script de métricas
**Propósito:** Calcular la precisión Top 1, Top 5, falsos positivos, falsos
negativos y tiempo promedio a partir de `evaluation.csv`.
**Resultado:** `scripts/reporte_metricas.py`.

### Prompt 3 - Protocolo de evaluación (20 pruebas)
**Propósito:** Definir el plan de las 20 consultas de prueba y las imágenes del
grupo A.
**Resultado:** `evaluation/test_plan.csv`, `evaluation/README.md` y 5 imágenes de
prueba en `evaluation/test_images/`.

### Prompt 4 - Verificación de la API de Sala 3
**Propósito:** Verificar que `api/search_engine.py` (conector de
Sala 1 + embeddings de Sala 4) carga los 1000 productos y responde búsquedas.
**Resultado:** Confirmado: 1000 productos, 1000 embeddings (1000,512), búsqueda
Top-K OK.

## Fecha: 2026-08-10 (rama sala-1, Hito 2)

### Prompt 5 - Informe de formatos del banco (Actividad 1 de Sala 1)
**Propósito:** Determinar cuántos formatos visuales existen, posición de marcos,
cabecera, pie/URL, ubicación de frente y espalda, y % recortable por reglas simples,
sobre una muestra ≥100 (se analizaron las 1000).
**Resultado:** `scripts/analizar_formatos.py` → `data/informe_formatos.txt` +
`data/detalle_formatos.csv`. Hallazgos: 5 formatos (1 dominante con 99,4%),
cabecera en 99,7%, pie/URL en 99,8%, frente 17–56% y espalda 57–97% del ancho,
recorte medio estimado 48,7%.

### Prompt 6 - Revisión de la muestra de 50 (Actividad 5 de Sala 1)
**Propósito:** Completar `data/revision_humana_50.csv` (muestra aleatoria semilla 42)
con la clasificación de cada normalizada: solo frente+espalda, sin logo, sin marco,
sin cabecera/pie, sin cortes, sin deformación, lienzo uniforme.
**Resultado:** `scripts/revisar_muestra_50.py` aplica criterios objetivos de píxel
cruzados con el estado del pipeline → **49/50 correctas (98%), 1 dudosa**
(`AIM-P003-164`, espalda lisa indistinguible del fondo), 0 incorrectas.
`data/informe_revision_humana.txt` + hoja de contacto para visto bueno visual final.

## Fecha: 2026-08-10 (rama piloto, complemento Sala 3 / Hito 2)

### Prompt 7 - Bug de rutas no-ASCII en el reranking del Hito 2
**Propósito:** El motor de Sala 3 (`api/search_engine_hito2.py`) dejaba
`score_color = 0` en todas las consultas: `cv2.imread` falla silenciosamente con
rutas que contienen caracteres no-ASCII (p. ej. la carpeta `Imágenes` del perfil
de Windows).
**Resultado:** lectura de imágenes reemplazada por PIL (`Image.open` → BGR) en
`_leer_bgr_desde_ruta` y `_a_imagen_bgr`. Verificado: el reranking por color
ahora produce scores > 0 y el Top 1 es correcto en consultas exactas y sin marco.

### Prompt 8 - Reranking por regiones y estructura
**Propósito:** Complementar el reranking del Hito 2 con los criterios que pide
TRABAJO.md: comparación por regiones (frente/espalda) y distribución del patrón,
con pesos en constantes para calibrar (no asumidos).
**Resultado:** `api/search_engine_hito2.py` ahora combina 5 señales: embedding CLIP
(0,55) + color HSV global (0,15) + color frente (0,10) + color espalda (0,10) +
estructura en grises 32×32 (0,10). Respuesta ampliada con `score_color_global`,
`score_color_frente`, `score_color_espalda`, `score_estructura`, `score_reranking`,
`posicion_final` y `modelo_utilizado`.

### Prompt 9 - Comparación Hito 1 vs Hito 2 con evidencia
**Propósito:** Medir objetivamente si el motor nuevo mejora al del Hito 1 usando
las mismas consultas, con tiempos por consulta y evidencia guardada.
**Resultado:** `scripts/compare_hito1_hito2.py` (lee `evaluation/consultas_hito2.csv`,
mide Top 1/Top 5/tiempos, guarda `data/comparacion_hito1_hito2.csv` + `.json`) y
`scripts/generar_consultas_prueba.py` (genera las 20 consultas derivables:
10 exactas + 10 sin marco; documenta cómo agregar las 30 restantes).
**Resultado real sobre 20 consultas:** Hito 1: Top1 80% / Top5 100% (2 294 ms);
Hito 2: Top1 90% / Top5 95% (2 665 ms). En sin_marco el Top 1 sube de 6/10 a 8/10.

## Fecha: 2026-08-11 (rama sala-2 / Hito 2)

### Prompt 10 - Migración de Sala 2 a la estructura canónica del repo
**Propósito:** El supervisor marcó que `REPORTES_HITO2.md` estaba desactualizado
(decía PENDIENTE y 20/50), que los números eran inconsistentes (resumen 35/50 vs
informe 8/50), que `frontend/app.py` no enviaba `modo`, que faltaban
`data/queries_original/` y `data/queries_procesadas/`, que
`evaluation/consultas_hito2.csv` solo tenía 20 filas y que la carpeta `hito2/`
debía borrarse moviendo sus archivos a las carpetas correspondientes.
**Resultado:**
- `evaluation/consultas_hito2.csv` reconstruido a **50 filas** (10 diseños × 5
  versiones) con las imágenes reales de `data/consultas/` (nomenclatura nueva:
  `cNN_exacto.jpg`, `cNN_sin_marco.jpg`, `cNN_recoloreado.jpeg`, `cNN_recorte.jpg`,
  `cNN_cuerpo.jpeg`) y su `id_correcto`.
- Run canónico nuevo en `data/resultados_hito2.csv` + `data/resumen_hito2.txt`:
  **Hito 1 Top1 35/50 · Hito 2 Top1 33/50 · auto 37/50; Top5 38/50 · 36/50 · 39/50**.
  Borrado el set viejo (`resultados_hito2_sala2_referencia.csv`,
  `resumen_hito2_sala2.txt`, `evidencia_coherencia_sala2.txt`).
- Scripts movidos a `scripts/` con rutas canónicas: `evaluar_hito2.py`,
  `evidencia_hito2.py`, `generar_consultas_hito2.py` (leen `evaluation/consultas_hito2.csv`
  y `data/consultas/`, escriben en `data/`).
- `frontend/app.py` integra selector de modo (`auto`, `procesada`, `original`,
  `completo`, `legacy`), vista antes/después (original vs preparada) y comparación
  de rankings Hito 1 vs Hito 2.
- Generadas `data/queries_original/` (50) y `data/queries_procesadas/` (50) con la
  venv usando `api/preprocesar_consulta.py` (backend GrabCut).
- `REPORTES_HITO2.md` actualizado: Sala 2 **COMPLETO**, 50/50 consultas, métricas
  finales con los números nuevos, comparación por casos A–F y próximos pasos.
- `evaluation/INFORME_SALA2_HITO2.md` actualizado a los números nuevos y movido a
  su carpeta canónica.
- Carpeta `hito2/` eliminada por completo.
