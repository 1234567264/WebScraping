# REPORTES: Estado General del Proyecto RAG Visual

Este documento detalla el estado actual del prototipo de búsqueda visual con RAG, con vistas a la entrega del **lunes 3 de agosto de 2026**. Se estructura en función a los objetivos propuestos originalmente en `TRABAJO.md`.

---

## 📊  Resumen General
- **Total de productos procesados:** 100
- **Imágenes válidas en repositorio:** 100
- **Vector Base:** 100 (Reales) - Indexados con CLIP.
- **Salas terminadas:** Sala 1 (100%), Sala 3 (100%), Sala 4 (100%), Sala 2 (100%)

---

## 🟢 Sala 1: Datos, nombres y base de datos (Completado)

**Responsabilidad:** Generar el dataset limpio de 100 pares imagen-nombre y consolidar la información extraída de *Designs Aimari*.

### ¿Qué está HECHO?
* **Scraping Configurado:** El script en `webScraping-v2/main.py` capaz de paginar y descargar dinámicamente imágenes (actualmente usando las páginas 1 y 2 para obtener 100 productos reales).
* **Consolidación Lograda:** `consolidar.py` unifica todo el trabajo de manera aislada. 
* **Archivos Entregables Creados:**
  * `data/consolidado.csv`: Con 100 filas. 
  * Directorio `data/images_final/` y `data/images/`: Almacena 100 imágenes 100% verificadas.
* **Correlación de Nombres (IDs):** Estandarización correcta.

### ¿Qué FALTA?
* **Nada.** El trabajo está 100% terminado.

---

## 🟢 Sala 3: Arquitectura, búsqueda vectorial e integración (Completado)

**Responsabilidad:** Crear motor RAG, pipeline y función core de similitud recibiendo el vector de entrada y retornando 5 resultados.

### ¿Qué está HECHO?
* **Ingesta Estructurada (`scripts/ingest.py`):** Un puente directo que lee `consolidado.csv` y estandariza la base.
* **Metadata Automatizada:** `data/metadata.json` rastrea satisfactoriamente las configuraciones.
* **Integración Completa:** Ahora se soporta la carga del índice final (`index_metadata.json` y `index_embeddings.npy`) utilizado para realizar la inferencia.

### ¿Qué FALTA?
* **Nada.** El motor RAG ha sido integrado con éxito.

---

## 🟢 Sala 4: Embeddings y similitud visual (Completado)

**Responsabilidad:** Procesar con modelos de Hugging Face (CLIP) la base vectorial y ejecutar la búsqueda por similitud visual coseno.

### ¿Qué está HECHO?
* **Integración del Modelo de Visión/Lenguaje:** Implementación de `openai/clip-vit-base-patch32` (`clip-ViT-B-32`).
* **Generación de Embeddings (`generar_embeddings.py`):** Script optimizado para la conversión de características visuales a bases exportadas en `.npy`.
* **Motor de Búsqueda Visual (`buscar_por_imagen.py`):** Función de CLI testeada y verificada matemáticamente (Similitud Coseno).

### ¿Qué FALTA?
* **Nada.** 100% completado.

---

## 🟢 Sala 2: Interfaz, pruebas y evaluación (Completado)

**Responsabilidad:** Frontend, UX/UI, conexión visual con el usuario para probar y un módulo de evaluación humana comparativa.

### ¿Qué está HECHO?
* **Crear `app.py`:** Aplicación con Streamlit completada y funcional que incluye toda la interfaz visual y grillas divisorias.
* **Generación de índice (`build_index.py`):** Integra toda la creación del índice `.npy` unificando la base del Scraper.
* **Pipeline de Interfaz y Lógica (Drag & Drop):** Completado. Extrae el feature visual de la foto subida y arroja el top 5 consultando el array numpy con métricas numéricas visuales.
* **Evaluación en CSV:** Validado. Se logra exportar y agregar reportes humanos del ranking en `evaluacion.csv`.

### ¿Qué FALTA?
* **Nada.** Interfaz conectada, desplegada y operativa.

---

## 🚀 Guía de Ejecución Completa (End-to-End)

Todos los comandos deben ejecutarse desde la carpeta `webScraping-v2`.

```bash
cd webScraping-v2
```

### 1. Generar el dataset (Sala 1)
Descarga las imágenes y genera `productos.json`.

```bash
python main.py --paginas 1,2 --imagenes 100 --modo fresh
```

> Ejecutar nuevamente solo si se desea actualizar o regenerar el dataset.

---

### 2. Generar el índice vectorial (Sala 4 / Sala 2)

Convierte las imágenes en embeddings utilizando CLIP y genera los archivos:

- `data/index_embeddings.npy`
- `data/index_metadata.json`

```bash
python build_index.py
```

> Este paso solo es necesario la primera vez o cuando cambien las imágenes, `productos.json` o el modelo de embeddings.

---

### 3. Ejecutar la interfaz (Sala 2)

```bash
streamlit run app.py
```

Abrir:

```
http://localhost:8501
```

Subir una imagen y visualizar el Top 5 de resultados similares.

> Mientras el índice no cambie, basta con ejecutar únicamente este comando para volver a utilizar la aplicación.