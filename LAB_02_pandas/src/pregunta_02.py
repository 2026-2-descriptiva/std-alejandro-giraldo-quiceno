from pathlib import Path

import pandas as pd


def pregunta_02():
    """
    ¿Cuántas columnas tiene la tabla `data/tbl0.tsv`? Retorne la cantidad
    como un número entero.

    Ejemplo del formato de la respuesta:

        4
    """

    ruta_datos = Path(__file__).resolve().parents[1] / "data" / "tbl0.tsv"
    tabla = pd.read_csv(ruta_datos, sep="\t")
    return int(tabla.shape[1])


if __name__ == "__main__":
    print(pregunta_02())
