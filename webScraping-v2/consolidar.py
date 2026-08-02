import json
import os
import re
import shutil
import csv
from PIL import Image  # pip install pillow
 
# ============================================================
# CONFIGURACIÓN — AJUSTA ESTO SEGÚN TU PROYECTO
# ============================================================
 
# Fuente: designsaimari.com
PROVEEDOR_NOMBRE = "Designs Aimari"
PROVEEDOR_PREFIJO = "AIM"
 
# Rutas base (relativas a la carpeta donde corres el script)
RUTA_JSON = os.path.join("data", "productos.json")
RUTA_IMAGENES_ORIGEN = os.path.join("data", "images")
RUTA_IMAGENES_DESTINO = os.path.join("data", "images_final")  # carpeta final a entregar
RUTA_CSV_SALIDA = os.path.join("data", "consolidado.csv")
 
# ============================================================
# 1. CARGA DE DATOS
# ============================================================
 
def cargar_productos():
    """
    Lee productos.json y devuelve una lista de diccionarios normalizados.
 
    Estructura real de tu productos.json (confirmada):
    { "id": str, "numero": int, "nombre": str, "url": str, "archivo": str }
 
    Tu JSON NO trae el campo "pagina" (número de página del scraping).
    Por defecto se asigna PAGINA_POR_DEFECTO a todos los registros.
    Si tu scraper sí paginó (ej. 20 productos por página), ajusta la
    función `calcular_pagina()` más abajo para que la calcule según
    "numero" en vez de usar un valor fijo.
    """
    with open(RUTA_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
 
    productos = []
    for item in data:
        productos.append({
            "id_scraper": item.get("id"),
            "numero": item.get("numero"),
            "nombre_original": item.get("nombre"),
            "imagen_original": item.get("archivo"),
            "url": item.get("url") or "",
            "pagina": calcular_pagina(item.get("numero")),
        })
    return productos
 
 
# Confirmado en data/metadata.json: 60 productos por página (3 páginas -> 180 productos)
PAGINA_POR_DEFECTO = 1
PRODUCTOS_POR_PAGINA = 60
 
 
def calcular_pagina(numero):
    if PRODUCTOS_POR_PAGINA and numero:
        return ((numero - 1) // PRODUCTOS_POR_PAGINA) + 1
    return PAGINA_POR_DEFECTO
 
 
# ============================================================
# 2. VALIDACIONES
# ============================================================
 
def validar_imagen_abre(ruta_imagen):
    """Verifica que el archivo de imagen no esté corrupto y pueda abrirse."""
    try:
        with Image.open(ruta_imagen) as img:
            img.verify()
        return True
    except Exception:
        return False
 
 
def nomenclatura_valida(nombre_archivo):
    """
    Verifica que el nombre siga el patrón PROVEEDOR-Pxxx-xxx.ext
    Ejemplo válido: BUS-P001-001.jpg
    """
    patron = rf"^{PROVEEDOR_PREFIJO}-P\d{{3}}-\d{{3}}\.(jpg|jpeg|png|gif)$"
    return re.match(patron, nombre_archivo, re.IGNORECASE) is not None
 
 
def ejecutar_validaciones(registros, errores):
    """
    Corre todas las verificaciones pedidas por la sala sobre la lista final
    de registros ya con su nuevo nombre de imagen asignado.
    """
    nombres_vistos = set()
    urls_vistas = set()
 
    for r in registros:
        # a) Que cada imagen tenga nombre
        if not r["imagen"]:
            errores.append(f"[SIN NOMBRE] Registro {r['id']} no tiene imagen asignada.")
            continue
 
        # b) Duplicados (por nombre de imagen final o por URL)
        if r["imagen"] in nombres_vistos:
            errores.append(f"[DUPLICADO] La imagen '{r['imagen']}' está repetida.")
        nombres_vistos.add(r["imagen"])
 
        if r["url"] and r["url"] in urls_vistas:
            errores.append(f"[DUPLICADO] La URL '{r['url']}' está repetida.")
        urls_vistas.add(r["url"])
 
        # c) Nomenclatura
        if not nomenclatura_valida(r["imagen"]):
            errores.append(f"[NOMENCLATURA] '{r['imagen']}' no sigue el formato {PROVEEDOR_PREFIJO}-Pxxx-xxx.ext")
 
        # d) El archivo debe existir físicamente y poder abrirse
        ruta_final = os.path.join(RUTA_IMAGENES_DESTINO, r["imagen"])
        if not os.path.exists(ruta_final):
            errores.append(f"[NO EXISTE] No se encontró el archivo físico: {ruta_final}")
        elif not validar_imagen_abre(ruta_final):
            errores.append(f"[CORRUPTA] El archivo no se pudo abrir: {ruta_final}")
 
    return errores
 
 
# ============================================================
# 3. CONSOLIDACIÓN (renombrado + generación de IDs)
# ============================================================
 
def indexar_imagenes_por_numero():
    """
    Recorre data/images y arma un índice { numero: ruta_completa }.
    Se usa el número al inicio del archivo (ej. '21-Bélgica Concept.jpg' -> 21)
    en vez del nombre completo, porque los nombres con tildes/ñ pueden
    llegar dañados según cómo se haya comprimido/movido la carpeta
    (ej. al hacer zip en Windows). El número es el único dato 100% estable.
    """
    indice = {}
    patron = re.compile(r"^(\d+)-")
    for archivo in os.listdir(RUTA_IMAGENES_ORIGEN):
        m = patron.match(archivo)
        if m:
            indice[int(m.group(1))] = os.path.join(RUTA_IMAGENES_ORIGEN, archivo)
    return indice
 
 
def consolidar():
    productos = cargar_productos()
    os.makedirs(RUTA_IMAGENES_DESTINO, exist_ok=True)
    indice_imagenes = indexar_imagenes_por_numero()
 
    registros = []
    errores = []
    contador = 1
 
    for p in productos:
        numero = p.get("numero")
        origen = indice_imagenes.get(numero)
 
        if not origen or not os.path.exists(origen):
            errores.append(f"[ARCHIVO FALTANTE] No se encontró imagen para el producto #{numero} ('{p['nombre_original']}').")
            continue
 
        ext = os.path.splitext(p["imagen_original"])[1].lower()
        numero = f"{contador:03d}"
        pagina_str = f"P{int(p['pagina']):03d}"
        id_registro = f"{PROVEEDOR_PREFIJO}-{pagina_str}-{numero}"
        nombre_final = f"{id_registro}{ext}"
 
        destino = os.path.join(RUTA_IMAGENES_DESTINO, nombre_final)
        shutil.copyfile(origen, destino)
 
        registros.append({
            "id": id_registro,
            "proveedor": PROVEEDOR_NOMBRE,
            "pagina": p["pagina"],
            "imagen": nombre_final,
            "nombre_original": p["nombre_original"],
            "url": p["url"],
        })
 
        contador += 1
 
    # Validaciones finales sobre los registros ya generados
    ejecutar_validaciones(registros, errores)
 
    # Escribir el CSV final
    with open(RUTA_CSV_SALIDA, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "proveedor", "pagina", "imagen", "nombre_original", "url"])
        writer.writeheader()
        writer.writerows(registros)
 
    # Reporte final
    print(f"\n✅ Procesados: {len(registros)} registros")
    print(f"✅ CSV generado en: {RUTA_CSV_SALIDA}")
    print(f"✅ Imágenes finales en: {RUTA_IMAGENES_DESTINO}")
 
    if errores:
        print(f"\n⚠️  Se encontraron {len(errores)} problema(s):")
        for e in errores:
            print("  -", e)
    else:
        print("\n🎉 Ninguna validación falló. Todo consistente.")
 
    return registros, errores
 
 
if __name__ == "__main__":
    consolidar()