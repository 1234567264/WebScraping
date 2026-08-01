# Aimari Web Scraper

Web scraper desarrollado en Python para extraer diseños de la página **Designs Aimari**.

El proyecto permite:

- Extraer productos desde páginas web.
- Obtener nombres e imágenes.
- Guardar información en JSON.
- Descargar imágenes localmente.
- Exportar datos a Excel.
- Controlar cantidad de imágenes.
- Trabajar con múltiples páginas.
- Ejecutar procesos en modo `fresh` o `update`.

---

# Características

## Extracción de productos

El scraper obtiene:

- Nombre del diseño.
- URL de la imagen.
- Extensión del archivo.
- Nombre final del archivo.

Ejemplo:

```json
{
    "numero": 1,
    "nombre": "Guadalcacin Blue",
    "url": "https://media.designsaimari.com/products/image.jpg",
    "archivo": "1-Guadalcacin Blue.jpg"
}
```

---

# Estructura del proyecto

```
webScraping-v2/

│
├── main.py
│
├── scraper/
│   ├── scraper.py
│   ├── parser.py
│   └── downloader.py
│
├── storage/
│   └── exporter.py
│
├── utils/
│   ├── helpers.py
│   ├── pagination.py
│   ├── limits.py
│   └── update.py
│
├── data/
│   ├── images/
│   ├── html/
│   ├── productos.json
│   ├── metadata.json
│   └── productos.xlsx
│
└── requirements.txt
```

---

# Instalación

## 1. Clonar proyecto

```bash
git clone <url-del-repositorio>
```

Entrar a la carpeta:

```bash
cd webScraping-v2
```

---

## 2. Crear entorno virtual (recomendado)

Windows:

```bash
python -m venv venv
```

Activar:

```bash
venv\Scripts\activate
```

Linux / Mac:

```bash
source venv/bin/activate
```

---

## 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

# Dependencias utilizadas

## requests

Permite realizar peticiones HTTP.

Uso:

- Descargar HTML.
- Descargar imágenes.

---

## beautifulsoup4

Permite analizar HTML.

Uso:

- Buscar imágenes.
- Extraer atributos como `src` y `alt`.

---

## lxml

Parser utilizado por BeautifulSoup.

Permite una lectura más rápida del HTML.

---

## openpyxl

Permite generar archivos Excel.

Uso:

- Exportar productos a `.xlsx`.

---

# Uso del programa

La ejecución principal se realiza mediante:

```bash
python main.py
```

---

# Argumentos disponibles

El programa acepta tres argumentos:

```
--imagenes
--paginas
--modo
```

---

# Control de imágenes

Argumento:

```bash
--imagenes
```

Controla cuántas imágenes descargar.

---

## Descargar todas las imágenes

```bash
python main.py --imagenes all
```

Resultado:

Descarga todos los productos encontrados.

---

## Descargar cantidad específica

Ejemplo:

```bash
python main.py --imagenes 100
```

Resultado:

Selecciona solamente las primeras 100 imágenes.

---

# Control de páginas

Argumento:

```bash
--paginas
```

Define qué páginas serán procesadas.

---

## Página individual

Ejemplo:

```bash
python main.py --paginas 1
```

Procesa únicamente:

```
pagina=1
```

---

## Varias páginas

Ejemplo:

```bash
python main.py --paginas 1,2,3
```

Procesa:

```
pagina 1
pagina 2
pagina 3
```

---

## Todas las páginas

Ejemplo:

```bash
python main.py --paginas all
```

Procesa todas las páginas disponibles.

---

# Modos de ejecución

Argumento:

```bash
--modo
```

Actualmente existen dos modos:

```
fresh
update
```

---

# Modo fresh

Es el modo de limpieza completa.

Ejemplo:

```bash
python main.py --modo fresh
```

Funcionamiento:

1. Limpia la carpeta `data`.
2. Genera nueva metadata.
3. Extrae nuevamente todos los productos.
4. Guarda un nuevo JSON.
5. Descarga nuevamente las imágenes.
6. Genera nuevamente el Excel.

Útil cuando:

- Se quiere una extracción desde cero.
- Se quiere actualizar toda la base.

---

# Modo update

Ejemplo:

```bash
python main.py --modo update
```

Funcionamiento:

1. Lee productos existentes.
2. Obtiene nuevos productos.
3. Fusiona información nueva con información antigua.
4. Conserva productos existentes.

Útil cuando:

- La página tiene nuevos diseños.
- No se quiere borrar información anterior.

---

# Ejemplos completos

## Extraer primera página completa

```bash
python main.py --paginas 1 --imagenes all --modo fresh
```

---

## Extraer páginas 1 y 2 con límite de imágenes

```bash
python main.py --paginas 1,2 --imagenes 100 --modo fresh
```

---

## Actualizar información existente

```bash
python main.py --paginas 1,2 --modo update
```

---

# Archivos generados

Después de ejecutar el scraper:

## productos.json

Contiene todos los productos extraídos.

Ejemplo:

```
data/productos.json
```

---

## metadata.json

Guarda información de páginas procesadas.

Ejemplo:

```json
{
    "paginas": {
        "1": {
            "cantidad":60
        },
        "2":{
            "cantidad":60
        }
    },
    "items_por_pagina":60
}
```

---

## images/

Contiene las imágenes descargadas.

Ejemplo:

```
data/images/

1-Guadalcacin Blue.jpg
2-Argentina Drexx.jpg
3-Ballbreakers DUO Kit.jpg
```

---

## productos.xlsx

Archivo Excel generado con la información extraída.

---

# Flujo interno

El programa trabaja en este orden:

```
main.py

    |
    |
    ↓

Obtener configuración CLI

    |
    |
    ↓

Validar metadata

    |
    |
    ↓

Descargar HTML

    |
    |
    ↓

Parsear productos

    |
    |
    ↓

Aplicar límite de imágenes

    |
    |
    ↓

Actualizar o reemplazar JSON

    |
    |
    ↓

Descargar imágenes

    |
    |
    ↓

Exportar Excel
```

---

# Próximas mejoras

Pendientes:

- Soporte completo para rangos de páginas:
  ```
  --paginas 1-5
  ```

- Mejor sistema de actualización usando identificadores únicos.

- Evitar descargar imágenes repetidas.

- Control de errores de conexión.

- Descarga paralela de imágenes.

- Registro de logs.

---

# Autor

Proyecto desarrollado para automatización de extracción de diseños deportivos desde Designs Aimari.
