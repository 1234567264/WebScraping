import os
import json
import pandas as pd


def cargar_productos_sala1(json_path: str = None) -> pd.DataFrame:
    """
    Lee webScraping-v2/data/productos.json (entregado por Sala 1) y devuelve
    un DataFrame de pandas con las columnas: id, nombre_original, imagen, url, proveedor.
    No lee ni depende de ningún archivo .npy.
    """
    if json_path is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_dir, "data", "productos.json")

    if not os.path.exists(json_path):
        raise FileNotFoundError(f"No se encontró el archivo productos.json de Sala 1 en: {json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    df = pd.DataFrame(data)

    # Mapear nombre -> nombre_original
    if "nombre" in df.columns and "nombre_original" not in df.columns:
        df["nombre_original"] = df["nombre"]

    # Mapear archivo -> imagen
    if "archivo" in df.columns and "imagen" not in df.columns:
        df["imagen"] = df["archivo"]

    # Proveedor por defecto si no existe
    if "proveedor" not in df.columns:
        df["proveedor"] = "Designs Aimari"

    columnas_requeridas = ["id", "nombre_original", "imagen", "url", "proveedor"]
    for col in columnas_requeridas:
        if col not in df.columns:
            df[col] = ""

    return df[columnas_requeridas]
