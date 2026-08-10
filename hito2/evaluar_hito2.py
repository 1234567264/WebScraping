# -*- coding: utf-8 -*-
"""
evaluar_hito2.py (Sala 2 - Hito 2)
-----------------------------------
Compara el motor Hito 1 (consulta original) contra el motor Hito 2
(consulta preparada por preprocesar_consulta) sobre las 50 consultas
del conjunto comun.

Para cada consulta:
    - embedding de la imagen original  -> ranking (motor Hito 1)
    - preprocesamiento + embedding de la imagen preparada -> ranking (motor Hito 2)
    - se verifica si el diseno correcto quedo en Top 1 y Top 5
    - se miden los tiempos

Salidas:
    evaluation/hito2/resultados_hito2.csv  (una fila por consulta)
    evaluation/hito2/resumen_hito2.txt     (metricas agregadas)

Uso (desde webScraping-v2/, con la venv activa):
    python evaluation/hito2/evaluar_hito2.py
"""

import os
import sys
import time

import numpy as np
import pandas as pd

# Resolucion adaptativa de rutas:
#   - en la copia de trabajo de Sala 2 el proyecto vive en webScraping-v2/
#     y este script corre desde webScraping-v2/evaluation/hito2/;
#   - en el repositorio principal el modulo vive en api/ y los resultados
#     viven en <raiz>/hito2/.
def _localizar_repo():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidatos = [
        os.path.join(script_dir, "..", ".."),       # copia Sala 2: webScraping-v2/evaluation/hito2/
        os.path.join(script_dir, ".."),             # repositorio principal: <raiz>/hito2/
    ]
    for c in candidatos:
        c = os.path.abspath(c)
        if os.path.isdir(os.path.join(c, "data")):
            return c
    return os.path.abspath(candidatos[-1])


BASE_DIR = _localizar_repo()
if os.path.basename(BASE_DIR) == "webScraping-v2":
    sys.path.insert(0, BASE_DIR)
    from preprocesar_consulta import preparar_consulta
else:
    sys.path.insert(0, BASE_DIR)
    from api.preprocesar_consulta import preparar_consulta

from api.search_engine import cargar_indice, search_similar

_H2_EVAL = os.path.join(BASE_DIR, "evaluation", "hito2")
H2_DIR = _H2_EVAL if os.path.isdir(_H2_EVAL) else os.path.join(BASE_DIR, "hito2")
CONSULTAS = os.path.join(H2_DIR, "consultas")
MANIFEST = os.path.join(H2_DIR, "consultas.csv")
SALIDA_CSV = os.path.join(H2_DIR, "resultados_hito2.csv")
SALIDA_TXT = os.path.join(H2_DIR, "resumen_hito2.txt")


def main():
    df = pd.read_csv(MANIFEST)
    print(f"Consultas a evaluar: {len(df)}")

    cargar_indice()
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("clip-ViT-B-32")

    filas = []
    tiempos_proc = []
    tiempos_orig = []
    tiempos_prep = []

    for idx, row in df.iterrows():
        archivo = os.path.join(CONSULTAS, row["archivo"])
        from PIL import Image
        imagen = Image.open(archivo).convert("RGB")
        correcto = row["correcto_id"]

        t0 = time.time()
        emb_orig = model.encode(imagen)
        res_orig = search_similar(emb_orig, top_k=5)
        t_orig = time.time() - t0

        t0 = time.time()
        prep = preparar_consulta(imagen)
        emb_proc = model.encode(prep["procesada"])
        res_proc = search_similar(emb_proc, top_k=5)
        t_proc = time.time() - t0

        ids_orig = [r["id"] for r in res_orig]
        ids_proc = [r["id"] for r in res_proc]

        filas.append({
            "archivo": row["archivo"],
            "categoria": row["categoria"],
            "correcto_id": correcto,
            "top1_original": ids_orig[0],
            "top1_original_score": res_orig[0]["score"],
            "top5_original": "|".join(ids_orig),
            "hit1_original": ids_orig[0] == correcto,
            "hit5_original": correcto in ids_orig,
            "top1_procesada": ids_proc[0],
            "top1_procesada_score": res_proc[0]["score"],
            "top5_procesada": "|".join(ids_proc),
            "hit1_procesada": ids_proc[0] == correcto,
            "hit5_procesada": correcto in ids_proc,
            "recorte_pct": prep["recorte_pct"],
            "pasos": ";".join(prep["pasos"]),
            "tiempo_original_s": round(t_orig, 3),
            "tiempo_procesada_s": round(t_proc, 3),
            "tiempo_preprocesado_s": prep["tiempo_segundos"],
        })
        tiempos_orig.append(t_orig)
        tiempos_proc.append(t_proc)
        tiempos_prep.append(prep["tiempo_segundos"])
        print(f"[{idx+1}/{len(df)}] {row['archivo']} | O1={ids_orig[0] != correcto} P1={ids_proc[0] != correcto}")

    res = pd.DataFrame(filas)
    res.to_csv(SALIDA_CSV, index=False, encoding="utf-8")

    def top5(regla, r):
        if regla == "score":
            usar = "top5_procesada" if r.top1_procesada_score > r.top1_original_score else "top5_original"
        elif regla == "recorte":
            usar = "top5_procesada" if r.recorte_pct < 0.95 else "top5_original"
        elif regla == "procesada":
            usar = "top5_procesada"
        else:
            usar = "top5_original"
        return getattr(r, usar).split("|")

    def top1(regla, r):
        if regla == "score":
            return r.top1_procesada if r.top1_procesada_score > r.top1_original_score else r.top1_original
        if regla == "recorte":
            return r.top1_procesada if r.recorte_pct < 0.95 else r.top1_original
        if regla == "procesada":
            return r.top1_procesada
        return r.top1_original

    def metrica(regla):
        t1 = int(sum(top1(regla, r) == r.correcto_id for r in res.itertuples()))
        t5 = int(sum(r.correcto_id in top5(regla, r) for r in res.itertuples()))
        return t1, t5

    lineas = []
    lineas.append("RESUMEN HITO 2 - SALA 2 (50 consultas comunes)")
    lineas.append("")
    lineas.append(f"Total consultas evaluadas: {len(res)}")
    lineas.append("")
    lineas.append(f"{'Regla':<34}{'Top1':>10}{'Top5':>10}")
    for nombre, regla in [
        ("Hito 1 (siempre original)", "original"),
        ("Hito 2 (siempre procesada)", "procesada"),
        ("Hito 2 auto: mayor score top1", "score"),
        ("Hito 2 auto: recorte < 0.95", "recorte"),
    ]:
        t1, t5 = metrica(regla)
        lineas.append(f"{nombre:<34}{t1:>7}/{len(res)}{t5:>7}/{len(res)}")
    lineas.append("")

    for nombre, regla in [("score", "score"), ("recorte", "recorte")]:
        res[f"auto_{regla}"] = res.apply(lambda r: top1(regla, r), axis=1)

    lineas.append("Por categoria (Hito 1 -> Hito 2 procesada):")
    lineas.append(f"{'Categoria':<14}{'n':>4}{'Top1 H1':>10}{'Top1 H2':>10}{'Top5 H1':>10}{'Top5 H2':>10}")
    for cat, g in res.groupby("categoria"):
        lineas.append(f"{cat:<14}{len(g):>4}{100*g['hit1_original'].mean():>9.0f}%{100*g['hit1_procesada'].mean():>10.0f}%{100*g['hit5_original'].mean():>9.0f}%{100*g['hit5_procesada'].mean():>10.0f}%")
    lineas.append("")
    lineas.append(f"Tiempo promedio de busqueda (original):  {np.mean(tiempos_orig):.2f}s")
    lineas.append(f"Tiempo promedio de busqueda (preparada):  {np.mean(tiempos_proc):.2f}s")
    lineas.append(f"Tiempo promedio de preprocesamiento:      {np.mean(tiempos_prep):.2f}s")
    lineas.append(f"Tiempo total de las 50 consultas:         {sum(tiempos_proc):.1f}s")
    lineas.append("")

    with open(SALIDA_TXT, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas))
    print("\n".join(lineas))


if __name__ == "__main__":
    main()
