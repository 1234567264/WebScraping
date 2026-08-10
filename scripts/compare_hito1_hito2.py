# -*- coding: utf-8 -*-
"""
compare_hito1_hito2.py
----------------------
SALA 4 - Hito 2: Comparación objetiva del motor Hito 1 vs Hito 2.

Para cada imagen de prueba manda la misma consulta a los dos endpoints y
revisa si el id_correcto esperado quedó en Top1 y en Top5:

    - /search/image      -> Hito 1 (solo embeddings CLIP)
    - /search/image/v2   -> Hito 2 (embeddings CLIP + reranking por color HSV)

Al final imprime la precisión agregada (Top1 y Top5) de cada motor.

Requisitos:
    1) Tener la API corriendo localmente:  uvicorn api.main:app --port 8000
    2) Completar TEST_SET con las 50 consultas del Hito 2.

Cómo completar TEST_SET:
    Cada entrada es una tupla (ruta_imagen, id_correcto_esperado).
    Las 50 consultas del Hito 2 se dividen en 5 categorías de 10:

        - 10 EXACTAS      : la misma imagen del catálogo (data/images_final/).
                           El id esperado es el que corresponde al archivo.
        - 10 SIN MARCO    : la imagen con el marco/blanco recortado.
        - 10 RECOLOREADAS : el mismo diseño con otros colores.
        - 10 RECORTADAS   : solo una zona del diseño (cercano al logo).
        - 10 MOCKUPS/PERSONAS: foto del diseño puesto en una persona.

    Los id correctos se obtienen del archivo data/products.csv (columna id).

Uso:
    python scripts/compare_hito1_hito2.py
"""

import os
import sys

import requests

# URL base de la API local (debe estar corriendo antes de ejecutar)
BASE_URL = "http://localhost:8000"

# ──────────────────────────────────────────────────────────────────────────
# TEST SET: COMPLETAR CON LAS 50 CONSULTAS DEL HITO 2
#
# EJEMPLOS ya cargados (consultas "exactas" sobre imágenes del catálogo,
# el id esperado es el que corresponde al archivo). Reemplazar/aumentar con
# las 10 + 10 + 10 + 10 + 10 consultas reales de la evaluación.
# ──────────────────────────────────────────────────────────────────────────
TEST_SET = [
    # ── 10 EXACTAS (misma imagen del catálogo) ──
    (os.path.join("data", "images_final", "AIM-P001-001.jpg"), "AIM-P001-001"),
    (os.path.join("data", "images_final", "AIM-P001-002.jpg"), "AIM-P001-002"),
    (os.path.join("data", "images_final", "AIM-P001-003.jpg"), "AIM-P001-003"),
    (os.path.join("data", "images_final", "AIM-P001-004.jpg"), "AIM-P001-004"),
    (os.path.join("data", "images_final", "AIM-P001-005.png"), "AIM-P001-005"),
    # ── 10 SIN MARCO: agregar aquí (ruta_imagen, id_correcto) ──
    # ── 10 RECOLOREADAS: agregar aquí ──
    # ── 10 RECORTADAS: agregar aquí ──
    # ── 10 MOCKUPS/PERSONAS: agregar aquí ──
]


def _top_1_y_top_5(resultados, id_correcto):
    """Devuelve (top1_ok, top5_ok) según la posición del id correcto."""
    top1_ok = False
    top5_ok = False
    if resultados:
        top1_ok = str(resultados[0].get("id", "")) == str(id_correcto)
        top5_ok = any(str(r.get("id", "")) == str(id_correcto) for r in resultados)
    return top1_ok, top5_ok


def _consultar(endpoint, ruta_imagen):
    """Hace POST de la imagen al endpoint y devuelve la lista de resultados."""
    with open(ruta_imagen, "rb") as f:
        respuesta = requests.post(
            BASE_URL + endpoint,
            files={"file": (os.path.basename(ruta_imagen), f)},
            timeout=120,
        )
    if respuesta.status_code != 200:
        return None, respuesta
    datos = respuesta.json()
    return datos.get("resultados", []), respuesta


def main():
    # Validar que el set de pruebas tenga entradas
    if not TEST_SET:
        print("Error: TEST_SET está vacío. Completá las 50 consultas del Hito 2.")
        sys.exit(1)

    resumen = {
        "h1": {"top1": 0, "top5": 0},
        "h2": {"top1": 0, "top5": 0},
    }

    print(f"{'#':<4}{'Imagen':<30}{'Esperado':<16}"
          f"{'H1_Top1':<9}{'H1_Top5':<9}{'H2_Top1':<9}{'H2_Top5':<9}")
    print("-" * 86)

    for i, (ruta, id_correcto) in enumerate(TEST_SET, start=1):
        if not os.path.exists(ruta):
            print(f"{i:<4}{os.path.basename(ruta):<30}NO EXISTE")
            continue

        nombre = os.path.basename(ruta)

        # Consulta al Hito 1
        resultados_h1, resp_h1 = _consultar("/search/image", ruta)
        # Consulta al Hito 2
        resultados_h2, resp_h2 = _consultar("/search/image/v2", ruta)

        # Si el endpoint respondió error, se marca como fallo de ese motor
        h1_top1 = h1_top5 = False
        h2_top1 = h2_top5 = False
        if resp_h1.status_code != 200:
            print(f"{i:<4}{nombre:<30}[H1 error {resp_h1.status_code}]")
        else:
            h1_top1, h1_top5 = _top_1_y_top_5(resultados_h1, id_correcto)
        if resp_h2.status_code != 200:
            print(f"{i:<4}{nombre:<30}[H2 error {resp_h2.status_code}]")
        else:
            h2_top1, h2_top5 = _top_1_y_top_5(resultados_h2, id_correcto)

        resumen["h1"]["top1"] += int(h1_top1)
        resumen["h1"]["top5"] += int(h1_top5)
        resumen["h2"]["top1"] += int(h2_top1)
        resumen["h2"]["top5"] += int(h2_top5)

        def marca(valor):
            return "SI" if valor else "no"

        print(f"{i:<4}{nombre:<30}{str(id_correcto):<16}"
              f"{marca(h1_top1):<9}{marca(h1_top5):<9}"
              f"{marca(h2_top1):<9}{marca(h2_top5):<9}")

    # ── Resumen agregado de precisión Top1 y Top5 ──
    total = len(TEST_SET)
    print("\n" + "=" * 86)
    print(f"RESUMEN (sobre {total} consultas válidas)")
    print("=" * 86)
    print(f"{'Método':<20}{'Precisión Top1':<18}{'Precisión Top5':<18}")
    print("-" * 56)
    print(f"{'Hito 1 (CLIP)':<20}"
          f"{(resumen['h1']['top1'] / total) * 100:<18.2f}"
          f"{(resumen['h1']['top5'] / total) * 100:<18.2f}")
    print(f"{'Hito 2 (CLIP+HSV)':<20}"
          f"{(resumen['h2']['top1'] / total) * 100:<18.2f}"
          f"{(resumen['h2']['top5'] / total) * 100:<18.2f}")

    # Diferencial para ver si el reranking mejoró la precisión
    delta_top1 = resumen["h2"]["top1"] - resumen["h1"]["top1"]
    delta_top5 = resumen["h2"]["top5"] - resumen["h1"]["top5"]
    print(f"\nDiferencia H2 - H1 en aciertos: Top1 = {delta_top1:+d}, Top5 = {delta_top5:+d}")


if __name__ == "__main__":
    main()
