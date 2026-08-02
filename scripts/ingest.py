

import os
import json
import pandas as pd
import numpy as np

DATADIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
CSVPATH = os.path.join(DATADIR, "products.csv")
JSONPATH = os.path.join(DATADIR, "metadata.json")
EMBEDDINGSPATH = os.path.join(DATADIR, "embeddings.npy")


def GuardarProductos_csv(df_productos: pd.DataFrame, csv_path: str = CSVPATH):
    """
    Guarda el dataframe de productos en formato CSV.
    Campos requeridos: id, proveedor, pagina, imagen, nombre_original, url
    """
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    df_productos.to_csv(csv_path, index=False, encoding="utf-8")
    print(f"[Ingest] Guardados {len(df_productos)} productos en {csv_path}")


def GuardarEmbeddings(matrix_embeddings: np.ndarray, embeddings_path: str = EMBEDDINGSPATH):
    """
    Guarda la matriz de embeddings (N_productos, Dimensión) en un archivo .npy.
    """
    os.makedirs(os.path.dirname(embeddings_path), exist_ok=True)
    # Convertir a float32 para optimizar rendimiento y compatibilidad
    matrix = np.array(matrix_embeddings, dtype=np.float32)
    
    # facilitar el cálculo directo de Similitud del Coseno mediante producto punto
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    # Evitar división por cero
    norms[norms == 0] = 1.0
    matrix_normalized = matrix / norms
    
    np.save(embeddings_path, matrix_normalized)
    print(f"[Ingest] Guardados {matrix_normalized.shape[0]} embeddings de dimensión {matrix_normalized.shape[1]} en {embeddings_path}")


def InicializarDatosDemo(n_samples: int = 20, dim: int = 512):
    """
    Función helper para generar un dataset sintético inicial de prueba (smoke test),
    para asegurar que la Sala 3 puede funcionar de inmediato sin esperar a las otras salas.
    """
    print(f"[Ingest] Generando dataset de prueba con {n_samples} elementos...")
    
    productos = []
    for i in range(1, n_samples + 1):
        prod_id = f"BUS-P001-{i:03d}"
        productos.append({
            "id": prod_id,
            "proveedor": "Bustencio",
            "pagina": 1,
            "imagen": f"{prod_id}.jpg",
            "nombre_original": f"Camiseta Deportiva Modelo #{i}",
            "url": f"https://designsaimari.com/{prod_id}"
        })
        
    df = pd.DataFrame(productos)
    GuardarProductos_csv(df)
    
    # Vectores sintéticos aleatorios normalizados
    embeddings_dummy = np.random.randn(n_samples, dim).astype(np.float32)
    GuardarEmbeddings(embeddings_dummy)
    print("[Ingest] Dataset de prueba generado exitosamente.")


if __name__ == "__main__":
    InicializarDatosDemo(n_samples=20, dim=512)
