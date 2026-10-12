from pathlib import Path

import pandas as pd


def pregunta_09():
    """
    Retorne la tabla `data/tbl0.tsv` completa con una columna adicional
    llamada `year`, al final, que contenga el año de la fecha de la columna
    `c3` como un texto de cuatro caracteres.

    Ejemplo del formato de la respuesta:

            c0 c1  c2          c3  year
        0    0  E   1  1999-02-28  1999
        1    1  A   2  1999-10-28  1999
        2    2  B   5  1998-05-02  1998
        ...
    """

    ruta_datos = Path(__file__).resolve().parents[1] / "data" / "tbl0.tsv"
    tabla = pd.read_csv(ruta_datos, sep="\t")
    tabla["year"] = tabla["c3"].str[:4]
    return tabla


if __name__ == "__main__":
    print(pregunta_09())
