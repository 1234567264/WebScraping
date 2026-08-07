# WebScraping — RAG Visual (Hito 1)

Plataforma de búsqueda visual de camisetas deportivas basada en **embeddings CLIP**. El proyecto scrapea catálogos de *Designs Aimari*, consolida un dataset, convierte cada imagen en un vector, y expone una API que devuelve el **Top 5 de diseños visualmente más parecidos** a una imagen cargada. Todo se presenta en una interfaz Streamlit.

> **Hito 1 — Integración real:** una sola fuente de datos, un solo índice de embeddings, un solo motor de búsqueda y una sola interfaz que consume la API.

## Flujo del sistema

```text
[Scraper]  →  data/images/  (imágenes crudas)
                │
[consolidar.py] → data/products.csv + data/images_final/   (Sala 1)
                │
[generar_embeddings.py] → data/embeddings.npy + data/ids.npy   (Sala 4)
                │
[FastAPI api/main.py] → POST /search/image + GET /health   (Sala 3)
                │
[Streamlit frontend/app.py] → sube imagen, muestra Top 5 y registra evaluación   (Sala 2)
```

## Requisitos previos

- **Python 3.10+** (probado con 3.13).
- Conexión a internet (para descargar el modelo CLIP de Hugging Face y scrapear el sitio).

## Instalación

Desde la raíz del proyecto:

```bash
# 1) (Opcional) Entorno virtual
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# 2) Instalar dependencias
pip install -r requirements.txt
```

> La primera vez que se ejecuta, el modelo `openai/clip-vit-base-patch32` se descarga a `~/.cache/huggingface` (~350 MB).

## Ejecución paso a paso

El flujo completo es: **scrapear → consolidar → generar embeddings → levantar API → levantar interfaz**.

### 1. Scrapear el catálogo

```bash
python main.py --paginas 1-20 --imagenes 1000 --modo fresh
```

**Parámetros de `main.py`:**

| Parámetro | Valores | Descripción |
|---|---|---|
| `--paginas` | `1-20`, `1,2,3`, `all` | Páginas del catálogo a scrapear. Un rango se escribe `inicio-fin`. `all` scrapea todo. |
| `--imagenes` | número o `all` | Cantidad máxima de imágenes/productos a descargar. |
| `--modo` | `fresh` o `update` | `fresh` **borra `data/` y re-descarga todo desde cero**. `update` fusiona con los productos existentes (evita re-descargar). |

Este paso genera:
- `data/productos.json` — datos crudos del scraping.
- `data/images/` — las 1000 imágenes descargadas (nombres originales).
- `data/metadata.json` — metadatos de paginación.
- `data/productos.xlsx` — exportación Excel de respaldo.

> En Windows usa `--paginas "1-20"` entre comillas si tu shell interpreta el guion.

### 2. Consolidar el dataset (Sala 1)

```bash
python scripts/consolidar.py
```

Lee `data/productos.json` + `data/images/` y genera:
- `data/products.csv` — dataset canónico (`id, proveedor, pagina, imagen, nombre_original, url`).
- `data/images_final/` — imágenes renombradas con nomenclatura uniforme `AIM-PXXX-NNN.ext`.

Valida nomenclatura, duplicados, archivos existentes y apertura de imagen.

### 3. Validar el dataset (opcional pero recomendado)

```bash
python scripts/validate_dataset.py
python scripts/validate_dataset.py --benchmark   # mide tiempo en 1000 registros
```

Reporta: registros totales/válidos, IDs duplicados, nombres vacíos, URLs vacías/repetidas, extensiones inválidas, imágenes faltantes/dañadas y duplicados por hash MD5.

### 4. Generar los embeddings (Sala 4)

```bash
python scripts/generar_embeddings.py
```

Lee `products.csv` en orden, abre cada imagen de `images_final/`, genera su vector con **CLIP** (`openai/clip-vit-base-patch32`), lo normaliza con L2 y guarda:
- `data/embeddings.npy` — matriz `(N, 512)`.
- `data/ids.npy` — IDs alineados por posición con los embeddings.

> La correspondencia posición ↔ ID es obligatoria: si se altera el orden, el sistema devolvería nombres asociados a la imagen equivocada.

### 5. Levantar la API (Sala 3)

```bash
python -m uvicorn api.main:app --port 8000
```

Al iniciar carga el índice y el modelo CLIP una sola vez. Endpoints:

- `GET /health` — estado, cantidad de productos/embeddings y modelo.
- `POST /search/image` — recibe una imagen (multipart), genera su embedding y devuelve el **Top 5**: `{resultados: [{id, nombre, imagen, url, proveedor, score}...], tiempo_segundos}`.

Prueba rápida desde otra terminal:

```bash
curl -X POST -F "file=@data/images_final/AIM-P001-001.jpg" http://localhost:8000/search/image
```

### 6. Levantar la interfaz (Sala 2)

```bash
streamlit run frontend/app.py
```

Abre `http://localhost:8501` en el navegador:
1. En el sidebar verifica "API OK · 1000 productos · 1000 embeddings".
2. Sube una imagen (JPG/JPEG/PNG).
3. Revisa el Top 5 (imagen, ID, nombre, proveedor, URL, score).
4. Clasifica cada resultado (**Correcto / Útil, pero no duplicado / Incorrecto**) y guarda la evaluación → `data/evaluation.csv`.

## Evaluación de las 20 pruebas (Sala 2)

El plan está en `evaluation/test_plan.csv` (grupos A–D) y las imágenes de consulta en `evaluation/test_images/`.

```bash
# Métricas (Precisión Top 1 y Top 5, falsos positivos/negativos, tiempos)
python scripts/reporte_metricas.py
```

Genera `data/reporte_evaluacion.xlsx` y la tabla Consulta | Top 1 correcto | Top 5 útiles | Observación.

## Estructura del proyecto

```text
WebScraping/
├── api/                 # FastAPI + motor de búsqueda (Sala 3)
│   ├── main.py          #   endpoints /search/image y /health
│   └── search_engine.py #   carga índice y search_similar(top_k=5)
├── frontend/
│   └── app.py           # Interfaz Streamlit (Sala 2, cliente HTTP de la API)
├── data/
│   ├── images/          # Imágenes crudas del scraping (fuente, legacy)
│   ├── images_final/    # Imágenes con ID uniforme (entregable Sala 1)
│   ├── products.csv     # Dataset canónico
│   ├── embeddings.npy   # Vectores CLIP (Sala 4)
│   ├── ids.npy          # IDs alineados con embeddings
│   ├── evaluation.csv   # Resultado de las 20 pruebas (Sala 2)
│   └── tiempos.csv      # Tiempo por consulta
├── scripts/             # consolidar, validar, embeddings, evaluación, reportes
├── scraper/             # Engine de scraping (main.py lo usa)
├── utils/               # helpers, pagination, limits, update
├── storage/             # exportación a Excel
├── config/              # configuración del scraper
├── evaluation/          # test_plan.csv + test_images/ (20 pruebas)
├── requirements.txt     # Dependencias del proyecto
├── main.py              # Punto de entrada del scraper
├── TRABAJO.md           # Consigna oficial del proyecto
├── REPORTES.md          # Auditoría del estado vs TRABAJO.md
└── README.md            # Este documento
```

## Archivos generados clave

| Archivo | Contenido |
|---|---|
| `data/products.csv` | 1000 filas: `id, proveedor, pagina, imagen, nombre_original, url` |
| `data/embeddings.npy` | Matriz `(1000, 512)` float32, normalizada L2 |
| `data/ids.npy` | 1000 IDs en el mismo orden que los embeddings |
| `data/evaluation.csv` | Evaluación de las 20 consultas (5 filas por consulta) |
| `data/reporte_evaluacion.xlsx` | Resumen por consulta |

> **Nota sobre archivos legacy:** `data/index_embeddings.npy` y `data/index_metadata.json` son de `scripts/build_index.py` (fuera del flujo integrado). El flujo del Hito 1 usa únicamente `embeddings.npy` + `ids.npy`.

## Solución de problemas

- **`ModuleNotFoundError`**: instala las dependencias (`pip install -r requirements.txt`).
- **La API no responde en `/health`**: verifica que esté corriendo (`python -m uvicorn api.main:app --port 8000`). La interfaz muestra el error en el sidebar.
- **El validador reporta imágenes faltantes**: asegúrate de haber corrido `consolidar.py` (el validador apunta a `data/images_final/`).
- **Errores de codificación en consola (Windows)**: usa `set PYTHONIOENCODING=utf-8` antes de ejecutar, o activa la consola UTF-8.
- **Primera ejecución lenta**: la descarga del modelo CLIP y de las imágenes toma unos minutos.

## Próximos pasos

- Calibrar la clasificación humana de los grupos C y D para alcanzar el ≥70% de Top 5 útil del supervisor.
- Migrar el índice a **PostgreSQL + pgvector** (o FAISS) para persistencia, filtros y concurrencia al escalar.
- Fase siguiente del RAG: usar un LLM con los resultados recuperados para **proponer nombres y etiquetas**.