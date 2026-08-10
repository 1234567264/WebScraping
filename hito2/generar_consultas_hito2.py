# -*- coding: utf-8 -*-
"""
generar_consultas_hito2.py (Sala 2 - Hito 2)
---------------------------------------------
Genera el conjunto comun de 50 consultas de prueba para el Hito 2.

Estructura:
    10 disenos del banco (diversos)
      x 5 versiones por diseno = 50 consultas

    versiones:
      exacta      -> imagen original del banco
      sin_marco   -> recorte del contenido (se elimina el marco fino)
      recoloreada -> rotacion de matiz + saturacion + brillo
      recortada   -> recorte central al ~55% (patron parcial)
      persona     -> mockup: camiseta sobre una persona sintetica con fondo

Cada consulta tiene su diseno correcto conocido (correcto_id = id del banco).

Salida:
    evaluation/hito2/consultas/<archivo>.jpg
    evaluation/hito2/consultas.csv   (manifiesto: archivo, categoria, correcto_id)

Uso:
    python evaluation/hito2/generar_consultas_hito2.py
"""

import os
import random
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance


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
IMG_SRC = os.path.join(BASE_DIR, "data", "images_final")
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "consultas")
MANIFEST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "consultas.csv")

SIZE = 320
SEED = 42

PATRONES = [
    "AIM-P001-001", "AIM-P001-010", "AIM-P001-025", "AIM-P001-040", "AIM-P001-055",
    "AIM-P002-101", "AIM-P010-550", "AIM-P004-201", "AIM-P006-301", "AIM-P016-901",
]


def contenido_box(arr, thr=0.15):
    """Bounding box de la zona con contenido (descarta marcos/bordes planos)."""
    h, w = arr.shape[:2]
    a = arr.astype(np.float32)
    rowstd = a.std(axis=(1, 2))
    colstd = a.std(axis=(0, 2))
    ys = np.where(rowstd > thr * rowstd.max())[0]
    xs = np.where(colstd > thr * colstd.max())[0]
    y1, y2 = (int(ys.min()), int(ys.max())) if len(ys) else (0, h)
    x1, x2 = (int(xs.min()), int(xs.max())) if len(xs) else (0, w)
    m = 5
    return (max(0, x1 - m), max(0, y1 - m), min(w, x2 + m), min(h, y2 + m))


def recolor(im, hue=60, sat=1.6, bri=1.15):
    im = ImageEnhance.Color(im).enhance(sat)
    im = ImageEnhance.Brightness(im).enhance(bri)
    arr = np.asarray(im.convert("RGB"))
    if hue:
        arr_hsv = np.asarray(im.convert("HSV"), dtype=np.int16)
        arr_hsv[:, :, 0] = (arr_hsv[:, :, 0] + hue) % 180
        im = Image.fromarray(arr_hsv.astype(np.uint8), "HSV").convert("RGB")
    return im


def recorte_central(im, frac=0.55):
    w, h = im.size
    nw, nh = int(w * frac), int(h * frac)
    x1, y1 = (w - nw) // 2, (h - nh) // 2
    return im.crop((x1, y1, x1 + nw, y1 + nh))


def persona(im_shirt):
    """Mockup: camiseta sobre una persona sintetica con fondo (pared + piso)."""
    rng = random.Random(SEED)
    try:
        import cv2
        arr = np.asarray(im_shirt.convert("RGB"))
        h, w = arr.shape[:2]
        M = cv2.getRotationMatrix2D((w / 2, h / 2), rng.uniform(-7, 7), 0.95)
        warped = cv2.warpAffine(arr, M, (w, h), borderValue=(220, 220, 220))
        camisa = Image.fromarray(warped)
    except Exception:
        camisa = im_shirt

    canvas = Image.new("RGB", (SIZE, SIZE))
    d = ImageDraw.Draw(canvas)

    for y in range(SIZE):
        t = y / SIZE
        color = (int(120 + 60 * t), int(150 + 40 * t), int(190 + 20 * t))
        d.line([(0, y), (SIZE, y)], fill=color)
    for y in range(int(SIZE * 0.82), SIZE):
        d.line([(0, y), (SIZE, y)], fill=(60, 55, 50))

    cx = SIZE // 2
    torso = (cx - 85, 95, cx + 85, 275)
    cabeza = (cx - 35, 35, cx + 35, 110)
    brazo_i = (cx - 110, 110, cx - 85, 245)
    brazo_d = (cx + 85, 110, cx + 110, 245)
    piernas = (cx - 70, 275, cx + 70, SIZE)
    piel = (235, 195, 160)

    d.ellipse(cabeza, fill=piel)
    d.rectangle(brazo_i, fill=piel)
    d.rectangle(brazo_d, fill=piel)
    d.rectangle(piernas, fill=(40, 60, 110))

    camisa = camisa.resize((170, 180), Image.LANCZOS)
    mascara = Image.new("L", camisa.size, 0)
    dm = ImageDraw.Draw(mascara)
    dm.rounded_rectangle([(0, 0), (170, 180)], radius=22, fill=255)
    canvas.paste(camisa, (torso[0], torso[1]), mascara)
    d.ellipse((torso[0] + 10, 95, torso[2] - 10, 120), fill=piel)
    return canvas


def _buscar_fuente(patron):
    """Localiza la imagen del patron en IMG_SRC tolerando extensiones."""
    for ext in (".jpg", ".jpeg", ".png", ".gif"):
        ruta = os.path.join(IMG_SRC, patron + ext)
        if os.path.exists(ruta):
            return ruta
    return None


def main():
    random.seed(SEED)
    os.makedirs(OUT_DIR, exist_ok=True)

    fuentes = []
    for p in PATRONES:
        ruta = _buscar_fuente(p)
        if ruta is not None:
            fuentes.append(ruta)
        else:
            print("SKIP fuente:", p)
    if len(fuentes) < 10:
        print(f"AVISO: solo {len(fuentes)} fuentes disponibles")

    filas = []
    for i, ruta in enumerate(fuentes, start=1):
        correcto_id = os.path.basename(ruta)[:-4]
        im = Image.open(ruta).convert("RGB")

        versiones = {
            "exacta": im,
            "sin_marco": im.crop(contenido_box(np.asarray(im))),
            "recoloreada": recolor(im),
            "recortada": recorte_central(im),
            "persona": persona(im.crop(contenido_box(np.asarray(im)))),
        }
        for cat, vim in versiones.items():
            archivo = f"c{i:02d}_{cat}.jpg"
            vim.convert("RGB").save(os.path.join(OUT_DIR, archivo), "JPEG", quality=92)
            filas.append((archivo, cat, correcto_id, ruta))
            print("OK", archivo, correcto_id)

    with open(MANIFEST, "w", encoding="utf-8") as f:
        f.write("archivo,categoria,correcto_id,fuente\n")
        for archivo, cat, cid, src in filas:
            f.write(f"{archivo},{cat},{cid},{os.path.basename(src)}\n")

    print(f"\nListo: {len(filas)} consultas en {OUT_DIR}")
    print(f"Manifiesto: {MANIFEST}")


if __name__ == "__main__":
    sys.exit(main())
