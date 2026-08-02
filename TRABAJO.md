**RAG**

**HACKATON FIN DE SEMANA**

No deben intentar **“preentrenar la IA”** este fin de semana. El término correcto sería:

> **Construir e indexar un prototipo de búsqueda visual con RAG.**

El modelo visual ya estará preentrenado. Los estudiantes usarán ese modelo para convertir las camisetas en vectores, buscar imágenes similares y recuperar sus nombres.

Tomo como fecha de entrega el **lunes 3 de agosto de 2026**. Actualmente es sábado 1 de agosto en Lima.

## **Objetivo único para el lunes**

El prototipo debe procesar **100 productos reales** y demostrar este flujo:

**Subir una camiseta sin nombre → obtener las cinco camisetas visualmente más parecidas → mostrar sus nombres, imágenes, URLs y porcentaje de similitud.**

No deben concentrarse todavía en generar el nombre comercial definitivo. Primero hay que comprobar que la recuperación visual funciona.

## **Distribución de las cuatro salas**

El ranking sirve únicamente para asignar el riesgo técnico. No significa que una sala sea incapaz.

| Sala | Responsabilidad | Entregable |
| ----- | ----- | ----- |
| **Sala 3** | Arquitectura, búsqueda vectorial e integración | Motor que recibe un vector y devuelve los cinco productos más similares |
| **Sala 1** | Datos, nombres y base de datos | Dataset limpio de 100 pares imagen-nombre y script de carga |
| **Sala 4** | Embeddings visuales con CLIP | Script que convierte imágenes en vectores y calcula similitud |
| **Sala 2** | Interfaz, pruebas y evaluación | Aplicación donde se carga una imagen y se visualizan los resultados |

### **Sala 3 — Núcleo RAG e integración**

Como fue la primera, debería encargarse del componente con mayor responsabilidad de integración.

Debe:

* Crear el repositorio principal.  
* Definir la estructura de carpetas.  
* Configurar PostgreSQL con pgvector o, como alternativa rápida, FAISS.  
* Crear la función `buscar_similares`.  
* Recibir un vector y devolver:  
  * ID.  
  * Nombre.  
  * Archivo.  
  * URL.  
  * Score de similitud.  
* Integrar el trabajo de las demás salas.

**Entregable:** una función probada que devuelva el top 5 de productos similares.

### **Sala 1 — Preparación e ingestión de datos**

Debe consolidar los resultados del scraping.

Si todos extrajeron la misma página, utilizarán la mejor extracción como base y las demás para verificar errores. Si extrajeron páginas distintas, consolidarán los registros.

Debe crear una estructura como:

id,proveedor,pagina,imagen,nombre\_original,url  
BUS-P001-001,Bustencio,1,BUS-P001-001.jpg,Nombre original,https://...

También debe comprobar:

* Que cada imagen tenga nombre.  
* Que cada nombre corresponda a la imagen correcta.  
* Que no existan duplicados.  
* Que los archivos puedan abrirse.  
* Que los nombres de archivos sigan una misma nomenclatura.

**Entregable:** carpeta con 100 imágenes, archivo CSV y script para insertarlas en la base de datos.

### **Sala 4 — Embeddings y similitud visual**

Esta sala debe investigar el componente que **no enseña Fazt 1**: embeddings de imágenes.

Debe utilizar un modelo preentrenado como:

* CLIP.  
* OpenCLIP.  
* SigLIP, solo si CLIP ya funciona.

Debe crear dos scripts:

generar\_embeddings.py  
buscar\_por\_imagen.py

El primero debe:

1. Abrir las 100 imágenes.  
2. Redimensionarlas correctamente.  
3. Pasarlas por CLIP.  
4. Obtener un vector por imagen.  
5. Guardar el vector asociado al ID del producto.

El segundo debe:

1. Recibir una imagen nueva.  
2. Generar su embedding.  
3. Compararlo con los 100 embeddings.  
4. Devolver las cinco imágenes más cercanas.

**Entregable:** búsqueda imagen contra imagen funcionando, inicialmente aunque sea desde consola o notebook.

### **Sala 2 — Interfaz y evaluación**

No es una tarea secundaria. Esta sala determinará si el sistema realmente funciona.

Debe construir una interfaz sencilla, preferentemente con Streamlit, que permita:

1. Cargar una imagen.  
2. Mostrar la imagen consultada.  
3. Mostrar las cinco imágenes similares.  
4. Mostrar nombre, URL y score.  
5. Registrar si el resultado fue correcto o incorrecto.

También debe preparar un conjunto de **20 imágenes de prueba** y una tabla:

| Consulta | Top 1 correcto | Top 5 útiles | Observación |
| ----- | ----- | ----- | ----- |
| Imagen 001 | Sí | 4 de 5 | Colores y líneas similares |

**Entregable:** interfaz funcional y reporte de evaluación sobre 20 consultas.

## **Qué deben estudiar todos del curso Fazt 1**

Todos deben comprender:

* Qué es RAG.  
* Qué es un embedding.  
* Qué es una base vectorial.  
* Diferencia entre base de datos normal y vectorial.  
* Búsqueda semántica.  
* Similitud entre vectores.  
* Indexación y recuperación.  
* Uso básico de pgvector.  
* Función para recuperar los registros más parecidos.

El curso de Fazt 1 presenta la relación entre productos, descripciones, embeddings y búsqueda semántica mediante pgvector. Esa arquitectura les sirve como base.

Pueden omitir por ahora:

* Text-to-SQL.  
* Autenticación.  
* Gestión de usuarios.  
* Seguridad SQL avanzada.  
* Despliegue final.  
* Diseño sofisticado del chat.  
* Caché y enrutamiento entre modelos.

El propio curso solamente menciona la interpretación de imágenes como una posible extensión, pero no la desarrolla. Por eso la Sala 4 tendrá que complementar el curso con CLIP.

## **Términos concretos que deben buscar**

La Sala 4 debe localizar tutoriales breves con estas búsquedas:

CLIP image embeddings Python Hugging Face  
OpenCLIP image similarity Python  
Image similarity search CLIP FAISS  
Cosine similarity image embeddings Python  
Store CLIP embeddings pgvector

La Sala 2:

Streamlit image upload Python  
Streamlit image similarity search  
Display image grid Streamlit

Las salas 1 y 3:

Python PostgreSQL pgvector tutorial  
Store embeddings in pgvector Python  
Cosine similarity pgvector  
Vector search top k PostgreSQL

## **Plan del fin de semana**

### **Sábado 1 de agosto**

**Actividad común**

Todos ven únicamente las partes relevantes de Fazt 1 y preparan una explicación breve de:

* Qué es un embedding.  
* Qué se guarda en pgvector.  
* Cómo se determina que dos elementos son similares.  
* Qué diferencia existe entre entrenar un modelo e indexar productos.

Después, cada sala construye su módulo utilizando inicialmente **20 productos**.

**Entrega del sábado:**

* Repositorio creado.  
* Estructura de datos definida.  
* 20 productos cargados.  
* Primer embedding generado.  
* Primer resultado de similitud.  
* Pull request de cada sala.

### **Domingo 2 de agosto**

* Subir de 20 a 100 productos.  
* Integrar los cuatro módulos.  
* Corregir imágenes y nombres mal relacionados.  
* Ejecutar las 20 consultas de evaluación.  
* Documentar instalación y ejecución.  
* Grabar una demostración corta.  
* Preparar explicación técnica individual.

**Entrega del domingo:**

/images  
/data/products.csv  
/scripts/ingest.py  
/scripts/generate\_embeddings.py  
/scripts/search.py  
/app.py  
README.md  
/evaluation/results.csv

### **Lunes 3 de agosto**

Cada sala debe realizar una demostración y responder preguntas.

La prueba principal será:

1. Se selecciona una camiseta que no esté dentro de las 100 imágenes.  
2. Se carga en la aplicación.  
3. El sistema devuelve cinco resultados.  
4. Se verifica si visualmente tienen relación.  
5. Se revisan nombres, URLs y scores.  
6. Un estudiante explica todo el recorrido de la información.

## **Reglas para el pair programming**

En cada sala:

* Un estudiante será **driver** y escribirá el código.  
* El otro será **navigator** y revisará lógica, documentación y errores.  
* Deben cambiar de rol cada 45 minutos.  
* Ningún módulo puede ser desarrollado únicamente por uno.  
* Ambos deben poder explicar todas las funciones.  
* Cada prompt utilizado con IA debe registrarse en un archivo `AI_LOG.md`.

No se acepta código generado por IA cuando ninguno pueda explicar:

* Qué recibe la función.  
* Qué devuelve.  
* Por qué utiliza esa librería.  
* Qué representa el vector.  
* Cómo calcula la similitud.  
* Qué ocurriría con 15.000 imágenes.

## **Criterios para saber si están preparados**

| Criterio | Peso |
| ----- | ----- |
| Búsqueda visual funcionando | 25% |
| Correspondencia correcta imagen-nombre | 20% |
| Integración entre módulos | 15% |
| Calidad y claridad del código | 10% |
| Resultados de las 20 pruebas | 15% |
| Explicación individual sin depender de IA | 15% |

El mínimo aceptable para el lunes sería:

* 100 de 100 imágenes procesadas.  
* Ninguna imagen sin nombre o ID.  
* Consulta visual funcionando.  
* Top 5 mostrado correctamente.  
* Al menos 70% de las pruebas con resultados razonablemente relacionados.  
* Proyecto ejecutable siguiendo el README.  
* Los ocho estudiantes capaces de explicar embeddings y similitud.

## **Lo que todavía no deben hacer**

Este fin de semana no deben intentar:

* Procesar las 15.000 imágenes.  
* Entrenar CLIP.  
* Ajustar un modelo con fine-tuning.  
* Crear el sistema definitivo de nomenclatura.  
* Generar categorías complejas.  
* Construir un RAG multimodal completo.  
* Optimizar para producción.

El avance correcto para el lunes es:

> **100 imágenes indexadas y una búsqueda visual que recupere correctamente sus nombres.**

Una vez demostrado eso, el siguiente paso será agregar la generación del nombre:

**Imagen nueva → productos similares → nombres recuperados → LLM propone un nombre nuevo.**

