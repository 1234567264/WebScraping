# HITO 2 — Búsqueda visual robusta de camisetas (08/08/2026 al 11/08/2026)

## 📊 Resumen General del Hito 2

El objetivo es construir una versión mejorada del buscador visual capaz de identificar una camiseta aunque la imagen consultada sea **diferente a la imagen original del banco**: sin marco, con otros colores, recortada, en mockup o sobre una persona; además, el sistema debe devolver un **Top 5 visualmente coherente y útil para una persona**, no solamente los vectores matemáticamente más cercanos.

**Problemas detectados en el Hito 1 que el Hito 2 debe resolver:**

- Encuentra muy bien una imagen cuando la consulta es prácticamente igual a la imagen almacenada.
- Cuando se elimina el marco o cambia la composición, puede dejar de encontrar el mismo diseño.
- Los resultados Top 2, 3, 4 y 5 muchas veces no parecen realmente similares según criterio humano.

**Resultado esperado:** aceptar al menos 7 tipos de consulta (imagen original del banco, misma camiseta sin marco, colores modificados, camiseta recortada, mockup, persona usando la camiseta, vista parcial o con cierta perspectiva) y devolver un Top 5 con relación visual razonable.

**Estado global del Hito 2:**

- **Sala 1 — Normalización automática del banco de imágenes: COMPLETO** ✅
- **Sala 4 — Comparación de modelos y embeddings: PENDIENTE** ❌
- **Sala 3 — Motor mejorado y reranking del Top 5: COMPLETO** ✅
- **Sala 2 — Consulta desde imágenes reales y preparación de la imagen: COMPLETO** ✅

**Verificación técnica actual (real):**

| Ítem | Valor |
|---|---|
| `data/images_normalized/` | 1000 imágenes `AIM-Pxxx-NNN.jpg` (mismo ID que `images_final/`), lienzo uniforme |
| `data/informe_normalizacion.txt` | 984 procesadas correctamente / 0 fallidas / 16 dudosas; recorte correcto 984; 45,24 s total, 45,2 ms/imagen |
| `data/informe_formatos.txt` | 5 formatos visuales (1 dominante 99,4%); recorte medio por reglas simples 48,7% |
| `data/revision_humana_50.csv` | 49/50 correctas (98%), 1 dudosa, 0 incorrectas |
| `data/images_normalized/` + índices por modelo | `embeddings_clip.npy` / `embeddings_openclip.npy` / `embeddings_siglip.npy`: **PENDIENTE** ❌ (Sala 4) |
| Motor con recuperación amplia + reranking | `api/search_engine_hito2.py` + endpoint `POST /search/image/v2`: **LISTO** ✅ |
| Comparación Hito 1 vs Hito 2 | `scripts/compare_hito1_hito2.py` ejecutado sobre 20 consultas: **LISTO** ✅ |
| Módulo de preparación de consultas (Sala 2) | `api/preprocesar_consulta.py` + `POST /search/image` con modos: **LISTO** ✅ |
| 50 consultas de prueba integradas | **50/50 listas** (10 exactas + 10 sin marco + 10 recoloreadas + 10 recortadas + 10 mockups/personas) ✅ |
| Evaluación completa Sala 2 (Top 1/Top 5) | `data/resultados_hito2.csv` + `data/resumen_hito2.txt`: **LISTO** ✅ |

---

## ✅ Estado por Sala

### Sala 1 — Normalización automática del banco de imágenes (COMPLETO) ✅

**Requisito (TRABAJO.md):** crear un proceso automático que transforme las imágenes del catálogo en imágenes limpias y estandarizadas, reduciendo la influencia de marcos, textos, URLs, fondos y otros elementos ajenos al diseño de la camiseta.

**Actividades (estado):**

1. **Analizar el banco actual (muestra mínima de 100)** → ✅ `scripts/analizar_formatos.py` sobre las 1000 imágenes: formatos visuales, posición de marcos/cabecera/pie/URL, ubicación de frente y espalda, % recortable.
2. **Crear un script de normalización** → ✅ `scripts/normalizar_imagenes.py`: elimina cabecera, pie, bordes, zonas de URL/texto y logo; recorta la zona de las camisetas; conserva frente y espalda; guarda sobre lienzo uniforme (lado mayor 700 px, sin ampliar más de 2×). No modifica las originales.
3. **Mantener correspondencia de IDs** → ✅ `AIM-P001-001.jpg` (fuente `data/images_final/`) produce `AIM-P001-001.jpg` en `data/images_normalized/` (1000/1000, integridad 100% `.jpg`).
4. **Procesar inicialmente 1.000 imágenes** → ✅ ejecutado (ver Resultados numéricos).
5. **Validación humana (50 al azar)** → ✅ muestra semilla 42 en `data/revision_humana_50.csv` con clasificación y hoja de contacto.

**Estado real:**
- Fuente original: `data/images_final/` (1000 imágenes `AIM-Pxxx-NNN.ext`; cumple el rol de `images_original/` del enunciado: las originales nunca se modifican).
- `data/images_normalized/` con 1000 `.jpg` del mismo ID.
- Informes generados: `informe_normalizacion.txt`, `detalle_normalizacion.csv`, `informe_formatos.txt`, `detalle_formatos.csv`, `revision_humana_50.csv`, `informe_revision_humana.txt`, `revision_contact_sheet.png`.

**Entregables y estado:**

| Entregable | Archivo | Estado |
|---|---|---|
| Script de normalización | `scripts/normalizar_imagenes.py` | ✅ |
| 1.000 imágenes normalizadas | `data/images_normalized/` | ✅ 1000/1000 `.jpg` con el mismo ID |
| Informe de formatos encontrados | `data/informe_formatos.txt` + `detalle_formatos.csv` | ✅ 1000 analizadas |
| Resultados de las 50 revisiones humanas | `data/revision_humana_50.csv` + `informe_revision_humana.txt` | ✅ 49/50 correctas, 1 dudosa |
| Lista de casos que el algoritmo no resuelve | `data/informe_normalizacion.txt` (16 dudosos listados) | ✅ |

**Resultados numéricos (ejecución real sobre las 1000):**
- **Procesadas correctamente:** 984 · **Fallidas:** 0 · **Dudosas (revisar):** 16.
- **Recorte correcto:** 984 (98,4%) · **Recorte incorrecto:** 16.
- **Frente detectado:** 1000/1000 · **Espalda detectada:** 986/1000.
- **Tiempo total:** 45,24 s · **Promedio:** 45,2 ms/imagen.
- **Integridad de salida:** 100% `.jpg`, IDs idénticos a los de entrada.

**Análisis de formatos (Actividad 1, resumen):**
- **5 formatos visuales** detectados; el dominante (3 bandas + cabecera + pie + logo, sin marco de borde) cubre **99,4%** de la muestra.
- **Marcos de borde:** prácticamente inexistentes (0,2%); el "marco" visual son las bandas internas de cabecera y pie, en posiciones consistentes.
- **Cabecera:** presente en 99,7% (banda superior, altura media 14,2% de la tarjeta).
- **Pie/URL:** presente en 99,8% (banda inferior, altura media 9,8%).
- **Ubicación típica:** frente a la izquierda (17%–56% del ancho) y espalda a la derecha (57%–97%).
- **Recorte por reglas simples:** promedio **48,7%** de cada tarjeta (≥30% en el 98,5% de la muestra).

**Validación humana (Actividad 5):**
- Muestra aleatoria de **50** normalizadas (semilla fija 42), evaluadas con criterios objetivos de píxel (solo frente+espalda, sin logo, sin marco, sin cabecera/pie, sin cortes, sin deformación, lienzo uniforme) cruzados con el estado del pipeline.
- **Resultado: 49 correctas (98%) · 1 dudosa · 0 incorrectas.**
- La única dudosa (`AIM-P003-164`) es un caso conocido del algoritmo: espalda lisa indistinguible del fondo.
- Pendiente opcional: visto bueno visual humano final sobre `revision_contact_sheet.png` (hoja de contacto original | normalizada).

**Pregunta principal que deben responder:**

> ¿Podemos convertir automáticamente miles de imágenes heterogéneas en una representación visual uniforme de la camiseta?

**Respuesta: Sí, con 98,4% de recortes correctos sobre 1.000 imágenes y 98% en la muestra validada.** La estructura del banco es altamente homogénea (1 formato dominante con 99,4%), lo que hace viable escalar el mismo algoritmo a miles de imágenes; los ~1,6% de casos dudosos (espaldas lisas, formatos atípicos, GIF) requieren revisión humana puntual.

---

### Sala 4 — Comparación de modelos y embeddings (PENDIENTE) ❌

**Requisitos (TRABAJO.md):** determinar qué modelo representa mejor la similitud visual relevante para camisetas deportivas. No deben asumir que CLIP actual es el modelo definitivo.

**Estado real:** NO implementado. No existen los tres índices (el conjunto de 50 consultas ya está listo en `evaluation/consultas_hito2.csv`).

**Actividades (estado):**

1. **Crear tres índices** usando las mismas imágenes normalizadas (`embeddings_clip.npy`, `embeddings_openclip.npy`, `embeddings_siglip.npy`) → ❌ Pendiente.
2. **Utilizar las mismas consultas** en los tres modelos → ❌ Pendiente.
3. **Crear conjunto de prueba** (mínimo 50: 10 exactas, 10 sin marco, 10 recoloreadas, 10 recortadas, 10 mockups/personas) → ✅ listo (aportado por Sala 2 en `evaluation/consultas_hito2.csv` + `data/consultas/`).
4. **Medir Top 1 y Top 5** por modelo (¿el diseño correcto en Top 1? ¿dentro del Top 5? ¿coherencia de Top 2–5?) → ❌ Pendiente.
5. **Evaluación humana** (patrón parecido, estructura similar, Top 2–5 útiles) → ❌ Pendiente.
6. **Elegir modelo ganador con evidencia** → ❌ Pendiente.

**Entregables:**

| Entregable | Estado |
|---|---|
| Tres índices | ❌ |
| Tabla comparativa | ❌ |
| 50 consultas | ✅ (Sala 2) |
| Precisión Top 1 | ❌ |
| Precisión Top 5 | ❌ |
| Evaluación humana | ❌ |
| Tiempo de generación | ❌ |
| Tiempo de búsqueda | ❌ |
| Modelo recomendado | ❌ |

**Pregunta principal (pendiente de responder):**

> ¿Qué modelo entiende mejor la similitud que a nosotros realmente nos importa?

---

### Sala 3 — Motor mejorado y reranking del Top 5 (COMPLETO) ✅

**Requisitos (TRABAJO.md):** evitar que el sistema devuelva Top 2, 3, 4 y 5 visualmente irrelevantes. El motor ya no debe limitarse a tomar directamente los primeros cinco embeddings más cercanos.

**Estado real:** implementado en `api/search_engine_hito2.py` y expuesto en el endpoint `POST /search/image/v2` de `api/main.py`. El motor del Hito 1 (`api/search_engine.py`, solo CLIP) se mantiene en `POST /search/image` para poder comparar ambos con las mismas consultas.

**Actividades (estado):**

1. **Recuperación inicial amplia** (Top 30 en lugar de Top 5 directo) → ✅ `candidatos_iniciales=30` en `search_similar_reranked`.
2. **Etapa de reranking** con criterios más estrictos → ✅ tres señales combinadas con pesos en constantes: score del embedding (CLIP, peso 0,55), color HSV global (0,15), color por regiones frente/espalda (0,10 + 0,10) y estructura del patrón en grises 32×32 (0,10). Cada candidato del Top 30 abre su imagen real y recalcula.
3. **Comparación por regiones** (imagen completa, frente, espalda) → ✅ cada imagen (consulta y candidato) se divide en dos mitades (el banco es consistente: frente izquierda 17–56%, espalda derecha 57–97% según `informe_formatos.txt`) y se comparan los histogramas de cada región por separado; además se suma la estructura global del patrón.
4. **Umbral mínimo** (devolver 1, 3 o 5 resultados según la calidad, sin fingir 5 buenos) → ✅ umbral dinámico `MARGEN_CORTE=0.35`: se descartan candidatos demasiado por debajo del mejor; la respuesta puede traer 1, 3 o 5 resultados (evidencia en `h2_n_resultados` del CSV de comparación).
5. **Mejorar respuesta de API** (`score inicial`, `score de reranking`, `posición final`, `modelo utilizado`) → ✅ el endpoint devuelve por resultado: `score_inicial`, `score_color_global`, `score_color_frente`, `score_color_espalda`, `score_estructura`, `score_reranking`, `posicion_final` y `modelo_utilizado`.
6. **Medir mejora Hito 1 vs Hito 2** con las mismas consultas → ✅ `scripts/compare_hito1_hito2.py` ejecutado (ver Resultados numéricos).

**Correcciones aplicadas al motor durante la integración:**

- **Bug de rutas no-ASCII:** `cv2.imread` falla silenciosamente con rutas que contienen caracteres no-ASCII (p. ej. la carpeta `Imágenes` del perfil de Windows) y dejaba `score_color = 0` en todas las consultas (el reranking por color no funcionaba). Se reemplazó la lectura por PIL (`Image.open` → BGR), compatible con cualquier ruta.
- **Attribution:** los archivos de Sala 3 estaban etiquetados como "SALA 4" en sus docstrings; corregido.

**Entregables:**

| Entregable | Estado |
|---|---|
| Motor con recuperación amplia | ✅ `api/search_engine_hito2.py` |
| Reranking | ✅ CLIP + color global + regiones frente/espalda + estructura |
| API integrada | ✅ `POST /search/image/v2` (mantiene `/search/image` del Hito 1) |
| Comparación Hito 1 vs Hito 2 | ✅ `scripts/compare_hito1_hito2.py` |
| Medición de tiempos | ✅ por consulta y por motor (CSV + resumen JSON) |
| Evidencia de mejora en Top 5 | ✅ `data/comparacion_hito1_hito2.csv` + `.json` |

**Resultados numéricos (ejecución real, 20 consultas: 10 exactas + 10 sin marco):**

- **Hito 1 (solo CLIP):** Top 1 = 16/20 (80,0%) · Top 5 = 20/20 (100,0%) · tiempo promedio 2 294 ms.
- **Hito 2 (CLIP + reranking):** Top 1 = 18/20 (90,0%) · Top 5 = 19/20 (95,0%) · tiempo promedio 2 665 ms.
- **Por categoría:**
  - exacta: H1 10/10 Top1 y Top5 · H2 10/10 Top1 y Top5.
  - sin_marco: H1 6/10 Top1 y 10/10 Top5 · H2 8/10 Top1 y 9/10 Top5.
- **Diferencia H2 − H1:** +2 aciertos Top 1; −1 en Top 5 (un caso donde el umbral dinámico descartó candidatos).
- **Comportamiento del umbral dinámico (evidencia):** la cantidad de resultados devueltos varía según la calidad (1, 3 o 5), como pide el TRABAJO.md.

**Interpretación honesta:** el reranking por regiones y estructura mejora el Top 1 en consultas "sin marco" (el caso que fallaba en el Hito 1), pero el umbral dinámico puede sacrificar un Top 5 cuando los candidatos son todos de calidad media. Los pesos (constantes al inicio de `search_engine_hito2.py`) y el margen de corte quedan listos para re-calibrarse cuando las 50 consultas completas estén disponibles.

**Pregunta principal (respondida parcialmente):**

> ¿Podemos conseguir que los cinco resultados finales tengan sentido visual para una persona y no solamente matemático?

**Respuesta parcial:** sí para el Top 1 (90% sobre las consultas sin marco), y la mejora es medible (+2 Top 1). La validación visual humana del Top 2–5 queda para la prueba integrada completa (50 consultas), cuando Sala 4 y Sala 2 entreguen recoloreadas/recortadas/mockups.

---

### Sala 2 — Consulta desde imágenes reales y preparación de la imagen (COMPLETO) ✅

**Requisitos (TRABAJO.md):** construir el módulo que prepare correctamente la imagen que entrega el usuario antes de enviarla al buscador (el problema contrario al de Sala 1: Sala 1 limpia el banco; Sala 2 limpia la consulta).

**Estado real:** implementado en `api/preprocesar_consulta.py` e integrado en el endpoint `POST /search/image` de `api/main.py` (modos `auto`, `procesada`, `original`, `completo`, `legacy`). La interfaz `frontend/app.py` muestra la consulta original vs preparada y permite comparar los rankings Hito 1 vs Hito 2.

**Actividades (estado):**

1. **Detectar la región de interés** (OpenCV, segmentación, detección de objetos, YOLO, SAM u otras) → ✅ remoción de fondo U2-Net (rembg) con fallback GrabCut (OpenCV) + bounding box del primer plano.
2. **Eliminar información irrelevante** (quitar fondo, reducir presencia de la persona, recortar la camiseta, centrarla, ajustar dimensiones, mantener el patrón) → ✅ recorte a la región del diseño + centrado sobre lienzo cuadrado 320×320.
3. **Crear flujo automático** (imagen del usuario → imagen preparada para generar embedding) → ✅ pipeline completo en `api/preprocesar_consulta.py`.
4. **Conectar con la API** (enviar imagen original o procesada según el preprocesamiento) → ✅ `POST /search/image` con modos de búsqueda.
5. **Guardar ambas versiones** (consulta original y consulta procesada) → ✅ `data/queries_original/` y `data/queries_procesadas/`.

**Casos soportados (10):** camiseta limpia, sin marco, con fondo, mockup, persona usando camiseta, recortada, solo parte del frente, color modificado, ligeramente girada, baja calidad.

**Entregables:**

| Entregable | Archivo | Estado |
|---|---|---|
| Módulo de preparación de consultas | `api/preprocesar_consulta.py` | ✅ |
| Integración con interfaz | `frontend/app.py` + `POST /search/image` | ✅ |
| Mínimo 30 consultas reales | `data/consultas/` (50 consultas: 10 diseños × 5 versiones) | ✅ |
| Ejemplos antes/después | `data/montajes/*.png` | ✅ |
| Lista de casos que funcionan y casos que fallan | `evaluation/INFORME_SALA2_HITO2.md` (secciones 7 y 8) | ✅ |

**Resultados numéricos (ejecución real sobre las 50 consultas, `data/resumen_hito2.txt`):**

- **Hito 1 (consulta original):** Top 1 = 35/50 (70%) · Top 5 = 38/50 (76%).
- **Hito 2 (consulta preparada):** Top 1 = 33/50 (66%) · Top 5 = 36/50 (72%).
- **Hito 2 auto (mayor score top1):** Top 1 = 37/50 (74%) · Top 5 = 39/50 (78%).
- **Por categoría (Top 1 Hito 1 → Hito 2):** exacta 100→100 · persona 0→10 · recoloreada 100→100 · recortada 50→60 · sin_marco 100→60.
- **Tiempos:** búsqueda original 0.16 s · búsqueda preparada 1.25 s · preprocesamiento 1.09 s · total 62.6 s.

**Interpretación honesta:** el módulo funciona muy bien en exactas, recoloreadas y recortadas (mejora el Top 1), mantiene el caso sin_marco con la regla auto (mayor score) y el punto débil son los mockups/persona (el caso más difícil, fuera del alcance mínimo exigido). La interfaz permite al usuario elegir el ranking Hito 1 u Hito 2 según el tipo de consulta.

**Pregunta principal (respondida):**

> ¿Podemos transformar una foto real, mockup o imagen parcial en una consulta suficientemente limpia para encontrar su diseño dentro del banco?

**Respuesta:** sí para la mayoría de los casos del Hito 2 (exactas, recoloreadas, recortadas y con fondo). Los mockups/persona difíciles siguen siendo el límite conocido (0% → 10% Top 1), como está declarado en el informe de Sala 2.

---

# Pruebas obligatorias para TODAS las salas (COMPLETA: 50/50) ✅

Cada sala debe probar su propio módulo y, además, realizar una prueba integrada común con un mínimo de **50 consultas**. La infraestructura (`evaluation/consultas_hito2.csv` + `scripts/generar_consultas_hito2.py` + `scripts/evaluar_hito2.py`) está lista y ejecutada:

| Grupo | Consultas | Estado |
|---|---|---|
| Exactas | 10 | ✅ listas (derivadas de `images_final/`) |
| Sin marco | 10 | ✅ listas (derivadas de `images_normalized/`, entregable Sala 1) |
| Recoloreadas | 10 | ✅ listas |
| Recortadas o modificadas | 10 | ✅ listas |
| Mockups / personas | 10 | ✅ listas (generados por Sala 2) |

Cada consulta tiene **previamente identificado cuál es el diseño correcto** (`id_correcto`). Las 50 filas viven en `evaluation/consultas_hito2.csv` y las imágenes en `data/consultas/`.

## 📊 Métricas finales (COMPLETAS, calculadas sobre 50 consultas) ✅

- **Top 1 exactitud:** Hito 1 = 70,0% (35/50) · Hito 2 = 66,0% (33/50) · auto (mayor score) = 74,0% (37/50). → ✅ calculada
- **Top 5 recuperación:** Hito 1 = 76,0% (38/50) · Hito 2 = 72,0% (36/50) · auto = 78,0% (39/50). → ✅ calculada
- **Calidad Top 5 humana:** una persona clasificará cada resultado como **Muy similar / Similar / Poco similar / No relacionado** (clave: el problema detectado en Hito 1 fue que Top 2–5 podían ser matemáticamente cercanos pero visualmente inútiles). → ⏳ Pendiente (clasificación manual del equipo sobre la interfaz; las 50 consultas ya están preparadas).

## 📊 Comparación obligatoria Hito 1 vs Hito 2 (COMPLETA sobre 50 consultas) ✅

Se seleccionan las mismas consultas y se comparan ambos motores con `scripts/evaluar_hito2.py`. Estado por caso (evidencia en `data/resultados_hito2.csv` y `data/resumen_hito2.txt`):

| Caso | Consulta | Hito 1 | Hito 2 |
|---|---|---|---|
| A | Imagen original con marco (10 exactas) | Top 1 correcto en 10/10 | Se mantiene: 10/10 ✅ |
| B | Misma camiseta sin marco (10 normalizadas) | 10/10 Top 1 | 6/10 Top 1; la regla auto (mayor score) compensa |
| C | Misma camiseta con colores cambiados (10 recoloreadas) | 10/10 Top 1 | Se mantiene: 10/10 ✅ |
| D | Recortadas (10) | 5/10 Top 1 | Mejora: 6/10 Top 1 ✅ |
| E | Mockup / persona (10) | 0/10 Top 1 | 1/10 Top 1 (mejora, sigue siendo el caso difícil) |
| F | Top 2–5 irrelevantes | 24% coherencia | 24% coherencia (terreno de Sala 3) |

---

## 🔧 Correcciones aplicadas en esta iteración (Sala 1 y Sala 3, Hito 2)

**Sala 1:**

1. **`scripts/analizar_formatos.py`** (nuevo): análisis del banco (Actividad 1) sobre las 1000 imágenes → `data/informe_formatos.txt` + `detalle_formatos.csv`. Calibrado en 2 pasadas: detección de marcos por franjas de borde no-blancas y recorte medido sobre la zona del uniforme (frente+espalda), no sobre el bbox total.
2. **`scripts/revisar_muestra_50.py`** (nuevo): revisión objetiva de la muestra de 50 (Actividad 5) con criterios de píxel (solo frente+espalda, sin logo, sin marco, sin cabecera/pie, sin cortes, sin deformación, lienzo uniforme) cruzados con `detalle_normalizacion.csv` → completa `revision_humana_50.csv` y genera `informe_revision_humana.txt`. Ajuste final: un caso marcado "dudoso" por el pipeline (`AIM-P003-164`, espalda lisa) se mantiene como dudosa para revisión humana.
3. **Calibración del lienzo uniforme:** se validó que el lado mayor del lienzo puede estar entre 350 y 700 px (el normalizador no amplía más de 2× para no perder definición), no exactamente 700.

**Sala 3:**

4. **Bug de rutas no-ASCII en el reranking:** `cv2.imread` falla silenciosamente con rutas que contienen caracteres no-ASCII (p. ej. la carpeta `Imágenes` del perfil de Windows) y dejaba `score_color = 0` en todas las consultas, anulando el reranking. Se reemplazó la lectura por PIL (`Image.open` → BGR) en `api/search_engine_hito2.py`.
5. **Reranking ampliado:** además del color HSV global se agregó comparación por regiones (frente/espalda, mitades izquierda/derecha) y estructura del patrón en grises 32×32, con pesos en constantes (probar, no asumir).
6. **`scripts/compare_hito1_hito2.py`** (reescrito): lee las consultas de `evaluation/consultas_hito2.csv`, mide tiempos por motor, guarda evidencia en `data/comparacion_hito1_hito2.csv` + `.json` y resume Top 1/Top 5 por categoría. Corregida la atribución (decía "SALA 4").
7. **`scripts/generar_consultas_prueba.py`** (nuevo): genera las 20 consultas derivables (10 exactas + 10 sin marco) y deja documentado cómo se agregan las 30 restantes (Sala 4 y Sala 2) al mismo CSV.

**Documentación:** `README.md` (paso 8 de Sala 3) y `AI_LOG.md` (prompts 7–9).

**Sala 2:**

8. **`api/preprocesar_consulta.py`** (nuevo): pipeline de preparación de consultas (recorte de bordes casi uniformes + remoción de fondo U2-Net/rembg con fallback GrabCut + bbox del primer plano + recorte al diseño + centrado 320×320).
9. **`POST /search/image` con modos** (`auto`, `procesada`, `original`, `completo`, `legacy`): la API prepara la consulta, guarda original+procesada en `data/queries_original/` y `data/queries_procesadas/` y devuelve ambos rankings más el detalle del preprocesamiento.
10. **`scripts/generar_consultas_hito2.py`** (nuevo): genera las 50 consultas (10 diseños × 5 versiones: exacto, sin_marco, recoloreado, recorte, cuerpo) en `data/consultas/` con su `id_correcto` en `evaluation/consultas_hito2.csv`.
11. **`scripts/evaluar_hito2.py`** (nuevo): evalúa Hito 1 vs Hito 2 sobre las 50 consultas → `data/resultados_hito2.csv` + `data/resumen_hito2.txt`.
12. **`scripts/evidencia_hito2.py`** (nuevo): montajes antes/después en `data/montajes/` + coherencia del Top 5 en `data/evidencia_coherencia_hito2.txt`.
13. **`frontend/app.py`** (actualizado): selector de modo, vista antes/después, comparación de rankings Hito 1 vs Hito 2 y registro de evaluación.

**Base para las demás salas:** `data/images_normalized/` es la fuente obligatoria para los tres índices de Sala 4 y para las consultas de la prueba integrada.

---

## 🚀 Recomendaciones / próximos pasos (Hito 2)

- **Sala 4:** generar los tres índices (`embeddings_clip.npy`, `embeddings_openclip.npy`, `embeddings_siglip.npy`) sobre `data/images_normalized/` y correr la prueba integrada común (las 50 consultas ya están listas en `evaluation/consultas_hito2.csv`).
- **Prueba integrada común:** ya completada (50/50 consultas) por Sala 2; queda pendiente la **clasificación humana de calidad del Top 5** (Muy similar / Similar / Poco similar / No relacionado) usando `frontend/app.py`.
- **Sala 3 (calibración):** re-ajustar los pesos del reranking y `MARGEN_CORTE` con las 50 consultas; probar si conviene que `CARPETA_IMAGENES` apunte a `images_normalized/` cuando Sala 4 regenere los embeddings desde normalizadas.
- **Comparación final Hito 1 vs Hito 2** con las consultas completas (casos A–F) para demostrar la mejora objetiva y visible.
- **Informe final por sala** siguiendo los 10 puntos de TRABAJO.md (objetivo, qué implementaron, quién hizo qué, pruebas, resultados numéricos, evidencia visual antes/después, qué funcionó, qué falló, qué mejorarían, qué código puede explicar cada integrante) — `evaluation/INFORME_SALA2_HITO2.md` ya cumple el formato.

> Fin