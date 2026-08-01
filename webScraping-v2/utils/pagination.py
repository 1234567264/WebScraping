from utils.helpers import leer_metadata


def convertir_paginas(valor):
    """
    Convierte el argumento --paginas en una lista de páginas.

    Ejemplos:
    "25"      -> [1,2,3,...,25]
    "1,3,5"   -> [1,3,5]
    "2-10"    -> [2,3,4,5,6,7,8,9,10]
    """

    if valor == "all":
        raise Exception("El modo all todavía no está implementado...")

    paginas = set()

    partes = valor.split(",")

    for parte in partes:

        parte = parte.strip()

        # Caso rango: 2-10
        if "-" in parte:

            inicio, fin = parte.split("-")

            inicio = int(inicio)
            fin = int(fin)

            paginas.update(
                range(inicio, fin + 1)
            )

        # Caso número: 25
        else:

            numero = int(parte)

            # Un número significa desde 1 hasta ese número
            paginas.update(
                range(1, numero + 1)
            )


    return sorted(paginas)



def obtener_inicio_pagina(pagina):
    """
    Calcula el número global inicial del producto
    usando metadata real.

    Ejemplo:
    página 3:
    página 1 = 60
    página 2 = 60

    inicio = 121
    """

    metadata = leer_metadata()

    paginas_metadata = metadata["paginas"]

    total = 0


    for numero_pagina in range(1, pagina):

        datos = paginas_metadata.get(
            str(numero_pagina)
        )

        if datos is None:
            raise Exception(
                f"Falta metadata de página {numero_pagina}"
            )


        total += datos["cantidad"]


    return total + 1



def obtener_paginas_faltantes(paginas):
    """
    Revisa qué páginas no existen todavía
    en metadata.
    """

    metadata = leer_metadata()

    paginas_existentes = metadata["paginas"]

    faltantes = []


    for pagina in paginas:

        if str(pagina) not in paginas_existentes:

            faltantes.append(pagina)


    return faltantes



def obtener_maxima_pagina(paginas):
    return max(paginas)

# =============================
def obtener_paginas_hasta_maximo(paginas):

    """
    Devuelve todas las páginas necesarias
    desde 1 hasta la mayor solicitada.

    Ejemplo:

    [25]
    retorna:
    [1,2,3,...25]

    [2,5]
    retorna:
    [1,2,3,4,5]
    """

    maxima = max(paginas)

    return list(range(1, maxima + 1))

# ============================
def obtener_paginas_sin_metadata(paginas):
    metadata = leer_metadata()
    existentes = metadata["paginas"]
    faltantes = []

    for pagina in paginas:

        if str(pagina) not in existentes:

            faltantes.append(pagina)
            
    return faltantes