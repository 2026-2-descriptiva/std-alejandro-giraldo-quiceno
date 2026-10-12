from pathlib import Path

import pandas as pd


def pregunta_06():
    """
    Usando `data/tbl1.tsv`, obtenga los valores distintos de la columna `c4`,
    conviértalos a mayúsculas y retórnelos como una lista ordenada
    alfabéticamente.

    Ejemplo del formato de la respuesta:

        ["A", "B", "C", "D", "E", "F", "G"]
    """

    ruta_datos = Path(__file__).resolve().parents[1] / "data" / "tbl1.tsv"
    tabla = pd.read_csv(ruta_datos, sep="\t")
    return sorted(tabla["c4"].str.upper().unique().tolist())


if __name__ == "__main__":
    print(pregunta_06())
