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

# **VISION**

Estamos construyendo una **plataforma de e-commerce** especializada en la venta de plantillas para camisetas deportivas, capaz de organizar y publicar miles de diseños, permitir búsquedas por imagen, palabras, categorías, estilos, colores y deportes, detectar diseños repetidos o similares, y usar inteligencia artificial para proponer nombres, etiquetas y metadatos; para lograrlo, **primero estamos desarrollando el motor inteligente** que organizará, comparará y conectará toda la biblioteca visual,   
y en el **Hito 1** integraremos en un solo sistema las partes que hoy están separadas para que una imagen pueda ingresar, compararse contra la biblioteca y devolver resultados reales con nombre, imagen, URL y nivel de similitud 

## **1\. Qué hicieron realmente**

Ellos construyeron esto:

**Imagen → embedding → comparación con otros embeddings → Top 5 de imágenes parecidas**

Eso es un **motor de búsqueda visual por similitud**.

Y sí: técnicamente **ya hicieron embeddings**, aunque algunos no supieran explicar el término. El código de las salas 2 y 4 convirtió imágenes en **vectores** usando CLIP, y luego comparó esos vectores. Eso es exactamente trabajar con embeddings.

## **2\. Entonces, ¿dónde está el RAG?**

Un RAG completo tendría este flujo:

**Imagen nueva → búsqueda de diseños similares → recuperación de nombres y datos → modelo de lenguaje genera una respuesta nueva**

Por ejemplo:

1. **Se carga una camiseta sin nombre.**  
2. **El sistema encuentra cinco camisetas parecidas.**  
3. **Recupera sus nombres, estilos y categorías.**  
4. Esos datos se entregan a un modelo como GPT o Claude.  
5. El modelo propone un nuevo nombre y etiquetas.

Ellos llegaron hasta el paso 3 parcialmente:

* Buscaron imágenes similares.  
* Recuperaron nombres, URL e ID.

Pero no hicieron todavía la parte final de **generación** con un modelo de lenguaje.

Por eso, lo más correcto es decir:

> Construyeron la parte de recuperación visual que luego formará parte del RAG.

No fue un error total llamarlo RAG, porque estaban construyendo su base. Pero aún no era un RAG completo.

**ENTONCES**  
En la actividad anterior construyeron embeddings y un sistema de recuperación visual. Esa es la primera parte de un RAG multimodal. Todavía falta la parte de generación, donde un modelo utilizará los resultados recuperados para proponer nombres, categorías y etiquetas. 

**Sobre el informe que presentaron y siguiente informe** 

He revisado los cuatro informes. El avance es bueno, pero hay una precisión fundamental:

> **Todavía no construyeron un RAG. Construyeron un prototipo de búsqueda visual por embeddings.**

Actualmente ya tienen:

* Extracción y preparación de datos.  
* Embeddings visuales con CLIP.  
* Búsqueda de las cinco imágenes más parecidas.  
* Una interfaz básica en Streamlit.  
* Relación de resultados con nombre, URL e ID.

Todavía falta:

* Unificar los cuatro módulos.  
* Procesar lotes masivos.  
* Base de datos vectorial permanente.  
* API central.  
* Búsqueda mediante texto.  
* Generación de nombres con RAG.  
* Integración con WordPress.

# **Evaluación de los informes**

## **Sala 1 — Datos e ingestión**

**Evaluación: 82/100**

Hicieron correctamente el scraping, la consolidación de 100 pares imagen-nombre, la nomenclatura, el CSV y la carga de registros. También explicaron bastante bien el funcionamiento de los scripts.

### **Lo positivo**

* Dataset organizado.  
* IDs uniformes.  
* CSV con columnas adecuadas.  
* Validación de archivos.  
* Control de duplicados por ID.  
* Explicación individual bastante completa.

### **Lo que deben corregir**

Existe una contradicción importante:

* En la tabla indican PostgreSQL/pgvector.  
* En realidad están usando `sqlite3` y un archivo `productos.db`.

Por tanto, deben escribir claramente:

> Base de datos actual: SQLite.  
> Migración futura: PostgreSQL con pgvector.

Tampoco demostraron realmente que el sistema pueda procesar 1.000 registros. Explicaron que el bucle podría hacerlo, pero no realizaron la prueba ni midieron tiempo.

La validación de que el nombre corresponde a la imagen parece ser estructural: misma fila, mismo ID y misma ruta. No queda demostrado que hayan revisado visualmente que el nombre sea realmente el correcto.

### **Para el siguiente informe**

Deben incluir:

* Tiempo real procesando 1.000 registros.  
* Cantidad de nombres vacíos.  
* Cantidad de URLs repetidas.  
* Cantidad de archivos duplicados por hash.  
* Cantidad de imágenes dañadas.  
* Evidencia de validación visual de una muestra.

---

## **Sala 2 — Interfaz y evaluación**

**Evaluación: 68/100**

Construyeron una interfaz funcional para cargar una imagen, mostrar el Top 5 y registrar evaluaciones. Eso es valioso.

### **Lo positivo**

* Interfaz Streamlit funcional.  
* Carga de imágenes.  
* Resultados con nombre, URL y score.  
* Registro de evaluación en CSV.  
* Prueba con una imagen fuera del dominio.

### **Lo que falta**

La tarea pedía 20 pruebas y solamente completaron 2\.

No se puede concluir todavía:

* Que el Top 1 tenga 100% de precisión.  
* Que un score menor a 0,50 deba descartarse.  
* Que el sistema detecte correctamente imágenes nuevas.  
* Que encuentre variantes de color o composición.

Además, Sala 2 volvió a generar su propio índice con CLIP. Eso duplica el trabajo de Sala 4\. La interfaz debería consumir el motor único de Sala 3, no tener una implementación paralela.

El informe solamente presenta a Mathias. Debe aclararse qué ocurrió con el segundo integrante de la sala.

### **Para el siguiente informe**

Deben completar:

* 20 pruebas reales.  
* 5 duplicados exactos.  
* 5 variantes.  
* 5 imágenes nuevas.  
* 5 imágenes que no sean camisetas.  
* Precisión Top 1\.  
* Precisión Top 5\.  
* Falsos positivos.  
* Falsos negativos.  
* Tiempo promedio por consulta.

---

## **Sala 3 — Arquitectura e integración**

**Evaluación: 74/100**

Construyeron el módulo central de ingestión y búsqueda y detectaron un error real de normalización. Esa detección es un aprendizaje importante.

### **Lo positivo**

* Función central `BuscarSimilares`.  
* Resultado con ID, nombre, imagen, URL y score.  
* Corrección del error de normalización.  
* Identificación de problemas de integración.  
* Reconocimiento claro de que todavía no existe API ni base vectorial.

### **Lo que falta**

Ellos mismos reconocen que:

* El buscador todavía utiliza un archivo con 20 vectores.  
* Los 100 embeddings finales de Sala 4 están en otra ruta.  
* La integración definitiva no está terminada.  
* No midieron el tiempo de procesamiento.  
* No existe manejo robusto de errores.  
* No existe API.  
* No existe PostgreSQL ni pgvector.

Por tanto, Sala 3 construyó el núcleo, pero todavía no puede considerarse una integración completa.

También hay una diferencia importante entre las pruebas:

* Una parte muestra un resultado principal de 67%.  
* Otra sección afirma resultados de 99% agregando ruido artificial al vector.

La prueba con ruido sobre un embedding ya existente sirve para verificar matemáticamente la función, pero no sustituye una prueba con una imagen externa real.

### **Para el siguiente informe**

Deben incluir:

* Los 100 o 1.000 embeddings conectados realmente.  
* Una única ruta de almacenamiento.  
* Pruebas con imágenes externas.  
* Tiempo de consulta.  
* Respuesta en JSON.  
* Manejo de archivo faltante.  
* Manejo de vector con dimensiones incorrectas.  
* Endpoint de API probado.

---

## **Sala 4 — Embeddings y similitud visual**

**Evaluación: 88/100**

Es el informe técnicamente más completo. Generaron embeddings CLIP de 512 dimensiones, normalización L2, almacenamiento NumPy y búsqueda Top 5\.

### **Lo positivo**

* Modelo identificado correctamente.  
* Flujo técnico bien explicado.  
* Embeddings reales.  
* Medición de tiempo.  
* Normalización correcta.  
* Búsqueda por similitud coseno.  
* Buen registro del uso de IA.  
* División clara del trabajo.

### **Lo que deben corregir**

No deben llamar al score:

> porcentaje de coincidencia o confianza.

Un score de `0,75` no significa necesariamente que exista un 75% de probabilidad de que sea el mismo diseño. Es una medida de cercanía dentro del modelo.

Tampoco es correcto establecer todavía:

* 100% \= duplicado.  
* 70% a 85% \= diseño parecido.

Eso solo se podrá definir después de probar cientos de casos etiquetados.

También afirmaron que 15.000 imágenes obligarían a usar FAISS o pgvector. No necesariamente. Una matriz de 15.000 × 512 todavía puede consultarse rápidamente con NumPy. La base vectorial será necesaria principalmente por persistencia, filtros, integración, concurrencia y crecimiento, no porque 15.000 sea una cantidad imposible para fuerza bruta.

### **Para el siguiente informe**

Deben incluir:

* Procesamiento por lotes.  
* Pruebas con imágenes fuera de la biblioteca.  
* Mismo diseño recomprimido.  
* Mismo diseño con otro color.  
* Mismo diseño con texto o escudo diferente.  
* Comparación CLIP contra SigLIP u OpenCLIP.  
* Separación entre duplicado exacto y similitud visual.  
* Tiempo real para 1.000 imágenes.

# **Diagnóstico general**

Los cuatro equipos construyeron componentes útiles, pero hay duplicación:

* Sala 2 genera embeddings.  
* Sala 4 genera embeddings.  
* Sala 3 tiene su propia búsqueda.  
* Sala 2 tiene otra búsqueda.  
* Existen varios nombres y rutas para los mismos archivos.

El próximo nivel no debe agregar más funciones todavía.

> **El siguiente nivel debe ser convertir los cuatro prototipos en un único sistema.**

# **Ruta de hitos**

## **Hito 1 — Integración real**

**Duración recomendada: 1 a 2 días.**

Resultado:

* Un solo dataset.  
* Un solo modelo CLIP.  
* Un solo archivo o tabla de embeddings.  
* Una sola función de búsqueda.  
* Una sola interfaz.  
* Sin rutas duplicadas.  
* Sin archivos de prueba antiguos.

Flujo final:

Imagen → CLIP → motor de búsqueda → Top 5 → interfaz.

### **Distribución**

**Sala 1:** entrega `products.csv` definitivo y validado.

**Sala 4:** genera `embeddings.npy` y `ids.npy`.

**Sala 3:** construye el motor único y una API FastAPI.

**Sala 2:** elimina su búsqueda propia y consume la API.

### **Entregable**

Un endpoint:

`POST /search/image`

Debe devolver:

* ID.  
* Nombre.  
* Imagen.  
* URL.  
* Score.

# **DESARROLLO DEL HITO 1 DETALLADO**

Sí. Para practicantes, ese Hito 1 necesita convertirse en una guía operativa, no quedarse en una descripción general.

# **Hito 1 — Integración real del motor de búsqueda visual**

## **Visión del hito**

Actualmente existen cuatro soluciones parciales que funcionan por separado. El objetivo de este hito es convertirlas en **un solo sistema**, donde cada sala entregue un componente compatible con los demás.

Al finalizar, una persona deberá poder subir una imagen desde la interfaz y recibir cinco diseños parecidos provenientes de una única biblioteca, con su nombre, ID, imagen, URL y score.

## **Problema que se resolverá**

Actualmente existen estas dificultades:

* Sala 2 y Sala 4 generan embeddings por separado.  
* Sala 2 y Sala 3 tienen motores de búsqueda distintos.  
* Existen diferentes nombres y ubicaciones para los archivos de embeddings.  
* Sala 3 todavía consume archivos de prueba anteriores.  
* No existe una API central.  
* La interfaz no consume el motor único del proyecto.

El Hito 1 eliminará esa duplicación.

---

# **Resultado final obligatorio**

El sistema debe seguir este único flujo:

**Usuario carga imagen → interfaz envía imagen a la API → CLIP genera embedding → motor busca en el índice único → API devuelve Top 5 → interfaz muestra resultados**

La demostración final debe hacerse desde la interfaz, no ejecutando scripts separados manualmente.

---

# **Estructura común obligatoria**

Antes de comenzar, las cuatro salas deben acordar una única estructura:

proyecto/  
├── api/  
│   ├── main.py  
│   └── search\_engine.py  
├── data/  
│   ├── products.csv  
│   ├── embeddings.npy  
│   ├── ids.npy  
│   └── images/  
├── frontend/  
│   └── app.py  
├── scripts/  
│   └── generate\_embeddings.py  
├── requirements.txt  
└── README.md

No deben crear copias adicionales como:

* `index_embeddings.npy`  
* `embeddings_productos.npy`  
* `scripts/data/embeddings.npy`  
* `embeddings_final_v2.npy`

Debe existir solamente:

data/embeddings.npy  
data/ids.npy  
data/products.csv

---

# **Contrato común de datos**

## **Archivo `products.csv`**

Debe tener exactamente estas columnas:

id  
proveedor  
pagina  
imagen  
nombre\_original  
url

Ejemplo:

AIM-P001-001,Aimari,1,AIM-P001-001.jpg,Guadalcacin Blue,https://...

El campo `imagen` debe contener solamente el nombre del archivo, no una ruta diferente en cada computadora.

## **Archivo `ids.npy`**

Debe conservar el mismo orden que `embeddings.npy`.

Ejemplo:

Posición 0 del embedding → AIM-P001-001  
Posición 1 del embedding → AIM-P001-002  
Posición 2 del embedding → AIM-P001-003

Esta relación es obligatoria. Si se altera el orden, el sistema podría devolver el nombre de una camiseta asociado a otra imagen.

---

# **Sala 1 — Dataset definitivo e ingestión**

## **Objetivo**

Entregar una única fuente confiable de productos para que todo el sistema trabaje con los mismos datos.

## **Actividades**

### **1\. Consolidar el dataset**

Deben generar:

data/products.csv  
data/images/

Las imágenes deben estar dentro de `data/images/`.

### **2\. Validar cada registro**

El script debe verificar:

* ID no vacío.  
* ID no repetido.  
* Nombre no vacío.  
* URL no vacía.  
* Archivo de imagen existente.  
* Imagen que pueda abrirse con Pillow.  
* Extensión permitida: JPG, JPEG o PNG.

### **3\. Corregir la inconsistencia de base de datos**

En el informe anterior mencionaron PostgreSQL, pero utilizaron SQLite. En este hito no es necesario migrar todavía a PostgreSQL. Deben indicar claramente:

> En el Hito 1 se utilizará CSV como fuente común. SQLite queda fuera del flujo integrado.

### **4\. Crear un script de validación**

Archivo:

scripts/validate\_dataset.py

Debe mostrar:

Registros totales:  
Registros válidos:  
IDs duplicados:  
Nombres vacíos:  
URLs vacías:  
Imágenes faltantes:  
Imágenes dañadas:

### **5\. Entregar una función para buscar productos por ID**

Ejemplo:

get\_product\_by\_id("AIM-P001-001")

Debe devolver:

{  
    "id": "AIM-P001-001",  
    "nombre": "Guadalcacin Blue",  
    "imagen": "AIM-P001-001.jpg",  
    "url": "https://...",  
    "proveedor": "Aimari"  
}

## **Entregable de Sala 1**

* `products.csv`  
* Carpeta `images/`  
* `validate_dataset.py`  
* Resultado de validación.  
* Confirmación de que todos los IDs coinciden con las imágenes.

## **Criterio de aceptación**

Sala 1 aprueba si:

* No existen IDs repetidos.  
* No existen imágenes faltantes.  
* Todos los archivos pueden abrirse.  
* Cada ID aparece una sola vez.  
* El CSV puede ser leído sin modificaciones por las otras salas.

---

# **Sala 4 — Embeddings únicos**

## **Objetivo**

Generar el único índice visual que utilizará todo el sistema.

## **Actividades**

### **1\. Usar un solo modelo**

Modelo obligatorio para este hito:

openai/clip-vit-base-patch32

No deben cambiar todavía a SigLIP ni OpenCLIP.

### **2\. Leer directamente `products.csv`**

El script no debe buscar imágenes libremente por carpeta. Debe seguir el orden del CSV.

Flujo:

Lee fila 1 del CSV  
→ abre la imagen correspondiente  
→ genera embedding  
→ guarda el ID en la misma posición

### **3\. Generar por lotes**

Archivo:

scripts/generate\_embeddings.py

Debe procesar imágenes en batches, por ejemplo:

batch\_size \= 16

### **4\. Normalizar los vectores**

Todos los embeddings deben quedar normalizados con L2 antes de guardarse.

### **5\. Guardar solamente dos archivos**

data/embeddings.npy  
data/ids.npy

### **6\. Validar correspondencia**

Al finalizar debe imprimir:

Productos en CSV: 100  
Embeddings generados: 100  
IDs guardados: 100  
Dimensiones: 512  
Errores: 0

### **7\. Probar una imagen externa**

No basta con buscar una imagen que ya se encuentra en la biblioteca. Deben usar al menos tres imágenes externas:

* Una muy parecida.  
* Una con colores diferentes.  
* Una no relacionada.

## **Entregable de Sala 4**

* `generate_embeddings.py`  
* `embeddings.npy`  
* `ids.npy`  
* Tiempo total de procesamiento.  
* Lista de imágenes fallidas, si existieran.  
* Resultado de tres pruebas externas.

## **Criterio de aceptación**

Sala 4 aprueba si:

* El número de embeddings coincide con el número de IDs.  
* Cada vector tiene 512 dimensiones.  
* Todos están normalizados.  
* Los archivos se generan siempre en la misma ruta.  
* No utilizan porcentajes de “confianza”; deben llamarlos scores de similitud.

---

# **Sala 3 — Motor central y API FastAPI**

## **Objetivo**

Crear el único motor de búsqueda y exponerlo mediante una API.

## **Actividades**

### **1\. Eliminar archivos antiguos**

No deben usar los 20 embeddings de prueba mencionados en el informe anterior.

Solo deben cargar:

data/products.csv  
data/embeddings.npy  
data/ids.npy

### **2\. Crear el motor central**

Archivo:

api/search\_engine.py

Debe contener una función:

search\_similar(query\_embedding, top\_k=5)

Debe devolver:

\[  
    {  
        "id": "AIM-P001-001",  
        "nombre": "Guadalcacin Blue",  
        "imagen": "AIM-P001-001.jpg",  
        "url": "https://...",  
        "proveedor": "Aimari",  
        "score": 0.82  
    }  
\]

### **3\. Crear la API**

Archivo:

api/main.py

Endpoint obligatorio:

POST /search/image

Debe recibir una imagen JPG, JPEG o PNG.

### **4\. Flujo interno del endpoint**

El endpoint debe:

1. Recibir la imagen.  
2. Validar el formato.  
3. Convertirla a RGB.  
4. Generar su embedding usando el mismo modelo CLIP.  
5. Normalizar el vector.  
6. Consultar `search_similar`.  
7. Devolver los cinco resultados en JSON.

### **5\. Manejo de errores**

Debe responder correctamente cuando:

* No se envía imagen.  
* El archivo no es una imagen.  
* Falta `embeddings.npy`.  
* Falta `products.csv`.  
* La cantidad de IDs no coincide con los embeddings.  
* El modelo CLIP no puede cargarse.

Ejemplo:

{  
  "error": "El archivo enviado no es una imagen válida"  
}

### **6\. Crear endpoint de verificación**

GET /health

Debe devolver:

{  
  "status": "ok",  
  "products": 100,  
  "embeddings": 100,  
  "model": "openai/clip-vit-base-patch32"  
}

### **7\. Probar la API sin interfaz**

Deben demostrar el endpoint usando Swagger, Postman o `curl`.

## **Entregable de Sala 3**

* `api/main.py`  
* `api/search_engine.py`  
* Endpoint `/search/image`.  
* Endpoint `/health`.  
* Respuesta JSON real.  
* Pruebas de errores.  
* Tiempo promedio de respuesta.

## **Criterio de aceptación**

Sala 3 aprueba si:

* La API inicia sin modificar rutas manualmente.  
* Carga el índice una sola vez al iniciar.  
* Devuelve cinco resultados reales.  
* Los IDs corresponden con los nombres correctos.  
* Maneja errores sin cerrar el servidor.  
* No tiene un motor alternativo o duplicado.

---

# **Sala 2 — Interfaz única**

## **Objetivo**

Convertir Streamlit en cliente de la API, sin volver a generar embeddings ni hacer búsquedas propias.

## **Actividades**

### **1\. Eliminar la lógica duplicada**

La Sala 2 no debe usar:

* `build_index.py`  
* Sentence-Transformers para crear embeddings.  
* `cosine_similarity` local.  
* Lectura directa de `embeddings.npy`.

Su responsabilidad será solamente la interfaz y evaluación.

En el informe anterior construyeron un índice propio; en este hito deben reemplazarlo por consumo de la API.

### **2\. Enviar la imagen a FastAPI**

Cuando el usuario suba una imagen:

Streamlit → POST /search/image → FastAPI

### **3\. Mostrar resultados**

Cada resultado debe mostrar:

* Imagen.  
* ID.  
* Nombre.  
* Proveedor.  
* URL.  
* Score de similitud.

### **4\. Manejar estados**

La interfaz debe mostrar:

* “Procesando imagen”.  
* “No se encontraron resultados”.  
* “El archivo no es válido”.  
* “El servidor no está disponible”.

### **5\. Registrar evaluación**

Debe permitir marcar cada resultado como:

* Correcto.  
* Útil, pero no duplicado.  
* Incorrecto.

También debe incluir una observación.

### **6\. Completar 20 pruebas**

Deben realizar:

* 5 imágenes existentes.  
* 5 imágenes externas parecidas.  
* 5 imágenes diferentes.  
* 5 imágenes fuera del dominio.

### **7\. Crear resultados de evaluación**

Debe generar:

data/evaluation.csv

Con:

consulta  
resultado\_id  
posición  
score  
clasificación\_humana  
observación

## **Entregable de Sala 2**

* `frontend/app.py`  
* Interfaz consumiendo FastAPI.  
* 20 pruebas.  
* `evaluation.csv`  
* Métricas Top 1 y Top 5\.  
* Tiempo percibido por consulta.

## **Criterio de aceptación**

Sala 2 aprueba si:

* No genera embeddings localmente.  
* No ejecuta búsqueda local.  
* Consume únicamente la API.  
* Muestra correctamente cinco resultados.  
* Registra las evaluaciones.  
* Completa las 20 pruebas.

---

# **Orden de trabajo obligatorio**

## **Paso 1**

Sala 1 entrega:

products.csv  
images/

Ninguna otra sala debe avanzar con datos diferentes.

## **Paso 2**

Sala 4 genera:

embeddings.npy  
ids.npy

## **Paso 3**

Sala 3 conecta esos archivos y levanta FastAPI.

## **Paso 4**

Sala 2 conecta Streamlit a FastAPI.

## **Paso 5**

Todos ejecutan una prueba integrada.

---

# **Prueba final del Hito 1**

La demostración debe realizarse así:

1. Ejecutar la API.  
2. Abrir Streamlit.  
3. Comprobar `/health`.  
4. Subir una imagen existente.  
5. Confirmar que aparece como Top 1\.  
6. Subir una imagen externa parecida.  
7. Revisar el Top 5\.  
8. Subir una imagen no relacionada.  
9. Confirmar que los scores son menores.  
10. Registrar la evaluación desde Streamlit.

No se aceptará como demostración ejecutar por separado:

generate\_embeddings.py  
search.py  
app.py con otro índice

Todo debe funcionar conectado.

---

# **Entregable general del Hito 1**

El equipo completo debe entregar:

products.csv  
embeddings.npy  
ids.npy  
FastAPI funcionando  
Streamlit funcionando  
20 pruebas registradas  
README con instrucciones

## **Resultado esperado**

Al finalizar, debe existir **un único prototipo integrado**, no cuatro proyectos independientes.

La frase de validación será:

> “Una imagen se carga una sola vez, se procesa con un solo modelo, se compara contra un solo índice y los resultados se muestran en una sola interfaz.”

