# REPORTES: Estado General del Proyecto RAG Visual

Este documento detalla el estado actual del prototipo de búsqueda visual con RAG, con vistas a la entrega del **lunes 3 de agosto de 2026**. Se estructura en función a los objetivos propuestos originalmentes en `TRABAJO.md`.

---

## 📊  Resumen General
- **Total de productos procesados:** 100
- **Imágenes válidas en repositorio:** 100
- **Vector Base (Demo):** 20 (falsa) - A la espera de embeddings 
- **Salas terminadas / en progreso:** Sala 1 (100%), Sala 3 (95%), Sala 4 (100%), Sala 2 (0%)

---

## 🟢 Sala 1: Datos, nombres y base de datos (Completado)

**Responsabilidad:** Generar el dataset limpio de 100 pares imagen-nombre y consolidar la información extraída de *Designs Aimari*.

### ¿Qué está HECHO?
* **Scraping Configurado:** El script en `webScraping-v2/main.py` es completamente capaz de paginar y descargar dinámicamente imágenes (actualmente usando las páginas 1 y 2 para obtener 100 productos reales).
* **Consolidación Lograda:** `consolidar.py` unifica todo el trabajo de manera aislada. 
* **Archivos Entregables Creados:**
  * `data/consolidado.csv`: Con 100 filas conteniendo `id, proveedor, pagina, imagen, nombre_original, url`. 
  * Directorio `data/images_final/`: Almacena 100 imágenes 100% verificadas para que no estén corruptas y puedan prepararse para los modelos de IA.
* **Correlación de Nombres (IDs):** Todas las imágenes y CSV han sido estandarizados correctamente reflejando las páginas solicitadas (por ej: `AIM-P001-xxx` y `AIM-P002-xxx`). Nomenclatura, duplicados y validez están resueltos.

### ¿Qué FALTA?
* **Nada.** El trabajo estructural requerido para consolidar la información base mediante scraping está **100% terminado** para la fase 1.

---

## 🟢 Sala 3: Arquitectura, búsqueda vectorial e integración (Casi Completado)

**Responsabilidad:** Crear motor RAG, pipeline y función core de similitud recibiendo el vector de entrada y retornando 5 resultados usando FAISS / Pgvector y similitud Coseno.

### ¿Qué está HECHO?
* **Ingesta Estructurada (`scripts/ingest.py`):** Un puente directo que lee `consolidado.csv`, estandariza, crea metadata unificada (`metadata.json`) y deja todos los metadatos requeridos para las búsquedas listos; eliminando dependencias sueltas.
* **Metadata Automatizada:** `data/metadata.json` rastrea satisfactoriamente las configuraciones del proveedor y el contador (total 100) para evitar colisiones.
* **Algoritmo Base de Similitud Vectorial (`scripts/search.py`):** La función `BuscarSimilares(vector)` carga un query individual, calcula **similitud coseno** con `numpy.dot` y renderiza top 5 diccionarios limpios (`id, nombre, imagen, url, score`).
* **Protección Anti-Bloqueos (Demo):** Si la Sala 4 tarda, la sala 3 tiene el flag `--demo` para inyectar vectores de testeo y poder seguir interactuando con Sala 2.

### ¿Qué FALTA?
* Recibir la matriz final generada por la **Sala 4 (Modelos)**, la cual llamará al helper global `GuardarEmbeddings()` para inyectar la matriz 100xVector a producción real. Tras recibirla, cambiar el flag a `embeddings_disponibles: true`. 
* La migración de base plana (.npy) a pgvector / FAISS como indicaba TRABAJO.md (aunque en numpy el prototipo está totalmente funcional para el domingo).

---

## 🟢 Sala 4: Embeddings y similitud visual (Completado)

**Responsabilidad:** Procesar con modelos de Hugging Face (CLIP) cada imagen limpia extraída por el Scraper de la Sala 1, generar la base vectorial y ejecutar la búsqueda por similitud visual coseno.

### ¿Qué está HECHO?
* **Integración del Modelo de Visión/Lenguaje:** Implementación de `openai/clip-vit-base-patch32` mediante las librerías `transformers`, `torch` y `Pillow`.
* **Generación de Embeddings (`generar_embeddings.py`):**
  * Script optimizado para iterar y procesar la totalidad de imágenes en `data/images_final/`.
  * Conversión de características visuales a tensores de 512 dimensiones con **normalización L2** aplicada para garantizar la precisión en cálculos vectoriales.
  * Exportación e inyección automatizada de la matriz final a la ruta estandarizada `data/embeddings_productos.npy`.
* **Motor de Búsqueda Visual (`buscar_por_imagen.py`):**
  * Función que recibe cualquier imagen de prueba como argumento desde la terminal.
  * Extrae su embedding en tiempo real mediante CLIP y calcula la **similitud coseno** frente a los 100 productos de la base.
  * Retorna e imprime de forma limpia el **Top 5** de productos más parecidos junto con sus porcentajes de coincidencia visual.
* **Documentación y Verificación:**
  * Creación del manual operativo completo `GUIA_SALA4.txt` detallando arquitectura, requisitos y orden de ejecución.
  * Verificación directa vía CLI (`python -c "..."`) que confirma la integridad de las 100 imágenes procesadas y la validez binaria de los vectores de 512 dimensiones.

### ¿Qué FALTA?
* **Nada.** El módulo de extracción visual de características y búsqueda por similitud coseno está **100% completado** y probado con un 100.00% de precisión en autocomparación y ~75% en coincidencias de patrón/diseño.

---

## 🔴 Sala 2: Interfaz, pruebas y evaluación (Por Iniciar)

**Responsabilidad:** Frontend, UX/UI, conexión visual con el usuario para probar y un módulo de evaluación humana comparativa.

### ¿Qué está HECHO?
* Nada. No existe aún `app.py` ni resultados de tabulación.

### ¿Qué FALTA?
* **Crear `app.py`:** Una aplicación rápida con Streamlit (`streamlit run app.py`) en la raíz.
* **Pipeline de Interfaz (Drag & Drop):** Un componente que reciba la imagen que se busca examinar.
* **Integración Total:**
  1. Mandar imagen a la función de Sala 4 para sacar el Embedding.
  2. Pasar Embedding a `BuscarSimilares()` en Sala 3.
  3. Desplegar una grilla HTML/Streamlit de 5 columnas mostrando de manera comparativa la imagen real consultada vs los Top 5 aciertos (`score, imagen, id y nombre`).
* **Tabla de QA (`evaluation/results.csv`):** Con al menos 20 iteraciones (subir X camisa → resultado top 1 fue correcto?). Deberá documentarse con comentarios (Ej: "La camisa de river plate reconoció los listones rojos").
