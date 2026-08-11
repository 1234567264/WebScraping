# -*- coding: utf-8 -*-
"""
search_engine_hito2.py
----------------------
SALA 3 - Hito 2: Motor mejorado y reranking del Top 5.

El Hito 1 (api/search_engine.py) devuelve los 5 candidatos más cercanos
según CLIP. El problema observado es que el Top 1 suele ser correcto, pero
el Top 2-5 a veces son matemáticamente cercanos en el espacio de CLIP y
visualmente irrelevantes para una persona (por ejemplo, mismos colores pero
diseño distinto, o diseño distinto con misma estructura).

Para solucionarlo, este módulo NO reemplaza el Hito 1: lo usa como capa
base y le agrega una capa de reranking visual. El pipeline es:

1) RECUPERACIÓN AMPLIA: pedimos más candidatos de los que vamos a devolver
   (p.ej. 30 en vez de 5). Así el reranking no se queda ciego: si el diseño
   correcto quedó en el puesto 12 del ranking de CLIP, todavía puede subir.

2) RERANKING VISUAL (múltiples criterios, pesos en constantes para probar):
   a) COLOR GLOBAL: histograma HSV de la imagen completa. El color es un
      atributo que CLIP promedia en todo el espacio de la imagen y puede
      "esconder"; la comparación directa de histogramas refuerza la
      similitud percibida por una persona.
   b) COLOR POR REGIONES (frente/espalda): el banco tiene una estructura
      consistente (frente a la izquierda, espalda a la derecha, ver
      data/informe_formatos.txt). Se divide cada imagen en dos mitades y se
      compara el histograma de cada mitad por separado. Así un diseño con el
      frente parecido pero espalda distinta no gana solo por el promedio.
   c) ESTRUCTURA / DISTRIBUCIÓN DEL PATRÓN: comparación en escala de grises
      a baja resolución (32x32). Captura la "forma" del diseño
      independiente del color: dos versiones recoloreadas del mismo diseño
      quedan cerca, mientras que un diseño distinto con los mismos colores
      se aleja.

3) SCORE PONDERADO: combinamos el score de embeddings (CLIP) con los scores
   de color y estructura con pesos ajustables (constantes al inicio del
   archivo). Los pesos se calibraron y pueden re-ajustarse con las 50
   consultas de la evaluación (scripts/generar_consultas_prueba.py +
   scripts/compare_hito1_hito2.py).

4) UMBRAL DINÁMICO: en vez de forzar siempre 5 resultados, descartamos los
   candidatos que quedan demasiado por debajo del mejor. Si no hay suficiente
   calidad, se devuelven menos resultados (prefiero pocos y buenos a 5 con
   "relleno").

Nota sobre las imágenes del catálogo: se leen con PIL (no con cv2.imread)
porque cv2.imread falla con rutas que contienen caracteres no-ASCII (p.ej.
la carpeta "Imágenes" del perfil de Windows), lo que dejaba score_color en 0.
"""

import os

import cv2
import numpy as np
from PIL import Image

from api.search_engine import DATADIR, search_similar

# ── PESOS DEL SCORE FINAL (probar, no asumir) ────────────────────────────
# Score_final = PESO_EMBEDDING*CLIP + PESO_COLOR_GLOBAL*color +
#               PESO_COLOR_FRENTE*frente + PESO_COLOR_ESPALDA*espalda +
#               PESO_ESTRUCTURA*estructura
PESO_EMBEDDING    = 0.55   # el embedding sigue mandando (es lo más informativo)
PESO_COLOR_GLOBAL = 0.15   # paleta global percibida por una persona
PESO_COLOR_FRENTE = 0.10   # región izquierda (frente en el banco)
PESO_COLOR_ESPALDA= 0.10   # región derecha (espalda en el banco)
PESO_ESTRUCTURA   = 0.10   # distribución del patrón en grises (robusto al color)

# Margen de corte dinámico: se descartan candidatos cuyo score_final quede
# más de este valor por debajo del mejor resultado
MARGEN_CORTE = 0.35

# Carpeta donde viven las imágenes reales del catálogo para el reranking.
# Hito 2 (integración Sala 4): los embeddings del motor se generan sobre las
# imágenes NORMALIZADAS de Sala 1 (data/images_normalized/), por lo que el
# color/estructura debe calcularse sobre la MISMA imagen que produjo el
# vector (coherencia entre el score de CLIP y los descriptores visuales).
CARPETA_IMAGENES = os.path.join(DATADIR, "images_normalized")

# Índice CLIP del Hito 2: generado por Sala 4 sobre data/images_normalized/
# (scripts/generar_indices_comparativos.py). Igual modelo que el Hito 1
# (openai/clip-vit-base-patch32), pero sobre el banco limpio, por lo que un
# query "sin marco" o preparado por Sala 2 encuentra mejor su diseño.
INDICE_NORMALIZADO = os.path.join(DATADIR, "embeddings_clip.npy")
IDS_NORMALIZADO = os.path.join(DATADIR, "ids.npy")

# Resolución de la comparación estructural (baja = robusta a detalles)
TAM_ESTRUCTURA = 32

# Cache de descriptores: cada imagen real se lee y procesa una sola vez por
# proceso. Con un catálogo fijo de 1000 imágenes esto evita re-leer el
# archivo en cada consulta y acelera mucho la evaluación con 50 queries.
_cache_descriptores = {}

# Cache del índice normalizado (Sala 4): (embeddings, ids, df_productos)
_indice_h2 = None


# ─────────────────────────────────────────────
# LECTURA Y DESCRIPTORES
# ─────────────────────────────────────────────

def _leer_bgr_desde_ruta(ruta):
    """
    Lee una imagen desde disco y la devuelve como arreglo BGR (formato de
    OpenCV). Usa PIL para tolerar rutas con caracteres no-ASCII, donde
    cv2.imread falla silenciosamente (devuelve None).
    """
    try:
        im = Image.open(ruta).convert("RGB")
    except Exception:
        return None
    return cv2.cvtColor(np.asarray(im), cv2.COLOR_RGB2BGR)


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
        return _leer_bgr_desde_ruta(str(imagen))

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


def _mitades_bgr(bgr):
    """Divide una imagen BGR en (izquierda, derecha) por la mitad del ancho."""
    if bgr is None or bgr.size == 0:
        return None, None
    w = bgr.shape[1]
    return bgr[:, : w // 2], bgr[:, w // 2 :]


def _estructura_gris(bgr):
    """
    Descriptor estructural: imagen en escala de grises redimensionada a
    TAM_ESTRUCTURA x TAM_ESTRUCTURA y normalizada a [0, 1]. Representa la
    distribución espacial del patrón independiente del color.
    """
    if bgr is None or bgr.size == 0:
        return None
    if bgr.ndim == 3:
        gris = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    else:
        gris = bgr
    gris = cv2.resize(gris, (TAM_ESTRUCTURA, TAM_ESTRUCTURA),
                      interpolation=cv2.INTER_AREA)
    return gris.astype(np.float32) / 255.0


def _correlacion_estructura(a, b):
    """
    Coeficiente de correlación de Pearson entre dos descriptores
    estructurales (1 = misma distribución del patrón). Si alguno es plano,
    no hay información: se devuelve 0.
    """
    if a is None or b is None:
        return 0.0
    fa = a.ravel()
    fb = b.ravel()
    if fa.std() < 1e-6 or fb.std() < 1e-6:
        return 0.0
    corr = float(np.corrcoef(fa, fb)[0, 1])
    return max(0.0, min(1.0, corr))


def _sim_color(a, b):
    """Similitud de histogramas HSV por correlación, recortada a [0, 1]."""
    if a is None or b is None:
        return 0.0
    sim = float(cv2.compareHist(a, b, cv2.HISTCMP_CORREL))
    return max(0.0, min(1.0, sim))


def _descriptores_de_archivo(nombre_archivo):
    """
    Lee la imagen real de un candidato desde CARPETA_IMAGENES y devuelve
    sus descriptores: (hist_global, hist_frente, hist_espalda, estructura).
    Usa cache para no re-leer el archivo en cada query. Devuelve None si la
    imagen no existe o no se puede abrir.
    """
    if nombre_archivo in _cache_descriptores:
        return _cache_descriptores[nombre_archivo]

    ruta = os.path.join(CARPETA_IMAGENES, str(nombre_archivo))
    bgr = _leer_bgr_desde_ruta(ruta)
    if bgr is None:
        _cache_descriptores[nombre_archivo] = None
        return None

    izq, der = _mitades_bgr(bgr)
    desc = {
        "hist_global": _histograma_hsv(bgr),
        "hist_frente": _histograma_hsv(izq),
        "hist_espalda": _histograma_hsv(der),
        "estructura": _estructura_gris(bgr),
    }
    _cache_descriptores[nombre_archivo] = desc
    return desc


# ─────────────────────────────────────────────
# MOTOR CON RERANKING
# ─────────────────────────────────────────────

def cargar_indice_normalizado():
    """
    Carga el índice CLIP del Hito 2 (Sala 4): data/embeddings_clip.npy +
    data/ids.npy alineados con data/products.csv. El vector de cada producto
    corresponde a su imagen NORMALIZADA (Sala 1). Devuelve None si el índice
    no existe (entonces el motor cae al índice del Hito 1).
    """
    global _indice_h2
    if _indice_h2 is not None:
        return _indice_h2
    if not os.path.exists(INDICE_NORMALIZADO):
        print("[search_engine_hito2] AVISO: no existe embeddings_clip.npy "
              "(Sala 4); usando el índice CLIP del Hito 1 (images_final).")
        return None

    import pandas as pd

    embeddings = np.load(INDICE_NORMALIZADO).astype(np.float32)
    normas = np.linalg.norm(embeddings, axis=1, keepdims=True)
    normas[normas == 0] = 1e-10
    embeddings = embeddings / normas

    ids = None
    if os.path.exists(IDS_NORMALIZADO):
        try:
            ids = np.load(IDS_NORMALIZADO, allow_pickle=True)
        except Exception:
            ids = None
    if ids is None or len(ids) != len(embeddings):
        csv_path = os.path.join(DATADIR, "products.csv")
        if os.path.exists(csv_path):
            df_csv = pd.read_csv(csv_path)
            ids = df_csv["id"].values
        else:
            ids = None
    if ids is None:
        raise ValueError(
            "No se pudo alinear embeddings_clip.npy con los IDs "
            "(falta ids.npy o products.csv)"
        )

    df = None
    csv_path = os.path.join(DATADIR, "products.csv")
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)

    _indice_h2 = (embeddings, np.asarray(ids), df)
    print(f"[search_engine_hito2] Índice normalizado de Sala 4 cargado: "
          f"{embeddings.shape[0]} productos x {embeddings.shape[1]} dims.")
    return _indice_h2


def buscar_en_indice_normalizado(query_embedding, top_k: int = 5) -> list[dict]:
    """
    Búsqueda por similitud coseno contra el índice CLIP del Hito 2
    (imágenes normalizadas, Sala 4). Contrato de respuesta idéntico al del
    Hito 1: id, nombre, imagen, url, proveedor, score.
    """
    indice = cargar_indice_normalizado()
    if indice is None:
        return search_similar(query_embedding, top_k=top_k)

    embeddings, ids, df = indice
    v_query = np.array(query_embedding, dtype=np.float32).flatten()
    if v_query.shape[0] != embeddings.shape[1]:
        raise ValueError(
            f"El vector de consulta tiene {v_query.shape[0]} dimensiones, "
            f"se esperaban {embeddings.shape[1]} (índice CLIP normalizado)"
        )
    norm_q = np.linalg.norm(v_query)
    if norm_q == 0:
        raise ValueError("El vector de consulta no puede ser un vector nulo")
    v_query = v_query / norm_q

    scores = np.dot(embeddings, v_query)
    top_idx = np.argsort(scores)[::-1][:top_k]

    resultados = []
    for idx in top_idx:
        row = {} if df is None else df.iloc[idx]
        resultados.append({
            "id": str(ids[idx]),
            "nombre": str(row.get("nombre_original", row.get("nombre", ""))),
            "imagen": str(row.get("imagen", "")),
            "url": str(row.get("url", "")),
            "proveedor": str(row.get("proveedor", "Designs Aimari")),
            "score": round(float(scores[idx]), 4),
        })
    return resultados


def search_similar_reranked(
    query_embedding,
    query_image,
    top_k: int = 5,
    candidatos_iniciales: int = 30,
) -> list[dict]:
    """
    Búsqueda visual con reranking (Hito 2).

    Paso 1: recuperación amplia contra el índice CLIP NORMALIZADO de Sala 4
    (data/embeddings_clip.npy sobre data/images_normalized/), pidiendo
    candidatos_iniciales en vez de top_k directo. Si el índice de Sala 4 no
    existe, cae al índice del Hito 1 (embeddings.npy).
    Paso 2: reranking ponderando el score de CLIP con los scores de color
    global, color por regiones (frente/espalda) y estructura del patrón.
    Paso 3: umbral dinámico que permite devolver menos de top_k resultados.

    Contrato de respuesta: list de objetos con las keys del Hito 1
    (id, nombre, imagen, url, proveedor, score) más:
      - score_inicial   : score de embeddings original (CLIP)
      - score_color     : componente de color ponderado (global+frente+espalda)
      - score_color_global / score_color_frente / score_color_espalda
      - score_estructura: similitud de distribución del patrón en grises
      - score_reranking : score_final ponderado
      - posicion_final  : rango final 1-indexado tras el reranking
      - modelo_utilizado: "clip+color_regiones+estructura"
    """
    # El índice se carga de forma diferida (buscar_en_indice_normalizado), y
    # el fallback al Hito 1 también (search_similar carga solo su índice).

    # ── Paso 1: RECUPERACIÓN AMPLIA ──────────────────────────────────────
    # Buscamos más candidatos de los que devolveremos para darle al
    # reranking la oportunidad de "resucitar" el diseño correcto si CLIP lo
    # dejó fuera del top 5. La búsqueda se hace contra el índice CLIP
    # NORMALIZADO (Sala 4, hito 2): los embeddings del banco limpio son
    # coherentes con los descriptores de color/estructura que se calculan
    # sobre images_normalized/.
    candidatos = buscar_en_indice_normalizado(query_embedding, top_k=candidatos_iniciales)

    # Descriptores de la consulta, calculados una sola vez
    bgr_consulta = _a_imagen_bgr(query_image)
    q_izq, q_der = _mitades_bgr(bgr_consulta)
    q_hist_global = _histograma_hsv(bgr_consulta)
    q_hist_frente = _histograma_hsv(q_izq)
    q_hist_espalda = _histograma_hsv(q_der)
    q_estructura = _estructura_gris(bgr_consulta)

    # ── Paso 2: RERANKING VISUAL ─────────────────────────────────────────
    reranked = []
    for cand in candidatos:
        # Score del Hito 1: similitud coseno de embeddings
        score_embedding = cand["score"]

        desc = _descriptores_de_archivo(cand["imagen"])
        # Si la imagen del candidato no se puede abrir, todos los scores
        # visuales quedan en 0: la búsqueda NO debe romperse por una sola
        # imagen defectuosa.
        if desc is not None:
            score_color_global = _sim_color(q_hist_global, desc["hist_global"])
            score_frente = _sim_color(q_hist_frente, desc["hist_frente"])
            score_espalda = _sim_color(q_hist_espalda, desc["hist_espalda"])
            score_estructura = _correlacion_estructura(q_estructura, desc["estructura"])
        else:
            score_color_global = 0.0
            score_frente = 0.0
            score_espalda = 0.0
            score_estructura = 0.0

        score_final = (
            PESO_EMBEDDING * score_embedding
            + PESO_COLOR_GLOBAL * score_color_global
            + PESO_COLOR_FRENTE * score_frente
            + PESO_COLOR_ESPALDA * score_espalda
            + PESO_ESTRUCTURA * score_estructura
        )

        # Componente de color agregado (para reportes y compatibilidad)
        score_color = (
            (PESO_COLOR_GLOBAL * score_color_global
             + PESO_COLOR_FRENTE * score_frente
             + PESO_COLOR_ESPALDA * score_espalda)
            / max(1e-9, PESO_COLOR_GLOBAL + PESO_COLOR_FRENTE + PESO_COLOR_ESPALDA)
        )

        reranked.append({
            **cand,
            "score_inicial": round(float(score_embedding), 4),
            "score_color_global": round(score_color_global, 4),
            "score_color_frente": round(score_frente, 4),
            "score_color_espalda": round(score_espalda, 4),
            "score_estructura": round(score_estructura, 4),
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
        r["modelo_utilizado"] = "clip+color_regiones+estructura"
        final.append(r)

    return final
