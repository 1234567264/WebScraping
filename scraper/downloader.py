import requests
from pathlib import Path
from utils.helpers import (
    leer_productos,
    IMAGES_DIR,
)


def descargar_imagenes():

    productos = leer_productos()

    ruta_imagenes = Path(IMAGES_DIR)

    ruta_imagenes.mkdir(parents=True, exist_ok=True)

    print(f"Descargando {len(productos)} imágenes...\n")

    for producto in productos:

        nombre_archivo = producto["archivo"]

        respuesta = requests.get(producto["url"])

        respuesta.raise_for_status()

        with open(
            ruta_imagenes / nombre_archivo,
            "wb"
        ) as archivo:

            archivo.write(respuesta.content)

        print(f"[OK] {nombre_archivo}")

    print("\nDescarga finalizada.")