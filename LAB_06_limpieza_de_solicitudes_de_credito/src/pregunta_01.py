from pathlib import Path
import unicodedata

import pandas as pd


def pregunta_01():
    """
    El archivo `data/solicitudes_de_credito.csv.gz` contiene las solicitudes de
    un programa de crédito, pero llegó sucio: tiene una columna de índice que
    no pertenece a los datos, registros duplicados, registros incompletos y
    valores que representan lo mismo escritos de formas distintas en los
    campos de texto, las fechas, el estrato y el monto.

    Su tarea es limpiarlo y guardar el resultado en
    `submission/solicitudes_de_credito.csv`, usando punto y coma (`;`) como
    separador y sin el índice de Pandas.

    El archivo limpio debe cumplir lo siguiente:

    - Contiene solamente las nueve columnas `sexo`, `tipo_de_emprendimiento`,
      `idea_negocio`, `barrio`, `estrato`, `comuna_ciudadano`,
      `fecha_de_beneficio`, `monto_del_credito` y `línea_credito`, en ese
      orden.
    - Los campos de texto están en minúsculas y sus palabras separadas por
      espacios.
    - `estrato` y `monto_del_credito` son números enteros, sin símbolos ni
      separadores de miles.
    - Todas las fechas de `fecha_de_beneficio` usan un mismo formato, por
      ejemplo `AAAA-MM-DD`.
    - No hay registros incompletos. La única excepción es
      `comuna_ciudadano`: sus valores faltantes son parte de los datos
      originales y deben conservarse.
    - No hay registros duplicados.

    Ejemplo del formato del archivo:

        sexo;tipo_de_emprendimiento;idea_negocio;barrio;estrato;...
        femenino;comercio;almacen de ropa en;los cerros el vergel;2;...
        ...
    """

    carpeta_actividad = Path(__file__).resolve().parents[1]
    ruta_datos = carpeta_actividad / "data" / "solicitudes_de_credito.csv.gz"
    df = pd.read_csv(ruta_datos, sep=";", index_col=0)

    columnas_texto = [
        "sexo",
        "tipo_de_emprendimiento",
        "idea_negocio",
        "barrio",
        "línea_credito",
    ]
    for columna in columnas_texto:
        df[columna] = (
            df[columna]
            .str.lower()
            .str.replace(r"[-_]", " ", regex=True)
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
        )

    df["estrato"] = df["estrato"].astype(int)

    df["monto_del_credito"] = (
        df["monto_del_credito"]
        .astype(str)
        .str.strip()
        .str.replace(r"\.00$", "", regex=True)
        .str.replace(r"[^0-9]", "", regex=True)
        .astype(int)
    )

    fechas = df["fecha_de_beneficio"].astype(str).str.strip()
    df["fecha_de_beneficio"] = pd.to_datetime(
        fechas, format="%d/%m/%Y", errors="coerce"
    ).fillna(pd.to_datetime(fechas, format="%Y/%m/%d", errors="coerce"))
    df["fecha_de_beneficio"] = df["fecha_de_beneficio"].dt.strftime("%Y-%m-%d")

    df["comuna_ciudadano"] = df["comuna_ciudadano"].astype("Int64")

    columnas_obligatorias = [c for c in df.columns if c != "comuna_ciudadano"]
    df = df.dropna(subset=columnas_obligatorias)
    df = df.drop_duplicates()

    salida = carpeta_actividad / "submission"
    salida.mkdir(parents=True, exist_ok=True)
    df.to_csv(salida / "solicitudes_de_credito.csv", sep=";", index=False)


if __name__ == "__main__":
    pregunta_01()
