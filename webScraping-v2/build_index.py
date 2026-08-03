# -*- coding: utf-8 -*-
"""
build_index.py
---------------
Recorre data/productos.json + data/images/ (generados por el scraper de las
otras salas) y crea un "indice" de busqueda: convierte cada imagen en un
vector numerico (embedding) usando el modelo CLIP, que entiende el contenido
visual de la imagen (colores, formas, estilo).

Genera:
    data/index_embeddings.npy  -> matriz con todos los vectores
    data/index_metadata.json   -> nombre, url y archivo de cada imagen indexada

Correr UNA vez (o cada vez que agreguen productos nuevos):
    python build_index.py
"""

import json
import os
import numpy as np
from PIL import Image
from sentence_transformers import SentenceTransformer

DATA_DIR = "data"
IMAGES_DIR = os.path.join(DATA_DIR, "images")
PRODUCTOS_JSON = os.path.join(DATA_DIR, "productos.json")
INDEX_EMB = os.path.join(DATA_DIR, "index_embeddings.npy")
INDEX_META = os.path.join(DATA_DIR, "index_metadata.json")


def main():
    if not os.path.exists(PRODUCTOS_JSON):
        print(f"ERROR: no se encontro {PRODUCTOS_JSON}")
        print("Asegurate de haber corrido el scraper (main.py) antes de esto.")
        return

    print("Cargando modelo CLIP (la primera vez descarga ~350MB, ten paciencia)...")
    model = SentenceTransformer("clip-ViT-B-32")

    with open(PRODUCTOS_JSON, "r", encoding="utf-8") as f:
        productos = json.load(f)

    embeddings = []
    metadata = []

    print(f"Procesando {len(productos)} productos...")
    for i, p in enumerate(productos, start=1):
        archivo = p.get("archivo")
        ruta = os.path.join(IMAGES_DIR, archivo) if archivo else None

        if not ruta or not os.path.exists(ruta):
            print(f"  [{i}/{len(productos)}] SALTADO (no existe la imagen): {archivo}")
            continue

        try:
            img = Image.open(ruta).convert("RGB")
            emb = model.encode(img)
            embeddings.append(emb)
            metadata.append({
                "nombre": p.get("nombre", ""),
                "url": p.get("url", ""),
                "archivo": archivo,
            })
            print(f"  [{i}/{len(productos)}] OK: {p.get('nombre')}")
        except Exception as e:
            print(f"  [{i}/{len(productos)}] ERROR con {archivo}: {e}")

    if not embeddings:
        print("No se pudo indexar ninguna imagen. Revisa que data/images/ tenga archivos.")
        return

    embeddings = np.array(embeddings, dtype="float32")
    np.save(INDEX_EMB, embeddings)
    with open(INDEX_META, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"\nListo. Indice generado con {len(metadata)} imagenes.")
    print(f"  -> {INDEX_EMB}")
    print(f"  -> {INDEX_META}")


if __name__ == "__main__":
    main()
