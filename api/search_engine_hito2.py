# -*- coding: utf-8 -*-
"""
search_engine_hito2.py
----------------------
SALA 4 - Hito 2: Motor mejorado y reranking del Top 5.

El Hito 1 (api/search_engine.py) devuelve los 5 candidatos más cercanos
según CLIP. El problema observado es que el Top 1 suele ser correcto, pero
el Top 2-5 a veces son matemáticamente cercanos en el espacio de CLIP y
visualmente irrelevantes para una persona (por ejemplo, mismos colores pero
diseño distinto, o diseño distinto con misma estructura).

Para solucionarlo, este módulo NO reemplaza el Hito 1: lo usa como capa
base y le agrega una capa de reranking por color. El pipeline es:

1) RECUPERACIÓN AMPLIA: pedimos más candidatos de los que vamos a devolver
   (p.ej. 30 en vez de 5). Así el reranking no se queda ciego: si el diseño
   correcto quedó en el puesto 12 del ranking de CLIP, todavía puede subir.

2) RERANKING VISUAL: cada candidato abre su imagen real en
   data/images_final/ y se compara su histograma de color HSV contra el de
   la imagen de consulta. El color es un atributo que CLIP promedia en todo
   el espacio de la imagen y puede "esconder", por eso la comparación directa
   de histogramas refuerza la similitud percibida por una persona.

3) SCORE PONDERADO: combinamos el score de embeddings (CLIP) con el score
   de color (HSV) con pesos ajustables.

4) UMBRAL DINÁMICO: en vez de forzar siempre 5 resultados, descartamos los
   candidatos que quedan demasiado por debajo del mejor. Si no hay suficiente
   calidad, se devuelven menos resultados (prefiero pocos y buenos a 5 con
   "relleno").

Los pesos y el margen son constantes al inicio del archivo para poder
ajustarlos con las 50 consultas de la evaluación.
"""

import os

import numpy as np
import cv2

from api.search_engine import DATADIR, cargar_indice, search_similar

# Peso del score original de embeddings (CLIP) en el score final
PESO_EMBEDDING = 0.7
# Peso del score de color (histograma HSV) en el score final
PESO_COLOR = 0.3
# Margen de corte dinámico: se descartan candidatos cuyo score_final quede
# más de este valor por debajo del mejor resultado
MARGEN_CORTE = 0.35

# Carpeta donde viven las imágenes reales del catálogo (misma que usa Hito 1)
CARPETA_IMAGENES = os.path.join(DATADIR, "images_final")

# Cache de histogramas: cada imagen real se lee y procesa una sola vez por
# proceso. Con un catálogo fijo de 1000 imágenes esto evita re-leer el
# archivo en cada consulta y acelera mucho la evaluación con 50 queries.
_cache_histogramas = {}


def _a_imagen_bgr(imagen):
    """
    Convierte la imagen de consulta a un arreglo BGR (formato que espera
    OpenCV). Acepta una ruta de archivo (str), un objeto PIL.Image (lo que
    recibe el endpoint) o un arreglo numpy ya en BGR. Devuelve None si no
    se puede obtener una imagen válida.
    """
    if imagen is None:
        return None

    # Ruta de archivo
    if isinstance(imagen, (str, os.PathLike)):
        bgr = cv2.imread(str(imagen))
        if bgr is None:
            return None
        return bgr

    # Objeto PIL.Image (como lo abre api/main.py)
    if hasattr(imagen, "convert"):
        try:
            arr = np.array(imagen.convert("RGB"))
        except Exception:
            return None
        # PIL entrega RGB, OpenCV trabaja en BGR: hay que reordenar canales
        return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)

    # Arreglo numpy ya preparado
    if isinstance(imagen, np.ndarray):
        return imagen

    return None


def _histograma_hsv(bgr):
    """
    Calcula el histograma HSV normalizado de una imagen BGR.
    El espacio HSV separa el color (H/S) del brillo (V), por eso responde
    mejor que RGB a "la paleta de colores del diseño", que es lo que una
    persona percibe primero en una camiseta.
    """
    if bgr is None or bgr.size == 0:
        return None

    # Si llegó una imagen en escala de grises (1 canal), la repetimos a BGR
    if bgr.ndim == 2:
        bgr = cv2.cvtColor(bgr, cv2.COLOR_GRAY2BGR)

    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)

    # 8 bins por canal: un balance entre granularidad y ruido. Si pusiéramos
    # 256 bins, dos fotos del mismo diseño con distinta iluminación darían
    # histogramas "distintos"; con pocos bins se captura la paleta global.
    histograma = cv2.calcHist(
        [hsv], [0, 1, 2], None,
        [8, 8, 8], [0, 180, 0, 256, 0, 256],
    )

    # Normalizar para que la comparación no dependa del tamaño/resolución
    cv2.normalize(histograma, histograma, 0, 1, cv2.NORM_MINMAX)
    return histograma


def _histograma_de_archivo(nombre_archivo):
    """
    Lee la imagen real de un candidato desde data/images_final/ y devuelve
    su histograma HSV. Usa cache para no re-leer el archivo en cada query.
    Devuelve None si la imagen no existe o no se puede abrir.
    """
    if nombre_archivo in _cache_histogramas:
        return _cache_histogramas[nombre_archivo]

    ruta = os.path.join(CARPETA_IMAGENES, str(nombre_archivo))
    bgr = cv2.imread(ruta)
    hist = _histograma_hsv(bgr)

    # Se guarda también el resultado None para no re-intentar abrir un
    # archivo corrupto en cada consulta
    _cache_histogramas[nombre_archivo] = hist
    return hist


def search_similar_reranked(
    query_embedding,
    query_image,
    top_k: int = 5,
    candidatos_iniciales: int = 30,
) -> list[dict]:
    """
    Búsqueda visual con reranking por color HSV (Hito 2).

    Paso 1: recuperación amplia con search_similar() del Hito 1 pidiendo
    candidatos_iniciales en vez de top_k directo.
    Paso 2: reranking ponderando el score de CLIP con el score de color.
    Paso 3: umbral dinámico que permite devolver menos de top_k resultados.

    Contrato de respuesta: list de objetos con las keys del Hito 1
    (id, nombre, imagen, url, proveedor, score) más:
      - score_inicial   : score de embeddings original (CLIP)
      - score_color     : similitud de histograma HSV
      - score_reranking : score_final ponderado (0.7*CLIP + 0.3*color)
      - posicion_final  : rango final 1-indexado tras el reranking
      - modelo_utilizado: "clip+color_hsv"
    """
    # Asegurar que el índice del Hito 1 está cargado (search_similar lo hace
    # solo, pero esta importación no da error si df es None)
    if os.path.isfile(os.path.join(DATADIR, "embeddings.npy")):
        cargar_indice()

    # ── Paso 1: RECUPERACIÓN AMPLIA ──────────────────────────────────────
    # Buscamos más candidatos de los que devolveremos para darle al
    # reranking la oportunidad de "resucitar" el diseño correcto si CLIP lo
    # dejó fuera del top 5.
    candidatos = search_similar(query_embedding, top_k=candidatos_iniciales)

    # Histograma HSV de la consulta, calculado una sola vez
    bgr_consulta = _a_imagen_bgr(query_image)
    hist_consulta = _histograma_hsv(bgr_consulta)

    # ── Paso 2: RERANKING POR COLOR ──────────────────────────────────────
    reranked = []
    for cand in candidatos:
        # Score del Hito 1: similitud coseno de embeddings
        score_embedding = cand["score"]

        # Score de color: comparación de histogramas HSV. Si la imagen del
        # candidato no se puede abrir, el score_color queda en 0: la
        # búsqueda NO debe romperse por una sola imagen defectuosa.
        score_color = 0.0
        if hist_consulta is not None:
            hist_cand = _histograma_de_archivo(cand["imagen"])
            if hist_cand is not None:
                # HISTCMP_CORREL: correlación, 1 = idéntico, 0 = sin relación
                score_color = float(cv2.compareHist(
                    hist_consulta, hist_cand, cv2.HISTCMP_CORREL,
                ))

        score_final = (
            PESO_EMBEDDING * score_embedding
            + PESO_COLOR * score_color
        )

        reranked.append({
            **cand,
            "score_inicial": round(float(score_embedding), 4),
            "score_color": round(score_color, 4),
            "score_reranking": round(float(score_final), 4),
        })

    # Ordenar por score_final descendente
    reranked.sort(key=lambda r: r["score_reranking"], reverse=True)

    # ── Paso 3: UMBRAL DINÁMICO ──────────────────────────────────────────
    # Solo conservamos candidatos cuya calidad esté razonablemente cerca del
    # mejor resultado. Si el 2do candidato está muy por debajo, no lo
    # forzamos: devolvemos menos de top_k en lugar de relleno irrelevante.
    if reranked:
        mejor_score = reranked[0]["score_reranking"]
        limite_corte = mejor_score - MARGEN_CORTE
        reranked = [
            r for r in reranked if r["score_reranking"] >= limite_corte
        ]

    # Recortar a top_k y asignar la posición final
    final = []
    for posicion, r in enumerate(reranked[:top_k], start=1):
        r["posicion_final"] = posicion
        r["modelo_utilizado"] = "clip+color_hsv"
        final.append(r)

    return final
