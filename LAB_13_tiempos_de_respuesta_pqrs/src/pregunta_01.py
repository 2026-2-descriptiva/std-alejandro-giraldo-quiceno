import pandas as pd
from pathlib import Path


def pregunta_01() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Una entidad pública recibe peticiones, quejas, reclamos y sugerencias
    (PQRS) por dos canales, la página web y las cartas, y la ley le da 15 días
    hábiles para responder cada una. Su tarea es medir si la entidad cumple
    ese plazo.

    Los archivos `data/historical_requests_web.csv.gz` y
    `data/historical_requests_letter.csv.gz` tienen una fila por solicitud
    recibida entre 2016 y 2021 por cada canal, con su identificador
    (`record_id`), la fecha de entrada (`in_date`), el día de la semana de
    entrada (`day_name`) y la fecha de respuesta (`out_date`). Si `out_date`
    está vacía, la solicitud todavía no ha sido respondida.

    Tenga en cuenta lo siguiente:

    - Algunas solicitudes aparecen repetidas: elimine las filas idénticas
      dentro de cada canal, para contar cada solicitud una sola vez. Las
      filas sin `record_id` son solicitudes válidas.
    - Llame `letter` al canal de las cartas y `web` al de la página web.
    - Los días hábiles de respuesta son los días de lunes a viernes
      posteriores a la fecha de entrada, hasta la fecha de respuesta
      incluida. Por ejemplo, una solicitud que entra un viernes y se responde
      el lunes siguiente tardó 1 día hábil. No considere los festivos.
    - Los días calendario de respuesta son la diferencia entre la fecha de
      respuesta y la de entrada.
    - Una solicitud cumple el plazo si fue respondida en 15 días hábiles o
      menos. Una solicitud pendiente no ha cumplido el plazo.
    - `on_time_rate` es la proporción de solicitudes que cumplen el plazo,
      sobre el total de solicitudes, incluidas las pendientes.
    - Las medianas de días se calculan solamente con las solicitudes
      respondidas.

    Genere tres archivos en `submission/`, sin el índice de Pandas y con las
    columnas en el orden indicado:

    1. `channel_summary.csv`, con una fila por canal, en orden alfabético:
       `channel`, `requests`, `answered`, `pending`,
       `median_business_days` y `on_time_rate`.

    2. `yearly_summary.csv`, con una fila por año de entrada y canal,
       ordenada por año y luego por canal: `year`, `channel`, `requests`,
       `pending` y `on_time_rate`.

    3. `entry_day_summary.csv`, con una fila por día de entrada, de lunes a
       domingo, con los dos canales juntos: `day_name`, `requests`,
       `median_calendar_days` y `median_business_days`.

    Observe en el tercer archivo cómo cambia la lectura del tiempo de
    respuesta según se cuenten días calendario o días hábiles.

    La función también debe retornar las tres tablas, en el mismo orden.

    Ejemplo del formato de `channel_summary.csv`:

        channel,requests,answered,pending,median_business_days,on_time_rate
        letter,28138,...
        ...
    """

    carpeta_actividad = Path(__file__).resolve().parents[1]
    carpeta_datos = carpeta_actividad / "data"
    carpeta_entrega = carpeta_actividad / "submission"

    solicitudes_web = pd.read_csv(
        carpeta_datos / "historical_requests_web.csv.gz",
        compression="gzip",
        parse_dates=["in_date", "out_date"],
    ).drop_duplicates()
    solicitudes_carta = pd.read_csv(
        carpeta_datos / "historical_requests_letter.csv.gz",
        compression="gzip",
        parse_dates=["in_date", "out_date"],
    ).drop_duplicates()
    solicitudes_web["channel"] = "web"
    solicitudes_carta["channel"] = "letter"
    solicitudes = pd.concat(
        [solicitudes_carta, solicitudes_web],
        ignore_index=True,
    )

    solicitudes["entry_year"] = solicitudes["in_date"].dt.year
    solicitudes["day_name"] = solicitudes["in_date"].dt.day_name()

    mascara_respondidas = solicitudes["out_date"].notna()
    dias_transcurridos = (
        solicitudes.loc[mascara_respondidas, "out_date"]
        - solicitudes.loc[mascara_respondidas, "in_date"]
    ).dt.days
    dia_semana_entrada = solicitudes.loc[
        mascara_respondidas, "in_date"
    ].dt.weekday
    semanas_completas = dias_transcurridos // 7
    dias_restantes = dias_transcurridos % 7
    dias_habiles = semanas_completas * 5
    for desplazamiento in range(1, 7):
        dias_habiles += (
            (dias_restantes >= desplazamiento)
            & ((dia_semana_entrada + desplazamiento) % 7 < 5)
        ).astype("int64")

    solicitudes["calendar_days"] = pd.Series(
        pd.NA, index=solicitudes.index, dtype="Int64"
    )
    solicitudes["business_days"] = pd.Series(
        pd.NA, index=solicitudes.index, dtype="Int64"
    )
    solicitudes.loc[mascara_respondidas, "calendar_days"] = dias_transcurridos
    solicitudes.loc[mascara_respondidas, "business_days"] = dias_habiles
    solicitudes["on_time"] = (
        mascara_respondidas & solicitudes["business_days"].le(15).fillna(False)
    )

    def resumir(columnas_agrupacion, incluir_medianas=False):
        grupos = solicitudes.groupby(
            columnas_agrupacion,
            sort=True,
            dropna=False,
        )
        resumen = grupos.agg(
            requests=("record_id", "size"),
            answered=("out_date", "count"),
            pending=("out_date", lambda valores: int(valores.isna().sum())),
            on_time_rate=("on_time", "mean"),
        )
        if incluir_medianas:
            medianas = grupos[["calendar_days", "business_days"]].median()
            resumen = resumen.join(medianas)
        return resumen

    resumen_canales = resumir("channel", incluir_medianas=True).reset_index()
    resumen_canales = resumen_canales.rename(
        columns={
            "business_days": "median_business_days",
            "on_time_rate": "on_time_rate",
        }
    )[
        [
            "channel",
            "requests",
            "answered",
            "pending",
            "median_business_days",
            "on_time_rate",
        ]
    ]

    resumen_anual = (
        solicitudes.groupby(["entry_year", "channel"], sort=True)
        .agg(
            requests=("record_id", "size"),
            pending=("out_date", lambda valores: int(valores.isna().sum())),
            on_time_rate=("on_time", "mean"),
        )
        .reset_index()
        .rename(columns={"entry_year": "year"})
    )

    orden_dias = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    resumen_dias_entrada = (
        solicitudes.groupby("day_name", sort=False)
        .agg(
            requests=("record_id", "size"),
            median_calendar_days=("calendar_days", "median"),
            median_business_days=("business_days", "median"),
        )
        .reindex(orden_dias)
        .rename_axis("day_name")
        .reset_index()
    )

    carpeta_entrega.mkdir(parents=True, exist_ok=True)
    resumen_canales.to_csv(carpeta_entrega / "channel_summary.csv", index=False)
    resumen_anual.to_csv(carpeta_entrega / "yearly_summary.csv", index=False)
    resumen_dias_entrada.to_csv(
        carpeta_entrega / "entry_day_summary.csv",
        index=False,
    )

    return resumen_canales, resumen_anual, resumen_dias_entrada


if __name__ == "__main__":
    pregunta_01()
