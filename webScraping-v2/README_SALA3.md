# Sala 3 — Arquitectura, Búsqueda Vectorial e Integración (RAG Engine)

Este módulo contiene la implementación del **Núcleo de Recuperación Visual y API Central** desarrollado por la **Sala 3** para el Hito 1 del Hackathon. 

Permite procesar vectores e imágenes de camisetas deportivas, calcular la similitud coseno mediante embeddings CLIP y exponer endpoints RESTful para la integración con la interfaz de usuario (Sala 2).

---

##  Lo que agregamos e implementamos

1. **Conector de Datos Real (`conector_sala3.py`)**:
   - Se conectó el motor directamente con los **1,000 productos reales** entregados por la Sala 1 (`data/productos.json`).
   - Mapea y estandariza los campos obligatorios: `id`, `nombre_original`, `imagen`, `url`, `proveedor` ("Designs Aimari").
   - Es totalmente independiente de los archivos de matriz `.npy`.

2. **Motor de Búsqueda Vectorial (`api/search_engine.py`)**:
   - **Normalización L2**: Normaliza la matriz de embeddings al cargar para garantizar un cálculo preciso de Similitud Coseno ($V_{norm} \cdot Q_{norm}$).
   - **Detección Estricta de Desfases**: Compara la cantidad de productos en `productos.json` contra la cantidad de embeddings cargados. Si detecta discrepancia (p. ej. 1,000 productos vs 20 embeddings), responde con una alerta clara en `/health` y previene inconsistencias lanzando un `ValueError`.
   - **Contrato de Respuesta Top 5**: Devuelve la lista exacta con los 5 productos más parecidos y sus scores normalizados.

3. **Servidor API FastAPI (`api/main.py`)**:
   - **Carga de Modelo CLIP**: Inicializa el modelo `openai/clip-vit-base-patch32` en el arranque.
   - **Endpoint `GET /health`**: Reporta el número de productos y embeddings cargados, estado de salud del servicio y detección de desfases.
   - **Endpoint `POST /search/image`**: Recibe una imagen (JPG/PNG), genera su embedding con CLIP y devuelve el Top 5 formateado en JSON.
   - **CORS Habilitado**: Configurado para consumo directo desde Streamlit (Sala 2) o clientes web externos.

4. **Módulo Unificado Todo-en-Uno (`sala3_app.py`)**:
   - Script consolidado que integra el conector, el motor vectorial y el servidor FastAPI en un solo archivo fácil de distribuir y ejecutar.

---

##  Estructura de Archivos Entregada

```
webScraping-v2/
├── conector_sala3.py        # Lee y mapea productos.json de Sala 1
├── sala3_app.py             # Versión unificada todo-en-uno de Sala 3
├── api/
│   ├── __init__.py
│   ├── search_engine.py    # Algoritmo de búsqueda vectorial y Similitud Coseno
│   └── main.py             # Servidor FastAPI (endpoints /health y /search/image)
├── data/
│   ├── productos.json       # Dataset oficial de 1,000 productos (Sala 1)
│   └── index_embeddings.npy # Matriz de vectores de 512 dimensiones
└── README_SALA3.md          # Documentación del entregable de Sala 3
```

---

##  Requisitos de Instalación

Asegúrate de contar con las siguientes librerías de Python instaladas:

```bash
pip install fastapi uvicorn python-multipart sentence-transformers pillow pandas numpy
```

---

##  Instrucciones de Ejecución

### Opción 1: Ejecutar la API desde el módulo `api/` (Recomendado)

Desde la carpeta `webScraping-v2`:

```bash
cd webScraping-v2
python -m uvicorn api.main:app --reload --port 8000
```

### Opción 2: Ejecutar la versión todo-en-uno (`sala3_app.py`)

```bash
cd webScraping-v2
python sala3_app.py
```

---

##  Documentación de Endpoints

### 1. Verification Check: `GET /health`
Verifica el estado del servidor y el balance entre productos indexados y embeddings.

**Respuesta de ejemplo (Sin desfase):**
```json
{
  "status": "ok",
  "products": 1000,
  "embeddings": 1000,
  "model": "openai/clip-vit-base-patch32",
  "desfase_detectado": false
}
```

### 2. Búsqueda Visual: `POST /search/image`
Envía una imagen mediante `multipart/form-data` en el parámetro `file`.

**Respuesta de ejemplo (Top 5):**
```json
[
  {
    "id": "AIM-P001-0001",
    "nombre": "Guadalcacin Blue",
    "imagen": "AIM-P001-0001.jpg",
    "url": "https://media.designsaimari.com/products/image.jpg",
    "proveedor": "Designs Aimari",
    "score": 0.8245
  },
  {
    "id": "AIM-P001-0002",
    "nombre": "Argentina Drexx",
    "imagen": "AIM-P001-0002.jpg",
    "url": "https://media.designsaimari.com/products/image2.jpg",
    "proveedor": "Designs Aimari",
    "score": 0.7412
  }
]
```

---

##  Pruebas Interactivas (Swagger UI)

Con el servidor encendido, ingresa desde tu navegador a:
👉 **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**
