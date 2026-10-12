import json
from pathlib import Path

import pandas as pd


def pregunta_01():
    """
    Una aseguradora quiere publicar datos de sus afiliados para que un grupo
    de investigación estudie el costo de los seguros, sin que nadie pueda
    reconocer a una persona. El archivo `data/insurance.csv.gz` tiene una fila
    por afiliado con su edad (`age`), sexo (`sex`), índice de masa corporal
    (`bmi`), número de hijos (`children`), si fuma (`smoker`), región
    (`region`) y el costo de su seguro (`charges`).

    El archivo no tiene nombres ni documentos, pero eso no basta: la edad, el
    sexo, el índice de masa corporal, el número de hijos y la región son
    cuasi-identificadores, porque combinados pueden señalar a una persona.
    `smoker` es el atributo sensible que se quiere proteger.

    En este laboratorio usted va a medir el riesgo de reidentificación y a
    decidir qué publicar. Use estas definiciones:

    - Una clase de equivalencia es un grupo de registros con los mismos
      valores en todos los cuasi-identificadores. Un conjunto de datos cumple
      k-anonimato si toda clase tiene al menos k registros. Use k = 5.
    - `age_group`: `18-29`, `30-39`, `40-49` o `50-64`.
    - `bmi_group`: `bajo peso` (menos de 18.5), `normal` (desde 18.5 y menos
      de 25), `sobrepeso` (desde 25 y menos de 30) u `obesidad` (30 o más).
    - `children_group`: `0`, `1-2` o `3+`.

    Evalúe dos esquemas de generalización:

    - `with_children`: `age_group`, `sex`, `bmi_group`, `children_group` y
      `region`.
    - `without_children`: `age_group`, `sex`, `bmi_group` y `region`; el
      número de hijos no se publica.

    En cada esquema, suprima (no publique) los registros de las clases con
    menos de 5 registros. Luego, entre las clases publicadas, identifique las
    que no tienen diversidad en el atributo sensible, es decir, aquellas en
    las que todos los afiliados fuman o ninguno fuma: en esas clases, saber
    que alguien pertenece a ellas revela si fuma.

    Escriba `submission/privacy_report.json` con estas claves:

    - `original_k`: el menor tamaño de clase usando los cuasi-identificadores
      originales, sin generalizar.
    - `original_unique_records`: cuántos registros son los únicos de su clase
      con los cuasi-identificadores originales.
    - `schemes`: un diccionario con una entrada por esquema (`with_children` y
      `without_children`), cada una con las claves `quasi_identifiers` (la
      lista de columnas del esquema), `equivalence_classes` (clases antes de
      suprimir), `k_before_suppression`, `suppressed_records`,
      `published_records`, `published_classes`,
      `classes_without_smoker_diversity` y
      `records_without_smoker_diversity`.
    - `selected_scheme`: el esquema que suprime menos registros.
    - `mean_charges_original` y `mean_charges_published`: el costo promedio
      de todos los afiliados y el de los registros publicados con el esquema
      seleccionado.
    - `smoker_rate_original` y `smoker_rate_published`: la proporción de
      fumadores en ambos casos.

    Escriba también `submission/insurance_published.csv`, sin el índice de
    Pandas, con los registros publicados del esquema seleccionado, en el
    mismo orden del archivo original, y las columnas del esquema seguidas de
    `smoker` y `charges`.

    La función también debe retornar el reporte como un diccionario.

    Ejemplo del formato del reporte:

        {
          "original_k": 1,
          "original_unique_records": 1330,
          "schemes": {
            "with_children": {
              "quasi_identifiers": ["age_group", "sex", ...],
              "equivalence_classes": 278,
              ...
            },
            ...
          },
          ...
        }
    """

    activity_dir = Path(__file__).resolve().parents[1]
    data_file = activity_dir / "data" / "insurance.csv.gz"
    submission_dir = activity_dir / "submission"
    report_file = submission_dir / "privacy_report.json"
    published_file = submission_dir / "insurance_published.csv"

    data = pd.read_csv(data_file, compression="gzip")
    original_quasi_identifiers = ["age", "sex", "bmi", "children", "region"]
    original_class_sizes = data.groupby(
        original_quasi_identifiers, dropna=False, observed=True
    ).size()

    data["age_group"] = pd.cut(
        data["age"],
        bins=[18, 30, 40, 50, 65],
        labels=["18-29", "30-39", "40-49", "50-64"],
        right=False,
    )
    data["bmi_group"] = pd.cut(
        data["bmi"],
        bins=[float("-inf"), 18.5, 25, 30, float("inf")],
        labels=["bajo peso", "normal", "sobrepeso", "obesidad"],
        right=False,
    )
    data["children_group"] = data["children"].map(
        lambda count: "0" if count == 0 else "1-2" if count <= 2 else "3+"
    )

    schemes = {
        "with_children": [
            "age_group",
            "sex",
            "bmi_group",
            "children_group",
            "region",
        ],
        "without_children": ["age_group", "sex", "bmi_group", "region"],
    }

    scheme_results = {}
    published_by_scheme = {}
    for scheme_name, quasi_identifiers in schemes.items():
        class_sizes = data.groupby(
            quasi_identifiers, dropna=False, observed=True
        ).size()
        row_class_sizes = data.groupby(
            quasi_identifiers, dropna=False, observed=True
        ).transform("size")
        published_mask = row_class_sizes >= 5
        published = data.loc[published_mask].copy()
        published_by_scheme[scheme_name] = published

        published_diversity = published.groupby(
            quasi_identifiers, dropna=False, observed=True
        )["smoker"].nunique()
        classes_without_diversity = published_diversity[
            published_diversity <= 1
        ].index
        if len(classes_without_diversity):
            class_index = pd.MultiIndex.from_frame(published[quasi_identifiers])
            without_diversity_mask = class_index.isin(classes_without_diversity)
            records_without_diversity = int(without_diversity_mask.sum())
        else:
            records_without_diversity = 0

        scheme_results[scheme_name] = {
            "quasi_identifiers": quasi_identifiers,
            "equivalence_classes": int(len(class_sizes)),
            "k_before_suppression": int(class_sizes.min()),
            "suppressed_records": int(len(data) - len(published)),
            "published_records": int(len(published)),
            "published_classes": int(len(published_diversity)),
            "classes_without_smoker_diversity": int(
                (published_diversity <= 1).sum()
            ),
            "records_without_smoker_diversity": records_without_diversity,
        }

    selected_scheme = min(
        schemes,
        key=lambda name: scheme_results[name]["suppressed_records"],
    )
    selected_columns = schemes[selected_scheme]
    published = published_by_scheme[selected_scheme]

    report = {
        "original_k": int(original_class_sizes.min()),
        "original_unique_records": int((original_class_sizes == 1).sum()),
        "schemes": scheme_results,
        "selected_scheme": selected_scheme,
        "mean_charges_original": float(data["charges"].mean()),
        "mean_charges_published": float(published["charges"].mean()),
        "smoker_rate_original": float(data["smoker"].eq("yes").mean()),
        "smoker_rate_published": float(published["smoker"].eq("yes").mean()),
    }

    submission_dir.mkdir(parents=True, exist_ok=True)
    report_file.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    published[selected_columns + ["smoker", "charges"]].to_csv(
        published_file,
        index=False,
    )
    return report


if __name__ == "__main__":
    pregunta_01()
