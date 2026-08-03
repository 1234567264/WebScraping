# Ejecución del proyecto

Todos los comandos deben ejecutarse desde la carpeta `webScraping-v2`.

```bash
cd webScraping-v2
```

---

## 1. Ejecutar el Web Scraper

Extrae los productos desde Designs Aimari, descarga las imágenes y genera los archivos de datos.

Ejemplo:

```bash
python main.py --paginas 1,2 --imagenes 100 --modo fresh
```

Este proceso genera:

- `data/productos.json`
- `data/productos.xlsx`
- `data/metadata.json`
- `data/images/`

> Si agregas nuevas páginas, cambias el número de imágenes o actualizas el dataset, vuelve a ejecutar este paso.

---

## 2. Generar el índice vectorial (CLIP)

Una vez descargadas las imágenes, genera los embeddings utilizados por el buscador visual.

```bash
python build_index.py
```

Este proceso:

- Carga el modelo CLIP (`clip-ViT-B-32`).
- Procesa todas las imágenes de `data/images/`.
- Genera:
  - `data/index_embeddings.npy`
  - `data/index_metadata.json`

> Solo es necesario ejecutarlo cuando cambian las imágenes, `productos.json` o el modelo de embeddings.

---

## 3. Ejecutar la aplicación web

Con el índice generado, inicia la interfaz de búsqueda visual.

```bash
streamlit run app.py
```

Luego abre:

```
http://localhost:8501
```

La aplicación permite:

- Subir una imagen.
- Obtener los 5 diseños más similares.
- Visualizar nombre, URL y puntaje de similitud.
- Evaluar manualmente los resultados.
- Guardar la evaluación en `data/evaluacion.csv`.

> Mientras el índice no cambie, solo necesitas ejecutar `streamlit run app.py`.

---

# Flujo completo

```text
main.py
    │
    ▼
Scraping de productos
    │
    ▼
productos.json
images/
metadata.json
    │
    ▼
build_index.py
    │
    ▼
index_embeddings.npy
index_metadata.json
    │
    ▼
app.py (Streamlit)
    │
    ▼
Búsqueda visual (Top 5)
```