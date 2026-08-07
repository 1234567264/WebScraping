# REPORTES: Estado General del Proyecto RAG Visual

**Fecha de Auditoría:** (Estado actual según evaluación real vs `TRABAJO.md`)

Este documento detalla el estado REAL del proyecto al contrastar la implementación actual en el repositorio contra los requerimientos fundamentales del **Hito 1** definidos en `TRABAJO.md`. 

## 📊 Resumen General del Proyecto
A pesar de que existen avances y scripts funcionales (1000 imágenes extraídas, pruebas locales de embeddings, endpoints construidos), **el proyecto se encuentra INCOMPLETO respecto a los criterios de integración definidos en el Hito 1 de TRABAJO.md.**

Existen 4 prototipos independientes en lugar de 1 sistema integrado. Las principales fallas radican en el contrato de datos (inexistencia de `products.csv`), almacenamiento separado de índices y la duplicación de responsabilidades entre salas.

---

## 🛑 Estado de Sala 1: Datos, nombres y base de datos (COMPLETO)
**Requisito de TRABAJO.md:** Entregar un único dataset confiable en `products.csv`, validar registros mediante un script de estadisticas y consolidar la información.

* **Estado Real:** COMPLETO.
* **Evidencias:**
  * Existe el script `webScraping-v2/consolidar.py` programado correctamente.
* **Observación breve:** Existen 1000 imágenes extraídas y un `productos.json`, pero la Sala 1 no ejecutó su pipeline final de consolidación. Las otras salas están intentando operar sobre los archivos preliminares y no sobre un dataset estándar aprobado.

---

## 🛑 Estado de Sala 3: Motor central e integración (PARCIALMENTE IMPLEMENTADO)
**Requisito de TRABAJO.md:** Servir un API central (`api/main.py`) con `/search/image` que reciba una query, la convierta a embedding y consulte a los únicos `embeddings.npy` e `ids.npy` entregados por la Sala 4.

* **Estado Real:** PARCIAL / INCOMPLETO.
* **Evidencias:**
  * Existe `api/main.py` y responde correctamente las queries consumiendo. 
  * *Falla de Integración:* El script `api/search_engine.py` utiliza su propio conector (`conector_sala3.py`) para leer archivos antiguos `productos.json` en lugar del obligatorio `products.csv`. Además consume `index_embeddings.npy` en lugar de unos indexados por la Sala 4 puramente.
* **Observación breve:** Arquitectura y endpoint de Flask/FastAPI están listos y son capaces de ejecutar. Funcionalmente la Sala 3 hizo su parte lógica, pero debido al atraso de Sala 1 y Sala 4, utiliza puentes provisionales. No cumple la regla del Hito 1.

---

## 🛑 Estado de Sala 4: Embeddings únicos (INCOMPLETO)
**Requisito de TRABAJO.md:** Script que lee de `products.csv`, y usando `openai/clip-vit-base-patch32` crea `embeddings.npy` e `ids.npy`. 

* **Estado Real:** INCOMPLETO.
* **Evidencias:**
  * Existe el archivo `webScraping-v2/generar_embeddings.py` usando HuggingFace `CLIPModel`.
  * *Falla de Integración:* El script busca imágenes escaneando libremente el directorio con `glob` en lugar de respetar el orden estricto de un CSV.
  * *Falla de Integración:* Genera un diccionario (clave=archivo, valor=vector) en `embeddings_productos.npy` contraviniendo la instrucción de generar dos Numpy Arrays independientes (`embeddings.npy` y `ids.npy`).
* **Observación breve:** Lógica base de IA implementada, pero arquitectura de integración ausente. No permite una búsqueda veloz y escalable si no separa los IDs.

---

## 🛑 Estado de Sala 2: Interfaz, pruebas y evaluación (INCOMPLETO)
**Requisito de TRABAJO.md:** App Streamlit que solamente sea cliente, consuma el API (POST `/search/image`) de la Sala 3, exponga los Top 5 y permita grabar un archivo `evaluaciones.csv` con métricas.

* **Estado Real:** INCOMPLETO.
* **Evidencias:**
  * Existe `webScraping-v2/app.py` que provee interfaz de carga y grillas de evaluacion.
  * *Falla de Integración (Grave):* Importa de nuevo `SentenceTransformer` localmente, calcula `cosine_similarity` en el mismo script y llama directamente al array `.npy`. No hace un HTTP POST a la Sala 3 (API).
* **Observación breve:** La interfaz no se comunica con el motor. Han construido un sistema "monolítico" alterno, sin respetar el modelo cliente-servidor exigido en el flujo de integración de Hito 1.

---

## 🚀 Próximos pasos y Recomendaciones Urgentes
Para cumplir verdaderamente con la integración descrita en TRABAJO.md:
1. **Paso 1:** Ejecutar `consolidar.py` para generar formalmente el **products.csv** y pasarlo a las demás salas. (Sala 1)
2. **Paso 2:** Corregir `generar_embeddings.py` para iterar el CSV línea a línea y exportar el array 2D normalizado y un vector Numpy ID separado. (Sala 4)
3. **Paso 3:** Modificar `search_engine.py` eliminando puentes y forzar que lea los dos entregables de paso 1 y 2. Desplegar API. (Sala 3)
4. **Paso 4:** Remover importaciones de Transformers y similitud de `app.py`, y realizar request vía framework tipo HTTP JSON-Request al endpoint expuesto de FastAPI. (Sala 2)