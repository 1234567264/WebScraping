import base64
import io
import os
import sys
import time
import uuid
from datetime import datetime, timezone

from PIL import Image
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sentence_transformers import SentenceTransformer

# Asegurar importación del módulo search_engine independientemente del working directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from api.search_engine import cargar_indice, info_indice, search_similar
from api.search_engine_hito2 import search_similar_reranked
from api.preprocesar_consulta import preparar_consulta

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

# Parámetros del Hito 2: cuántos candidatos se recuperan en la fase amplia
# antes de hacer el reranking por color.
CANDIDATOS_INICIALES = 30

# Guardado de las dos versiones de cada consulta (Sala 2, Hito 2)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
QUERIES_ORIGINAL_DIR = os.path.join(BASE_DIR, "data", "queries_original")
QUERIES_PROCESADA_DIR = os.path.join(BASE_DIR, "data", "queries_procesadas")


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


def _imagen_b64(imagen) -> str:
    """Codifica una imagen PIL en base64 (JPEG)."""
    buf = io.BytesIO()
    imagen.convert("RGB").save(buf, "JPEG", quality=90)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def _guardar_versiones(query_id, original, procesada):
    """Guarda la consulta original y la procesada para comparar resultados."""
    os.makedirs(QUERIES_ORIGINAL_DIR, exist_ok=True)
    os.makedirs(QUERIES_PROCESADA_DIR, exist_ok=True)
    original.save(os.path.join(QUERIES_ORIGINAL_DIR, f"{query_id}.jpg"), "JPEG", quality=92)
    procesada.save(os.path.join(QUERIES_PROCESADA_DIR, f"{query_id}.jpg"), "JPEG", quality=92)


@app.post("/search/image")
async def search_image(file: UploadFile = File(...), modo: str = Form("auto")):
    """
    Recibe una imagen (JPG/PNG) y devuelve los 5 productos más parecidos.

    Parametro de formulario `modo` (Sala 2, Hito 2):
      - "auto"      : prepara la consulta (remueve fondo/recorta) y devuelve
                      respuesta enriquecida (original + procesada + ambos
                      rankings + preprocesamiento + modelo).
      - "procesada" : fuerza el uso de la imagen preparada (motor Hito 2).
      - "original"  : fuerza el uso de la consulta tal como llega (motor Hito 1).
      - "legacy"    : devuelve solo la lista del motor (comportamiento Hito 1).
      - "completo"  : prepara la consulta (Sala 2) y aplica el reranking
                      visual (Sala 3): Sala 1 + Sala 2 + Sala 3 juntos.
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
        if modo == "legacy":
            embedding = model.encode(imagen)
            return search_similar(embedding, top_k=5)

        prep = preparar_consulta(imagen)
        procesada = prep["procesada"]

        emb_original = model.encode(imagen)
        emb_procesada = model.encode(procesada)
        res_original = search_similar(emb_original, top_k=5)
        res_procesada = search_similar(emb_procesada, top_k=5)

        query_id = f"q_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        _guardar_versiones(query_id, imagen, procesada)

        if modo == "completo":
            modo_usado = "completo"
            resultados = search_similar_reranked(
                emb_procesada,
                query_image=procesada,
                top_k=5,
                candidatos_iniciales=CANDIDATOS_INICIALES,
            )
        elif modo == "procesada":
            modo_usado = "procesada"
            resultados = res_procesada
        elif modo == "original":
            modo_usado = "original"
            resultados = res_original
        else:
            # Auto = Hito 2: buscar con la consulta preparada (mejor Top 5).
            # La respuesta incluye resultados_original para comparar.
            modo_usado = "procesada"
            resultados = res_procesada

        return {
            "query_id": query_id,
            "modo": modo_usado,
            "modelo": "openai/clip-vit-base-patch32",
            "preprocesamiento": {
                "ok": True,
                "pasos": prep["pasos"],
                "backend": prep["backend"],
                "bbox": prep["bbox"],
                "recorte_pct": prep["recorte_pct"],
                "tiempo_segundos": prep["tiempo_segundos"],
            },
            "tiempo_segundos": round(time.perf_counter() - t0, 3),
            "imagen_original_b64": _imagen_b64(imagen),
            "imagen_procesada_b64": _imagen_b64(procesada),
            "resultados": resultados,
            "resultados_original": res_original,
            "resultados_procesada": res_procesada,
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


@app.post("/search/image/v2")
async def search_image_v2(file: UploadFile = File(...)):
    """
    Hito 2: Motor mejorado con reranking por color HSV.
    Recibe la imagen igual que /search/image, pero en vez de devolver el
    top 5 directo de CLIP, hace una recuperación amplia de
    CANDIDATOS_INICIALES y reordena combinando el score de CLIP con el
    score del histograma HSV de la imagen real (recuperación amplia +
    reranking + umbral dinámico, ver api/search_engine_hito2.py).
    """
    # Mismo control de tipo de archivo que el endpoint del Hito 1
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
        resultados = search_similar_reranked(
            embedding,
            query_image=imagen,
            top_k=5,
            candidatos_iniciales=CANDIDATOS_INICIALES,
        )
        tiempo_segundos = round(time.perf_counter() - t0, 4)
        return {
            "resultados": resultados,
            "tiempo_segundos": tiempo_segundos,
            "candidatos_evaluados": CANDIDATOS_INICIALES,
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
