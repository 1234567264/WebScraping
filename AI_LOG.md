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
