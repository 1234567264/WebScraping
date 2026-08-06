# -*- coding: utf-8 -*-
"""
app.py - Interfaz Streamlit (Sala 2)
--------------------------------------
Sube una imagen -> muestra las 5 imagenes mas parecidas de la base de datos
(nombre, URL, score) -> permite marcar cada resultado como correcto/incorrecto
-> guarda la evaluacion en data/evaluacion.csv

Correr con:
    streamlit run app.py
"""

import json
import os
from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")
IMAGES_DIR = os.path.join(DATA_DIR, "images")
INDEX_EMB = os.path.join(DATA_DIR, "index_embeddings.npy")
INDEX_META = os.path.join(DATA_DIR, "index_metadata.json")
EVAL_CSV = os.path.join(DATA_DIR, "evaluacion.csv")

st.set_page_config(page_title="Buscador de estampados similares", layout="wide")


@st.cache_resource
def cargar_modelo():
    return SentenceTransformer("clip-ViT-B-32")


@st.cache_data
def cargar_indice():
    embeddings = np.load(INDEX_EMB)
    with open(INDEX_META, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    return embeddings, metadata


def guardar_evaluacion(filas):
    df_nuevo = pd.DataFrame(filas)
    if os.path.exists(EVAL_CSV):
        df_existente = pd.read_csv(EVAL_CSV)
        df_final = pd.concat([df_existente, df_nuevo], ignore_index=True)
    else:
        df_final = df_nuevo
    df_final.to_csv(EVAL_CSV, index=False)


st.title("🔍 Buscador de estampados similares")
st.caption("Sube una imagen y encuentra los 5 diseños más parecidos en la base de datos")

# st.write("Directorio actual:", os.getcwd())
# st.write("INDEX_EMB:", INDEX_EMB)
# st.write("INDEX_META:", INDEX_META)
# st.write("Existe EMB:", os.path.exists(INDEX_EMB))
# st.write("Existe META:", os.path.exists(INDEX_META))

if not os.path.exists(INDEX_EMB) or not os.path.exists(INDEX_META):
    st.error("No se encontró el índice todavía.")
    st.code("python build_index.py", language="bash")
    st.stop()

model = cargar_modelo()
embeddings, metadata = cargar_indice()

archivo_subido = st.file_uploader("Sube una imagen de consulta", type=["jpg", "jpeg", "png", "webp"])

if archivo_subido:
    col_izq, col_der = st.columns([1, 2])

    imagen_consulta = Image.open(archivo_subido).convert("RGB")
    with col_izq:
        st.subheader("Imagen consultada")
        st.image(imagen_consulta, use_container_width=True)

    emb_consulta = model.encode(imagen_consulta).reshape(1, -1)
    similitudes = cosine_similarity(emb_consulta, embeddings)[0]
    sorted_indices = np.argsort(similitudes)[::-1]
    
    top5_idx = []
    nombres_vistos = set()
    for idx in sorted_indices:
        nombre_completo = metadata[idx]["nombre"]
        base_nombre = nombre_completo.split(" (Variante")[0].strip()
        
        if base_nombre not in nombres_vistos:
            nombres_vistos.add(base_nombre)
            top5_idx.append(idx)
            
        if len(top5_idx) >= 5:
            break

    with col_der:
        st.subheader("Top 5 resultados similares")

        resultados_marcados = []
        for rank, idx in enumerate(top5_idx, start=1):
            item = metadata[idx]
            score = float(similitudes[idx])
            ruta_local = os.path.join(IMAGES_DIR, item["archivo"])

            c1, c2 = st.columns([1, 2])
            with c1:
                if os.path.exists(ruta_local):
                    st.image(ruta_local, use_container_width=True)
                else:
                    st.warning("Imagen local no encontrada")
            with c2:
                st.markdown(f"**#{rank} — {item['nombre']}**")
                st.markdown(f"URL: {item['url']}")
                st.markdown(f"Score: `{score:.4f}`")
                correcto = st.radio(
                    f"¿Resultado #{rank} correcto?",
                    ["Correcto", "Incorrecto"],
                    key=f"eval_{rank}_{archivo_subido.name}",
                    horizontal=True,
                )
                resultados_marcados.append({
                    "rank": rank,
                    "nombre": item["nombre"],
                    "url": item["url"],
                    "score": score,
                    "correcto": correcto == "Correcto",
                })
            st.divider()

        observacion = st.text_area("Observación sobre esta consulta (opcional)")

        if st.button("💾 Guardar evaluación de esta consulta"):
            filas = []
            for r in resultados_marcados:
                filas.append({
                    "timestamp": datetime.now().isoformat(timespec="seconds"),
                    "consulta": archivo_subido.name,
                    "rank": r["rank"],
                    "nombre_resultado": r["nombre"],
                    "url_resultado": r["url"],
                    "score": r["score"],
                    "correcto": r["correcto"],
                    "observacion": observacion,
                })
            guardar_evaluacion(filas)
            st.success("Evaluación guardada en data/evaluacion.csv ✅")
