# -*- coding: utf-8 -*-
"""
compare_hito1_hito2.py
----------------------
SALA 3 - Hito 2: Comparación objetiva del motor Hito 1 vs Motor Hito 2.

Para cada consulta de la prueba integrada se envía la MISMA imagen a los dos
endpoints y se revisa si el id_correcto esperado quedó en Top1 y en Top5:

    - /search/image      -> Hito 1 (solo embeddings CLIP)
    - /search/image/v2   -> Hito 2 (CLIP + reranking por color/regiones/estructura)

Además mide el tiempo de cada consulta por motor (requisito: "Medición de
tiempos") y guarda la evidencia en:

    data/comparacion_hito1_hito2.csv   detalle por consulta (top1/top5/tiempos)
    data/comparacion_hito1_hito2.json  resumen agregado por motor y por categoría

CONSULTAS DE PRUEBA (evaluation/consultas_hito2.csv):
    Columnas: consulta, categoria, ruta_imagen, id_correcto
    Generado por scripts/generar_consultas_prueba.py con las categorías del
    Hito 2 (exacta, sin_marco, recoloreada, recortada, mockup_persona).
    Las filas que les faltan a otras salas se agregan al mismo CSV y este
    script las toma automáticamente (solo omite archivos inexistentes).

Requisitos:
    1) Tener la API corriendo localmente:  python -m uvicorn api.main:app --port 8000

Uso:
    python scripts/compare_hito1_hito2.py
    python scripts/compare_hito1_hito2.py --url http://localhost:8000
    python scripts/compare_hito1_hito2.py --solo hito2   # solo mide el motor nuevo
"""

import argparse
import csv
import json
import os
import sys
import time

import requests

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_URL = "http://localhost:8000"
CONSULTAS_CSV = os.path.join(BASE_DIR, "evaluation", "consultas_hito2.csv")
SALIDA_CSV = os.path.join(BASE_DIR, "data", "comparacion_hito1_hito2.csv")
SALIDA_JSON = os.path.join(BASE_DIR, "data", "comparacion_hito1_hito2.json")

ENDPOINT_H1 = "/search/image"
ENDPOINT_H2 = "/search/image/v2"

CATEGORIAS = ("exacta", "sin_marco", "recoloreada", "recortada", "mockup_persona")

# Conjunto de respaldo si no existe evaluation/consultas_hito2.csv
TEST_SET_FALLBACK = [
    (os.path.join("data", "images_final", "AIM-P001-001.jpg"), "AIM-P001-001"),
    (os.path.join("data", "images_final", "AIM-P001-002.jpg"), "AIM-P001-002"),
    (os.path.join("data", "images_final", "AIM-P001-003.jpg"), "AIM-P001-003"),
    (os.path.join("data", "images_final", "AIM-P001-004.jpg"), "AIM-P001-004"),
]


def cargar_consultas():
    """
    Carga (consulta, categoria, ruta, id_correcto) desde el CSV de la prueba
    integrada. Si el CSV no existe, usa TEST_SET_FALLBACK (categoría exacta).
    """
    if not os.path.exists(CONSULTAS_CSV):
        print(f"AVISO: no existe {CONSULTAS_CSV}; usando conjunto de respaldo.")
        return [
            {"consulta": os.path.basename(ruta), "categoria": "exacta",
             "ruta_imagen": ruta, "id_correcto": id_correcto}
            for ruta, id_correcto in TEST_SET_FALLBACK
        ]

    filas = []
    with open(CONSULTAS_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if not row.get("ruta_imagen"):
                continue
            filas.append({
                "consulta": row.get("consulta") or os.path.basename(row["ruta_imagen"]),
                "categoria": row.get("categoria", "exacta"),
                "ruta_imagen": os.path.join(BASE_DIR, row["ruta_imagen"]),
                "id_correcto": row.get("id_correcto", ""),
            })
    return filas


def _top_1_y_top_5(resultados, id_correcto):
    """Devuelve (top1_ok, top5_ok, id_top1) según la posición del id correcto."""
    top1_ok = False
    top5_ok = False
    id_top1 = ""
    if resultados:
        id_top1 = str(resultados[0].get("id", ""))
        top1_ok = id_top1 == str(id_correcto)
        top5_ok = any(str(r.get("id", "")) == str(id_correcto) for r in resultados)
    return top1_ok, top5_ok, id_top1


def _consultar(base_url, endpoint, ruta_imagen):
    """
    Hace POST de la imagen al endpoint y devuelve
    (resultados, tiempo_segundos, respuesta_http). Nunca lanza: ante un error
    del servidor devuelve ([], tiempo=0, respuesta con status != 200).
    """
    t0 = time.perf_counter()
    try:
        with open(ruta_imagen, "rb") as f:
            respuesta = requests.post(
                base_url + endpoint,
                files={"file": (os.path.basename(ruta_imagen), f)},
                timeout=180,
            )
    except requests.exceptions.ConnectionError:
        print("ERROR: no se puede conectar a", base_url)
        sys.exit(1)
    except requests.exceptions.Timeout:
        return [], round(time.perf_counter() - t0, 4), None

    tiempo = round(time.perf_counter() - t0, 4)
    if respuesta.status_code != 200:
        return [], tiempo, respuesta

    datos = respuesta.json()
    resultados = datos.get("resultados", [])
    if isinstance(datos, list):
        resultados = datos
    return resultados, tiempo, respuesta


def main():
    parser = argparse.ArgumentParser(description="Sala 3 - Comparación Hito 1 vs Hito 2")
    parser.add_argument("--url", default=DEFAULT_URL, help="URL base de la API")
    parser.add_argument("--solo", choices=["hito1", "hito2"], default=None,
                        help="Probar un solo motor (por defecto ambos)")
    args = parser.parse_args()

    consultas = cargar_consultas()
    if not consultas:
        print("Error: no hay consultas. Ejecutá scripts/generar_consultas_prueba.py")
        sys.exit(1)

    probar_h1 = args.solo in (None, "hito1")
    probar_h2 = args.solo in (None, "hito2")

    base = args.url.rstrip("/")
    filas = []
    omitidas = 0
    por_categoria = {}
    total = {"h1": {"top1": 0, "top5": 0, "n": 0, "tiempos": []},
             "h2": {"top1": 0, "top5": 0, "n": 0, "tiempos": []}}

    encabezado = ("consulta", "categoria", "id_correcto", "archivo",
                  "h1_top1", "h1_top5", "h1_tiempo_ms", "h1_mejor_id", "h1_n_resultados",
                  "h2_top1", "h2_top5", "h2_tiempo_ms", "h2_mejor_id", "h2_n_resultados")

    print("=" * 100)
    print("SALA 3 / HITO 2 - COMPARACION HITO 1 vs HITO 2 (mismas consultas)")
    print(f"Consultas cargadas: {len(consultas)}  |  API: {base}")
    print("=" * 100)

    for i, c in enumerate(consultas, start=1):
        ruta = c["ruta_imagen"]
        if not os.path.exists(ruta):
            omitidas += 1
            print(f"{i:3d}  [OMITIDA] {c['consulta']} (archivo no existe: {ruta})")
            continue

        fila = {
            "consulta": c["consulta"], "categoria": c["categoria"],
            "id_correcto": c["id_correcto"], "archivo": os.path.basename(ruta),
            "h1_top1": "-", "h1_top5": "-", "h1_tiempo_ms": "-", "h1_mejor_id": "-", "h1_n_resultados": "-",
            "h2_top1": "-", "h2_top5": "-", "h2_tiempo_ms": "-", "h2_mejor_id": "-", "h2_n_resultados": "-",
        }

        for motor, endpoint, probar in (("h1", ENDPOINT_H1, probar_h1),
                                        ("h2", ENDPOINT_H2, probar_h2)):
            if not probar:
                continue
            resultados, tiempo, resp = _consultar(base, endpoint, ruta)
            if resp is not None and resp.status_code != 200:
                print(f"{i:3d}  [{c['categoria']:12s}] {c['consulta']:<28s} {motor.upper()} error {resp.status_code}")
                continue
            top1_ok, top5_ok, id_top1 = _top_1_y_top_5(resultados, c["id_correcto"])
            fila[f"{motor}_top1"] = "SI" if top1_ok else "no"
            fila[f"{motor}_top5"] = "SI" if top5_ok else "no"
            fila[f"{motor}_tiempo_ms"] = round(tiempo * 1000, 1)
            fila[f"{motor}_mejor_id"] = id_top1
            fila[f"{motor}_n_resultados"] = len(resultados)

            total[motor]["top1"] += int(top1_ok)
            total[motor]["top5"] += int(top5_ok)
            total[motor]["n"] += 1
            total[motor]["tiempos"].append(tiempo)
            por_categoria.setdefault(c["categoria"], {"h1": [0, 0], "h2": [0, 0]})
            por_categoria[c["categoria"]][motor][0] += int(top1_ok)
            por_categoria[c["categoria"]][motor][1] += int(top5_ok)

        print(f"{i:3d}  [{c['categoria']:12s}] {c['consulta']:<28s} esperado={c['id_correcto']:<15s}"
              f" H1 top1={fila['h1_top1']:>2s}/top5={fila['h1_top5']:>2s} ({fila['h1_tiempo_ms']:>6} ms)"
              f"  H2 top1={fila['h2_top1']:>2s}/top5={fila['h2_top5']:>2s} ({fila['h2_tiempo_ms']:>6} ms)")
        filas.append([fila[k] for k in encabezado])

    # ── guardar evidencia CSV ──
    with open(SALIDA_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(encabezado)
        w.writerows(filas)

    # ── resumen ──
    print()
    print("=" * 100)
    print("RESUMEN AGREGADO")
    print("=" * 100)

    resumen = {"total_consultas": len(consultas), "omitidas": omitidas,
               "por_categoria": {}, "por_motor": {}}
    for motor, etiqueta in (("h1", "Hito 1 (CLIP)"), ("h2", "Hito 2 (CLIP+reranking)")):
        t = total[motor]
        n = max(1, t["n"])
        prom_ms = (sum(t["tiempos"]) / n * 1000) if t["tiempos"] else 0
        print(f"{etiqueta:<28s} Top1={t['top1']}/{t['n']} ({100*t['top1']/n:.1f}%)"
              f"  Top5={t['top5']}/{t['n']} ({100*t['top5']/n:.1f}%)"
              f"  tiempo prom={prom_ms:.0f} ms")
        resumen["por_motor"][motor] = {
            "top1": t["top1"], "top5": t["top5"], "n": t["n"],
            "tiempo_promedio_ms": round(prom_ms, 1),
        }

    print()
    print("Por categoría (Top1 / Top5):")
    for cat in CATEGORIAS:
        if cat not in por_categoria:
            continue
        d_h1, d_h2 = por_categoria[cat]["h1"], por_categoria[cat]["h2"]
        n_h1 = sum(1 for f in filas if f[1] == cat and f[4] != "-")
        n_h2 = sum(1 for f in filas if f[1] == cat and f[9] != "-")
        print(f"  {cat:<14s} H1: {d_h1[0]}/{n_h1} - {d_h1[1]}/{n_h1}   H2: {d_h2[0]}/{n_h2} - {d_h2[1]}/{n_h2}")
        resumen["por_categoria"][cat] = {
            "h1_top1": d_h1[0], "h1_top5": d_h1[1],
            "h2_top1": d_h2[0], "h2_top5": d_h2[1],
        }

    if probar_h1 and probar_h2 and total["h1"]["n"] and total["h2"]["n"]:
        delta_top1 = total["h2"]["top1"] - total["h1"]["top1"]
        delta_top5 = total["h2"]["top5"] - total["h1"]["top5"]
        print()
        print(f"Diferencia H2 - H1 en aciertos: Top1 = {delta_top1:+d}, Top5 = {delta_top5:+d}")

    with open(SALIDA_JSON, "w", encoding="utf-8") as f:
        json.dump(resumen, f, ensure_ascii=False, indent=2)

    print()
    print(f"Evidencia: {SALIDA_CSV}")
    print(f"Resumen  : {SALIDA_JSON}")


if __name__ == "__main__":
    main()
