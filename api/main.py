import io
import os
import sys
import time
from PIL import Image
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sentence_transformers import SentenceTransformer

# Asegurar importación del módulo search_engine independientemente del working directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from api.search_engine import cargar_indice, info_indice, search_similar

app = FastAPI(
    title="Motor de Búsqueda Visual RAG - Sala 3 API",
    description="API FastAPI para búsqueda e integración visual de camisetas deportivas",
    version="1.0.0"
)

# Configuración CORS para la interfaz de Sala 2 y clientes frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_NAME = "clip-ViT-B-32"  # equivalente a openai/clip-vit-base-patch32
_model = None


def get_model():
    """Retorna la instancia singleton del modelo CLIP, cargándolo si es necesario."""
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


@app.on_event("startup")
def startup():
    """Carga el índice de vectores y el modelo CLIP una sola vez al iniciar el servidor."""
    try:
        cargar_indice()
        print("[API] Índice de embeddings y dataset cargado correctamente.")
    except Exception as e:
        print(f"[API] AVISO al cargar índice: {e}")

    try:
        get_model()
        print(f"[API] Modelo CLIP '{MODEL_NAME}' cargado correctamente.")
    except Exception as e:
        print(f"[API] ERROR al cargar el modelo CLIP: {e}")


@app.get("/health")
def health():
    """Endpoint de verificación del estado de la API y datos indexados."""
    try:
        info = info_indice()
        return {
            "status": "ok",
            "products": info["products"],
            "embeddings": info["embeddings"],
            "model": "openai/clip-vit-base-patch32",
            "desfase_detectado": info.get("desfase_detectado", False),
            "observacion": info.get("observacion", ""),
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "detail": str(e)}
        )


@app.post("/search/image")
async def search_image(file: UploadFile = File(...)):
    """
    Recibe una imagen (JPG/PNG), genera su embedding con CLIP y devuelve los 5 productos más parecidos.
    Devuelve lista de objetos con id, nombre, imagen, url, proveedor y score.
    """
    if file.content_type and file.content_type not in ("image/jpeg", "image/jpg", "image/png"):
        return JSONResponse(
            status_code=400,
            content={"error": "El archivo enviado no es una imagen válida"}
        )

    try:
        contenido = await file.read()
        imagen = Image.open(io.BytesIO(contenido)).convert("RGB")
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"error": "El archivo enviado no es una imagen válida"}
        )

    try:
        model = get_model()
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error al cargar el modelo CLIP: {str(e)}"}
        )

    try:
        t0 = time.perf_counter()
        embedding = model.encode(imagen)
        resultados = search_similar(embedding, top_k=5)
        tiempo_segundos = round(time.perf_counter() - t0, 4)
        return {
            "resultados": resultados,
            "tiempo_segundos": tiempo_segundos,
        }
    except FileNotFoundError as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Falta un archivo de datos: {str(e)}"}
        )
    except ValueError as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error interno: {str(e)}"}
        )
