# Sala 2 — Interfaz y evaluación

## Qué hace esto

- `build_index.py` → convierte todas tus imágenes ya descargadas en "huellas
  digitales" numéricas (embeddings) usando un modelo de IA llamado CLIP.
  Esto es lo que permite comparar imágenes por parecido visual.
- `app.py` → la interfaz Streamlit: subes una imagen, te muestra las 5 más
  parecidas con nombre, URL y score, y puedes marcar cada una como
  correcta/incorrecta.
- `reporte_evaluacion.py` → junta todas las evaluaciones que guardaste en la
  app y arma la tabla final (Consulta / Top 1 correcto / Top 5 útiles /
  Observación) para el entregable.

## Paso 1: Copiar estos archivos a tu proyecto

Copia estos 4 archivos (`build_index.py`, `app.py`, `reporte_evaluacion.py`,
`requirements_sala2.txt`) directamente dentro de la carpeta `webScraping-v2`,
al mismo nivel que `main.py`. Debe quedar así:

```
webScraping-v2/
├── main.py
├── build_index.py          <- nuevo
├── app.py                  <- nuevo
├── reporte_evaluacion.py   <- nuevo
├── requirements_sala2.txt  <- nuevo
├── scraper/
├── storage/
├── utils/
└── data/
    ├── images/
    ├── productos.json
    └── ...
```

## Paso 2: Estar en la rama correcta y el entorno activado

```
git checkout sala-2
source venv/Scripts/activate
```
Debes ver `(venv)` al inicio de tu línea de terminal.

## Paso 3: Instalar las librerías nuevas

Esto va a tardar varios minutos la primera vez (descarga PyTorch, que pesa
bastante) — es normal, ten paciencia:

```
pip install -r requirements_sala2.txt
```

## Paso 4: Construir el índice (una sola vez)

```
python build_index.py
```

La primera vez que corras esto va a descargar el modelo CLIP (~350MB), así
que también puede tardar un poco. Vas a ver algo como:

```
Procesando 120 productos...
  [1/120] OK: Magic Glitter
  [2/120] OK: Basketball Design Lince Geometric
  ...
Listo. Indice generado con 120 imagenes.
```

Esto crea dos archivos nuevos dentro de `data/`:
- `index_embeddings.npy`
- `index_metadata.json`

## Paso 5: Correr la interfaz

```
streamlit run app.py
```

Se va a abrir automáticamente una pestaña en tu navegador (algo como
`http://localhost:8501`). Ahí:

1. Sube una imagen de prueba con el botón "Sube una imagen de consulta"
2. Vas a ver a la izquierda la imagen que subiste, y a la derecha las 5 más
   parecidas con nombre, URL y score
3. Para cada una, marca si te parece "Correcto" o "Incorrecto"
4. Escribe una observación si quieres
5. Dale clic a "💾 Guardar evaluación de esta consulta"

**Repite esto con tus 20 imágenes de prueba** (una por una). Cada vez que
guardes, se agrega una fila nueva a `data/evaluacion.csv` — no se borra lo
anterior.

Para preparar las 20 imágenes de prueba: puedes usar 20 fotos de camisetas
reales (capturas de pantalla, fotos que descargues de internet, o algunas de
las mismas imágenes ya descargadas pero renombradas) — lo importante es que
sean variadas para probar bien el sistema.

## Paso 6: Generar el reporte final

Cuando ya hayas evaluado las 20 imágenes, corre:

```
python reporte_evaluacion.py
```

Esto imprime la tabla en la terminal y genera `data/reporte_evaluacion.xlsx`
con las columnas que pide la consigna:

| Consulta | Top 1 correcto | Top 5 útiles | Observación |
|---|---|---|---|

Ese Excel es tu entregable final junto con la app funcionando.

## Problemas comunes

- **"No module named streamlit"** → no activaste el entorno virtual
  (`source venv/Scripts/activate`) o no corriste el `pip install` del Paso 3.
- **Error al cargar el modelo CLIP / se cuelga descargando** → revisa tu
  conexión a internet, la primera descarga es pesada.
- **"No se encontró data/productos.json"** → primero debes correr el
  scraper (`python main.py --paginas 3,4 --imagenes all --modo fresh`) para
  generar esos datos.
