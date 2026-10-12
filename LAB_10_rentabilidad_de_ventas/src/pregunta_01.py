import pandas as pd
from pathlib import Path


def pregunta_01() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Una cadena de suministros de oficina vende mucho, pero la gerencia
    sospecha que parte de esas ventas no deja utilidad. El archivo
    `data/superstore_orders.csv.gz` tiene una fila por línea de pedido, con
    el número de pedido (`Order ID`), las ventas (`Sales`), la utilidad
    (`Profit`), el descuento aplicado (`Discount`, como proporción), el
    segmento del cliente (`Customer Segment`) y la categoría del producto
    (`Product Category`). Una utilidad negativa significa que la línea se
    vendió con pérdida.

    Use estas definiciones:

    - Margen (`profit_margin`): utilidad sobre ventas.
    - Línea con pérdida: una línea cuya utilidad es negativa.
    - `loss_line_rate`: la proporción de líneas con pérdida.
    - `lost_profit`: la suma de las pérdidas de las líneas con pérdida,
      escrita como número positivo.
    - Rango de descuento (`discount_band`): `0%` si no hubo descuento,
      `1%-5%` si fue mayor que 0 y hasta 5 %, `6%-10%` si fue mayor que 5 % y
      hasta 10 %, y `más de 10%` en otro caso.

    Genere tres archivos en `submission/`, sin el índice de Pandas y con las
    columnas en el orden indicado:

    1. `profitability_summary.csv`, con una sola fila: `lines` (cantidad de
       líneas), `orders` (pedidos distintos), `sales`, `profit`,
       `profit_margin`, `loss_lines` (cantidad de líneas con pérdida),
       `loss_line_rate` y `lost_profit`.

    2. `discount_summary.csv`, con una fila por rango de descuento, en el
       orden en que se definieron arriba: `discount_band`, `lines`, `sales`,
       `profit`, `profit_margin`, `loss_line_rate` y `lost_profit`.

    3. `priority_segments.csv`, con los cinco segmentos segmento–categoría
       que más utilidad pierden: `Customer Segment`, `Product Category`,
       `lines`, `sales`, `profit`, `profit_margin` y `lost_profit`. Considere
       solamente segmentos con al menos 100 líneas y ordénelos por
       `lost_profit` de mayor a menor.

    La función también debe retornar las tres tablas, en el mismo orden.

    Ejemplo del formato de `discount_summary.csv`:

        discount_band,lines,sales,profit,profit_margin,loss_line_rate,...
        0%,166,170539.05,29472.3789,0.1728,0.488,...
        ...
    """

    activity_dir = Path(__file__).resolve().parents[1]
    data_file = activity_dir / "data" / "superstore_orders.csv.gz"
    submission_dir = activity_dir / "submission"

    data = pd.read_csv(
        data_file,
        sep=";",
        decimal=",",
        compression="gzip",
    )
    loss_lines = data["Profit"] < 0
    data["is_loss"] = loss_lines
    data["line_lost_profit"] = (-data["Profit"]).where(loss_lines, 0)

    def summarize(grouped):
        summary = grouped.agg(
            lines=("Profit", "size"),
            sales=("Sales", "sum"),
            profit=("Profit", "sum"),
            loss_lines=("is_loss", "sum"),
            lost_profit=("line_lost_profit", "sum"),
        )
        summary["profit_margin"] = summary["profit"] / summary["sales"]
        summary["loss_line_rate"] = summary["loss_lines"] / summary["lines"]
        return summary

    overall = summarize(data.groupby(lambda _: 0, sort=False)).iloc[[0]]
    profitability_summary = pd.DataFrame(
        {
            "lines": [int(overall["lines"].iloc[0])],
            "orders": [int(data["Order ID"].nunique())],
            "sales": [overall["sales"].iloc[0]],
            "profit": [overall["profit"].iloc[0]],
            "profit_margin": [overall["profit_margin"].iloc[0]],
            "loss_lines": [int(overall["loss_lines"].iloc[0])],
            "loss_line_rate": [overall["loss_line_rate"].iloc[0]],
            "lost_profit": [overall["lost_profit"].iloc[0]],
        }
    )

    discount_labels = ["0%", "1%-5%", "6%-10%", "más de 10%"]
    discount_band = data["Discount"].map(
        lambda discount: (
            "0%"
            if discount == 0
            else "1%-5%"
            if 0 < discount <= 0.05
            else "6%-10%"
            if 0.05 < discount <= 0.10
            else "más de 10%"
        )
    )
    data["discount_band"] = pd.Categorical(
        discount_band,
        categories=discount_labels,
        ordered=True,
    )
    discount_summary = (
        summarize(data.groupby("discount_band", observed=False, sort=False))
        .reindex(discount_labels)
        .reset_index()
        .rename(columns={"discount_band": "discount_band"})
    )
    discount_summary = discount_summary[
        [
            "discount_band",
            "lines",
            "sales",
            "profit",
            "profit_margin",
            "loss_line_rate",
            "lost_profit",
        ]
    ]

    segment_summary = summarize(
        data.groupby(["Customer Segment", "Product Category"], sort=False)
    )
    segment_summary = segment_summary.loc[segment_summary["lines"] >= 100]
    segment_summary = segment_summary.sort_values(
        "lost_profit", ascending=False, kind="stable"
    ).head(5)
    priority_segments = segment_summary.reset_index()[
        [
            "Customer Segment",
            "Product Category",
            "lines",
            "sales",
            "profit",
            "profit_margin",
            "lost_profit",
        ]
    ]

    submission_dir.mkdir(parents=True, exist_ok=True)
    profitability_summary.to_csv(
        submission_dir / "profitability_summary.csv", index=False
    )
    discount_summary.to_csv(submission_dir / "discount_summary.csv", index=False)
    priority_segments.to_csv(submission_dir / "priority_segments.csv", index=False)

    return profitability_summary, discount_summary, priority_segments


if __name__ == "__main__":
    pregunta_01()
