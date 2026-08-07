# -*- coding: utf-8 -*-
"""
app.py - Interfaz Streamlit (Sala 2, contrato Hito 1 / rama sala-2-v2)
-----------------------------------------------------------------------
ESTA SALA NO GENERA EMBEDDINGS NI BUSCA LOCALMENTE.

Flujo unico del proyecto:
    Usuario sube imagen -> Streamlit -> POST /search/image (API Sala 3)
    -> la API genera el embedding con CLIP y busca en el indice unico
    -> devuelve Top 5 -> la interfaz muestra resultados y registra evaluacion

Correr (con la API de Sala 3 levantada en el puerto 8000):
    streamlit run app.py          # desde webScraping-v2/

La API de Sala 3 se levanta con:
    uvicorn api.main:app --port 8000   # desde webScraping-v2/
"""

import io
import os

import pandas as pd
import requests
import streamlit as st
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
IMAGES_DIR = os.path.join(DATA_DIR, "images_final")
EVAL_CSV = os.path.join(DATA_DIR, "evaluation.csv")

API_URL_DEFAULT = "http://localhost:8000"

CLASIFICACIONES = {
    "Correcto": "Correcto",
    "Util, pero no duplicado": "Util_no_duplicado",
    "Incorrecto": "Incorrecto",
}

st.set_page_config(page_title="Buscador visual de camisetas", layout="wide")


def api_url():
    return (st.session_state.get("api_url") or API_URL_DEFAULT).rstrip("/")


def llamar_api(url, archivo):
    """Envia la imagen a FastAPI y devuelve (ok, datos_o_error)."""
    try:
        resp = requests.post(
            f"{url}/search/image",
            files={"file": (archivo.name, archivo.getvalue(), archivo.type)},
            timeout=120,
        )
    except requests.exceptions.ConnectionError:
        return False, {"tipo": "servidor_no_disponible"}
    except requests.exceptions.Timeout:
        return False, {"tipo": "timeout"}

    if resp.status_code == 200:
        data = resp.json()
        if isinstance(data, list):
            data = {"resultados": data}
        return True, data
    if resp.status_code == 400:
        return False, {"tipo": "archivo_invalido", "detalle": resp.text}
    return False, {"tipo": "error", "detalle": resp.text}


def ruta_imagen_local(nombre_archivo):
    ruta = os.path.join(IMAGES_DIR, nombre_archivo)
    return ruta if os.path.exists(ruta) else None


def mostrar_resultado(rank, res, consulta):
    c1, c2 = st.columns([1, 2.2])
    with c1:
        local = ruta_imagen_local(res["imagen"])
        if local:
            st.image(local, use_container_width=True)
        else:
            st.image(res["url"], use_container_width=True)
    with c2:
        st.markdown(f"**#{rank} — {res['nombre']}**")
        st.markdown(f"`{res['id']}` · Proveedor: {res['proveedor']}")
        st.markdown(f"**Score de similitud:** `{res['score']:.4f}`")
        st.markdown(f"[Abrir imagen original]({res['url']})")
        clasificacion = st.radio(
            "¿El resultado es relevante?",
            list(CLASIFICACIONES.keys()),
            index=0,
            key=f"eval_{consulta}_{rank}",
            horizontal=True,
            label_visibility="visible",
        )
    st.divider()
    return {
        "consulta": consulta,
        "resultado_id": res["id"],
        "posicion": rank,
        "score": float(res["score"]),
        "clasificacion_humana": CLASIFICACIONES[clasificacion],
        "observacion": "",
    }


def guardar_evaluacion(filas):
    df_nuevo = pd.DataFrame(filas)
    if os.path.exists(EVAL_CSV):
        df_anterior = pd.read_csv(EVAL_CSV, encoding="utf-8")
        df_final = pd.concat([df_anterior, df_nuevo], ignore_index=True)
    else:
        df_final = df_nuevo
    df_final.to_csv(EVAL_CSV, index=False, encoding="utf-8")
    return df_final


def guardar_tiempo(consulta, tiempo_segundos):
    ruta = os.path.join(DATA_DIR, "tiempos.csv")
    fila = pd.DataFrame([{"consulta": consulta, "tiempo_segundos": float(tiempo_segundos)}])
    if os.path.exists(ruta):
        anterior = pd.read_csv(ruta, encoding="utf-8")
        fila = pd.concat([anterior, fila], ignore_index=True)
    fila.to_csv(ruta, index=False, encoding="utf-8")


def mostrar_metricas(df_eval):
    if df_eval.empty:
        st.info("Aun no hay evaluaciones guardadas.")
        return
    consultas = df_eval["consulta"].unique()
    n_top1 = 0
    n_util = 0
    for c in consultas:
        g = df_eval[df_eval["consulta"] == c]
        top1 = g[(g["posicion"] == 1) & (g["clasificacion_humana"] == "Correcto")]
        util = g[g["clasificacion_humana"] != "Incorrecto"]
        if not top1.empty:
            n_top1 += 1
        if not util.empty:
            n_util += 1
    n = len(consultas)
    c1, c2, c3 = st.columns(3)
    c1.metric("Consultas evaluadas", n)
    c2.metric("Top 1 correcto", f"{n_top1} de {n} ({n_top1 / n * 100:.0f}%)" if n else "0")
    c3.metric("Top 5 util (>=1 relevante)", f"{n_util} de {n} ({n_util / n * 100:.0f}%)" if n else "0")


st.title("Busqueda visual de camisetas")
st.caption("Una imagen se carga una sola vez, se procesa con un solo modelo, se compara "
           "contra un solo indice y los resultados se muestran en una sola interfaz.")

with st.sidebar:
    st.header("Conexion a la API")
    st.text_input("URL de la API (Sala 3)", value=API_URL_DEFAULT, key="api_url")
    if st.button("Ver estado del servidor", use_container_width=True):
        with st.spinner("Consultando /health..."):
            try:
                r = requests.get(f"{api_url()}/health", timeout=10)
                if r.status_code == 200:
                    d = r.json()
                    st.success(f"API OK · {d['products']} productos · {d['embeddings']} embeddings · {d['model']}")
                else:
                    st.error(f"API responde con estado {r.status_code}: {r.text}")
            except requests.exceptions.ConnectionError:
                st.error("El servidor no esta disponible. Ejecuta: uvicorn api.main:app --port 8000")

st.subheader("1. Sube la imagen de consulta")
archivo = st.file_uploader("Imagen (JPG, JPEG o PNG)", type=["jpg", "jpeg", "png"])

if archivo is None:
    st.stop()

consulta = archivo.name

col_q, col_r = st.columns([1, 2])
with col_q:
    st.subheader("Imagen consultada")
    st.image(Image.open(io.BytesIO(archivo.getvalue())), use_container_width=True)

with col_r:
    st.subheader("Resultados similares")

    if st.session_state.get("resultado_consulta") != consulta:
        st.session_state["resultado_consulta"] = consulta
        st.session_state["resultados"] = None
        st.session_state["error"] = None
        with st.spinner("Procesando imagen..."):
            ok, data = llamar_api(api_url(), archivo)
        if ok:
            st.session_state["resultados"] = data
            if data.get("tiempo_segundos") is not None:
                guardar_tiempo(consulta, data["tiempo_segundos"])
        else:
            st.session_state["error"] = data

    error = st.session_state.get("error")
    if error:
        tipo = error.get("tipo")
        if tipo == "servidor_no_disponible":
            st.error("El servidor no esta disponible. Verifica que la API de Sala 3 este corriendo.")
        elif tipo == "archivo_invalido":
            st.error("El archivo no es valido. Sube una imagen JPG, JPEG o PNG.")
        elif tipo == "timeout":
            st.error("La API tardo demasiado en responder. Reintenta.")
        else:
            st.error(f"Error del servidor: {error.get('detalle', tipo)}")
        st.stop()

    data = st.session_state.get("resultados")
    if data is None:
        st.info("No se encontraron resultados.")
        st.stop()

    res = data.get("resultados") or []
    if not res:
        st.info("No se encontraron resultados.")
        st.stop()

    filas = []
    for rank, r in enumerate(res, start=1):
        filas.append(mostrar_resultado(rank, r, consulta))

    observacion = st.text_area("Observacion sobre esta consulta (opcional)")
    if st.button("Guardar evaluacion de esta consulta", type="primary"):
        for f in filas:
            f["observacion"] = observacion
        df = guardar_evaluacion(filas)
        st.success(f"Evaluacion guardada en data/evaluation.csv (total {len(df)} registros)")

st.divider()
st.subheader("2. Metricas de las pruebas")
df_eval = None
if os.path.exists(EVAL_CSV):
    df_eval = pd.read_csv(EVAL_CSV, encoding="utf-8")
mostrar_metricas(df_eval if df_eval is not None else pd.DataFrame(columns=[
    "consulta", "resultado_id", "posicion", "score", "clasificacion_humana", "observacion"]))
