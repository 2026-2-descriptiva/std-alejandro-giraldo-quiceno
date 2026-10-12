from pathlib import Path
import re

import pandas as pd


def pregunta_01():
    """
    El archivo `data/clusters_report.txt` es un reporte de clústeres de
    palabras clave pensado para ser leído por una persona, no por un programa:
    los encabezados ocupan varias líneas, las columnas están alineadas con
    espacios y la lista de palabras clave de un clúster continúa en las líneas
    siguientes.

    Su tarea es convertir ese reporte en un DataFrame de Pandas con una fila
    por clúster y las columnas:

    - `cluster`: número del clúster, como entero.
    - `cantidad_de_palabras_clave`: como entero.
    - `porcentaje_de_palabras_clave`: como número decimal; por ejemplo, el
      texto `15,9 %` debe quedar como `15.9`.
    - `principales_palabras_clave`: todas las palabras clave del clúster en un
      solo texto, separadas por una coma y un único espacio.

    Retorne el DataFrame.

    Ejemplo del formato de la respuesta (se omite la última columna):

           cluster  cantidad_de_palabras_clave  porcentaje_de_palabras_clave
        0        1                         105                          15.9
        1        2                         102                          15.4
        ...
    """

    ruta_reporte = Path(__file__).resolve().parents[1] / "data" / "clusters_report.txt"
    patron_fila = re.compile(r"^\s*(\d+)\s+(\d+)\s+([\d,]+)\s*%\s+(.*)$")
    registros = []
    registro_actual = None

    with ruta_reporte.open(encoding="utf-8") as archivo:
        for linea in archivo:
            coincidencia = patron_fila.match(linea)
            if coincidencia:
                if registro_actual is not None:
                    registros.append(registro_actual)

                cluster, cantidad, porcentaje, palabras = coincidencia.groups()
                registro_actual = {
                    "cluster": int(cluster),
                    "cantidad_de_palabras_clave": int(cantidad),
                    "porcentaje_de_palabras_clave": float(
                        porcentaje.replace(",", ".")
                    ),
                    "fragmentos": [palabras.strip()],
                }
            elif registro_actual is not None and linea.strip():
                registro_actual["fragmentos"].append(linea.strip())

    if registro_actual is not None:
        registros.append(registro_actual)

    for registro in registros:
        texto = " ".join(" ".join(registro.pop("fragmentos")).split()).rstrip(".")
        palabras = [palabra.strip() for palabra in texto.split(",")]
        registro["principales_palabras_clave"] = ", ".join(palabras)

    return pd.DataFrame(
        registros,
        columns=[
            "cluster",
            "cantidad_de_palabras_clave",
            "porcentaje_de_palabras_clave",
            "principales_palabras_clave",
        ],
    )


if __name__ == "__main__":
    print(pregunta_01())
