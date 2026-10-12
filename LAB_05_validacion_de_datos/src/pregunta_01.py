import json
from pathlib import Path

import pandas as pd


def main():
    """
    Antes de limpiar o analizar un conjunto de datos, un analista debe
    documentar qué problemas tiene. En este laboratorio usted no va a limpiar
    `data/ventas.csv.gz`: va a construir un reporte de calidad que deje evidencia
    de sus problemas, tal como están en el archivo.

    Lea `data/ventas.csv.gz` sin modificar sus valores. Para trabajar con los
    encabezados, normalícelos: páselos a minúsculas, elimine los espacios al
    inicio y al final (y cualquier marca BOM) y reemplace los espacios
    internos por `_`. Las columnas requeridas son `supplier_id`, `supplier`,
    `country`, `city`, `purchase_date`, `amount`, `discount`, `weight`,
    `units`, `unit_price` y `contact_email`.

    Escriba el reporte en `submission/data_quality_report.json` con estas
    claves:

    - `row_count`: cantidad de filas de datos.
    - `column_count`: cantidad de columnas.
    - `missing_required_columns`: lista ordenada de columnas requeridas que no
      están en el archivo.
    - `unexpected_columns`: lista ordenada de columnas del archivo que no son
      requeridas.
    - `duplicate_row_count`: cantidad de filas idénticas a una fila anterior.
    - `duplicate_supplier_id_row_count`: cantidad de filas cuyo `supplier_id`
      aparece más de una vez (cuente todas esas filas, no solo las
      repetidas).
    - `missing_value_count_by_column`: diccionario con la cantidad de valores
      faltantes de cada columna. Considere faltantes las celdas vacías y las
      que contienen `N/A`.
    - `invalid_email_count`: cantidad de valores de `contact_email` que no
      tienen la forma `usuario@dominio.extension`.
    - `invalid_unit_count`: cantidad de valores numéricos de `units` que no son
      enteros positivos. Los valores faltantes no se cuentan aquí.
    - `country_values`: lista ordenada de los valores distintos de `country`,
      escritos exactamente como aparecen en el archivo.

    La función también debe retornar el reporte como un diccionario.

    Ejemplo del formato del reporte:

        {
          "row_count": 103,
          "column_count": 11,
          "missing_required_columns": [],
          ...
          "country_values": [" Colombia ", "CO", ...]
        }
    """

    activity_dir = Path(__file__).resolve().parents[1]
    data_file = activity_dir / "data" / "ventas.csv.gz"
    report_file = activity_dir / "submission" / "data_quality_report.json"

    df = pd.read_csv(
        data_file,
        compression="gzip",
        dtype=str,
        keep_default_na=False,
        encoding="utf-8-sig",
    )
    df.columns = [
        column.replace("\ufeff", "").strip().lower().replace(" ", "_")
        for column in df.columns
    ]

    required_columns = [
        "supplier_id",
        "supplier",
        "country",
        "city",
        "purchase_date",
        "amount",
        "discount",
        "weight",
        "units",
        "unit_price",
        "contact_email",
    ]

    def missing_values(values):
        stripped = values.str.strip()
        return stripped.eq("") | stripped.str.upper().eq("N/A")

    missing_required_columns = sorted(set(required_columns) - set(df.columns))
    unexpected_columns = sorted(set(df.columns) - set(required_columns))
    missing_value_count_by_column = {
        column: int(missing_values(df[column]).sum()) for column in df.columns
    }

    if "supplier_id" in df.columns:
        supplier_ids = df["supplier_id"]
        present_ids = supplier_ids.loc[~missing_values(supplier_ids)]
        duplicate_supplier_id_row_count = int(present_ids.duplicated(keep=False).sum())
    else:
        duplicate_supplier_id_row_count = 0

    if "contact_email" in df.columns:
        emails = df["contact_email"]
        email_is_missing = missing_values(emails)
        email_is_valid = emails.str.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+")
        invalid_email_count = int((~email_is_missing & ~email_is_valid).sum())
    else:
        invalid_email_count = 0

    if "units" in df.columns:
        units = df["units"]
        units_are_missing = missing_values(units)
        numeric_units = pd.to_numeric(units.where(~units_are_missing), errors="coerce")
        invalid_units = ~units_are_missing & (
            numeric_units.isna()
            | numeric_units.le(0)
            | numeric_units.mod(1).ne(0)
        )
        invalid_unit_count = int(invalid_units.sum())
    else:
        invalid_unit_count = 0

    if "country" in df.columns:
        country = df["country"]
        country_values = sorted(country.loc[~missing_values(country)].unique().tolist())
    else:
        country_values = []

    report = {
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "missing_required_columns": missing_required_columns,
        "unexpected_columns": unexpected_columns,
        "duplicate_row_count": int(df.duplicated().sum()),
        "duplicate_supplier_id_row_count": duplicate_supplier_id_row_count,
        "missing_value_count_by_column": missing_value_count_by_column,
        "invalid_email_count": invalid_email_count,
        "invalid_unit_count": invalid_unit_count,
        "country_values": country_values,
    }

    report_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return report


if __name__ == "__main__":
    main()
