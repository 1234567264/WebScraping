# WebScraping - RAG Visual Hito 1

## Descripción del proyecto
Plataforma especializada en extraer, organizar y comparar miles de diseños de camisetas deportivas usando inteligencia artificial. Este proyecto constituye el **Hito 1**, cuyo objetivo fundamental es lograr la **Integración Real** de un motor inteligente que organice, compare y conecte un dataset extraído de *Designs Aimari* mediante la generación de vectores con CLIP.

## Objetivo
Procesar un mínimo de 100 productos reales (actualmente 1000) y demostrar un flujo automatizado de recuperación visual: 
**Subir una camiseta → Generar embedding → Obtener los 5 diseños más similares con nombres, URLs y % de precisión.**

## Arquitectura / estructura del proyecto
El sistema está diseñado para funcionar en un ecosistema cliente-servidor para el Hito 1, dividiendo la extracción, vectorización, servidor motor y frontend (interfaz).

```text
Usuario carga imagen
       │
       ▼
[Frontend: Streamlit]  ── (POST Imagen) ──▶  [Backend: FastAPI]
                                                  │
                                                  ▼
                                           Generar Embedding (CLIP)
                                                  │
                                                  ▼
                                      Consultar en Arrays (ids.npy/embeddings.npy)
                                                  │
                                                  ▼
                                     Top 5 Resultados en JSON 
```

## Salas y responsabilidades
- **Sala 1:** Datos, nombres y base de datos (Ingestión web scraping y estandarización CSV).
- **Sala 4:** Embeddings visuales (Procesamiento Batch de imágenes mediante CLIP para indexación matricial Numpy).
- **Sala 3:** Arquitectura e Integración (Motor RAG con búsqueda por similitud de Coseno + Endpoints RESTful).
- **Sala 2:** Interfaz y evaluación (Cliente VDU de Streamlit, conexión de API RESTful y métricas operativas).

## Estado actual de cada sala
El repositorio actual presenta resultados funcionales de forma independiente pero **INCOMPLETOS** en el Hito 1 de integración conectada (ninguna sala consume a la otra según las reglas oficiales):
- **Sala 1:** INCOMPLETO. Faltan los entregables finales (`products.csv`, carpeta `/images_final`) al no haberse corrido `consolidar.py`. No cuenta con métricas de dataset validado.
- **Sala 3:** PARCIALMENTE IMPLEMENTADO. Funciona correctamente mediante endpoints POST `/search/image` pero utiliza archivos temporales/propios de json.
- **Sala 4:** INCOMPLETO. Código de CLIP funcional, pero graba un array erróneo (Diccionario en `.npy`) saltándose el formato estricto Hito 1 (`embeddings.npy` e `ids.npy`).
- **Sala 2:** INCOMPLETO. Funciona la UI Streamlit pero comete un error crítico de arquitectura: duplica la librería de Transformers e indexa directamente en vez de ser cliente API de la Sala 3.

## Tecnologías utilizadas
* **Lenguaje:** Python 3.x
* **Backend:** FastAPI, Uvicorn, Sentence-Transformers, PyTorch.
* **Procesamiento de visión:** CLIP (`openai/clip-vit-base-patch32` / `clip-ViT-B-32`), Pillow, NumPy, Pandas.
* **Frontend:** Streamlit.

## Instalación
Desde la raíz o carpeta `webScraping-v2`, con un entorno virtual activado (Ej: `python -m venv venv`):

```bash
pip install -r requirements.txt
pip install fastapi uvicorn python-multipart sentence-transformers pillow pandas numpy streamlit
```

## Ejecución
> **Nota:** Dado el estado actual, el proyecto solo se ejecuta usando puentes locales no unificados debido a las fallas entre alas. Para ejecutar la UI aislada existente:

1. **Generar los datos:**
   ```bash
   cd webScraping-v2
   python main.py --paginas 1,2 --imagenes 100 --modo fresh
   ```
2. **Generar el vector índice:**
   ```bash
   python build_index.py
   ```
3. **Desplegar Servidor Backend:**
   ```bash
   python -m uvicorn api.main:app --reload --port 8000
   ```
4. **Desplegar Frontend:**
   ```bash
   streamlit run app.py
   ```
*(Nota: la ejecución anterior ignora intencionalmente el API corriendo.)*

## Estructura de carpetas importante
```
WebScraping/
├── webScraping-v2/
│   ├── api/                 # Endpoints FastAPI y motor algorítmico RAG
│   ├── data/                # Bases de datos, JSON pre-scraped, carpetas de imágenes y vectores
│   ├── scraper/             # Engine web-extraction inicial
│   ├── utils/               # Validaciones, loggers y parsers
│   ├── app.py               # Frontend: Interfaz Streamlit de testeo
│   ├── main.py              # Script inicial Scraper
│   ├── consolidar.py        # Pipeline unificación de datos
│   └── generar_embeddings.py# Script principal CLIP Batch Processing
├── REPORTES.md              # Dictamen de integración técnica del Hito 1
└── README.md                # Este documento central
```

## Datos y archivos generados
* `data/productos.json`: Dataset bruto del scraper.
* `data/images/`: Biblioteca visual (imágenes JPG).
* `data/index_embeddings.npy` / `embeddings_productos.npy`: Matrices flotantes 1D/2D del encoder neuronal.

## Flujo general del proyecto
1. Extracción de Metadatos y Catálogo.
2. Limpieza y Consolidación (Asignación ID Uniforme).
3. Transformación Visual (Image RGB a 512D Float Tensor).
4. Persistencia Serial (Almacenamiento `.npy`).
5. Búsqueda L2 Vectorial (Producto punto en FastApi).
6. Representación Visual Frontend.

## Próximos pasos
El **Siguiente Nivel** debe consistir 100% en arreglar los puentes del Hito 1 (Enlazar formalmente las cuatro alas usando endpoints en vez de rutinas unilineales):
- Correr `consolidar.py` real (Sala 1) y generar `products.csv`.
- Reescribir Script Sala 4 para producir `embeddings.npy` (matriz) y `ids.npy`.
- Forzar Sala 3 a leer variables exactas sin correctores intermedios.
- Re-codificar el botón Upload de Streamlit de Sala 2 bajo `requests.post()` al API de FastAPI.