import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


def build_cohort_analysis() -> pd.DataFrame:
    """
    Una tienda quiere saber si sus clientes vuelven a comprar después de su
    primera compra. Para responder, agrupe a los clientes en cohortes según
    el mes de su primera compra y mida, mes a mes, qué proporción de cada
    cohorte vuelve a comprar. Use `data/sales.csv.gz`, que tiene una fila por
    orden con su cliente (`CustomerID`) y su fecha (`OrderDate`).

    Use estas definiciones:

    - `cohort_month`: el mes de la primera compra del cliente, escrito como
      `AAAA-MM`.
    - `period_index`: los meses transcurridos desde `cohort_month`; es 0 en el
      mes de la primera compra, 1 en el mes siguiente, y así sucesivamente.
    - `active_customers`: la cantidad de clientes distintos de la cohorte que
      compraron en ese período.
    - `cohort_size`: la cantidad de clientes de la cohorte, es decir, sus
      clientes activos en el período 0.
    - `retention_rate`: `active_customers` sobre `cohort_size`.

    Genere dos archivos en `submission/`:

    1. `cohort_retention.csv`, sin el índice de Pandas, con las columnas
       `cohort_month`, `period_index`, `active_customers`, `cohort_size` y
       `retention_rate`, y una fila por cada combinación cohorte–período
       observada, ordenadas por cohorte y período.

    2. `cohort_retention_heatmap.png`, un mapa de calor de `retention_rate`
       con una fila por cohorte (eje vertical) y una columna por período
       (eje horizontal). Muestre los valores como porcentajes. Los períodos
       que todavía no se pueden observar para una cohorte no significan
       retención cero: déjelos vacíos en el mapa.

    La función también debe retornar la tabla de retención.

    Ejemplo del formato de `cohort_retention.csv`:

        cohort_month,period_index,active_customers,cohort_size,retention_rate
        2022-01,0,100,100,1.0
        2022-01,1,26,100,0.26
        ...
    """

    activity_dir = Path(__file__).resolve().parents[1]
    data_file = activity_dir / "data" / "sales.csv.gz"
    submission_dir = activity_dir / "submission"
    submission_dir.mkdir(parents=True, exist_ok=True)

    orders = pd.read_csv(data_file, compression="gzip")
    orders["OrderDate"] = pd.to_datetime(orders["OrderDate"])
    orders["order_month"] = orders["OrderDate"].dt.to_period("M")
    first_purchase = orders.groupby("CustomerID")["order_month"].min()
    orders["cohort_month"] = orders["CustomerID"].map(first_purchase)
    orders["period_index"] = (
        (orders["order_month"].dt.year - orders["cohort_month"].dt.year) * 12
        + orders["order_month"].dt.month
        - orders["cohort_month"].dt.month
    )

    cohort_sizes = first_purchase.groupby(first_purchase).size().rename("cohort_size")
    retention = (
        orders.groupby(["cohort_month", "period_index"])["CustomerID"]
        .nunique()
        .rename("active_customers")
        .reset_index()
    )
    retention["cohort_month"] = retention["cohort_month"].astype(str)
    retention["cohort_size"] = retention["cohort_month"].map(
        cohort_sizes.rename(index=str)
    )
    retention["retention_rate"] = (
        retention["active_customers"] / retention["cohort_size"]
    )
    retention = retention[
        [
            "cohort_month",
            "period_index",
            "active_customers",
            "cohort_size",
            "retention_rate",
        ]
    ].sort_values(["cohort_month", "period_index"], ignore_index=True)

    retention.to_csv(submission_dir / "cohort_retention.csv", index=False)

    heatmap = retention.pivot(
        index="cohort_month",
        columns="period_index",
        values="retention_rate",
    )
    figure, axis = plt.subplots(
        figsize=(max(8, heatmap.shape[1] * 1.1), max(4, heatmap.shape[0] * 0.65))
    )
    image = axis.imshow(
        heatmap,
        aspect="auto",
        interpolation="none",
        cmap="YlGnBu",
        vmin=0,
        vmax=1,
    )
    image.cmap.set_bad("white")
    axis.set_xticks(range(len(heatmap.columns)), heatmap.columns)
    axis.set_yticks(range(len(heatmap.index)), heatmap.index)
    axis.set_xlabel("Período desde la primera compra (meses)")
    axis.set_ylabel("Cohorte de primera compra")
    axis.set_title("Retención de clientes por cohorte")
    for row_index in range(heatmap.shape[0]):
        for column_index in range(heatmap.shape[1]):
            value = heatmap.iloc[row_index, column_index]
            if pd.notna(value):
                axis.text(
                    column_index,
                    row_index,
                    f"{value:.0%}",
                    ha="center",
                    va="center",
                    color="black",
                    fontsize=8,
                )
    figure.colorbar(image, ax=axis, label="Retención")
    figure.tight_layout()
    figure.savefig(submission_dir / "cohort_retention_heatmap.png", dpi=150)
    plt.close(figure)
    return retention


if __name__ == "__main__":
    build_cohort_analysis()
