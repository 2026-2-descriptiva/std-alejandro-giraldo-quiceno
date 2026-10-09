import csv
import os


def pregunta_06():
    """
    La quinta columna (`metrics`) contiene pares `clave:valor` separados por
    comas. Para cada clave, encuentre el valor mínimo y el valor máximo que
    aparecen en todo el archivo. Retorne una lista de tuplas
    `(clave, mínimo, máximo)` ordenada alfabéticamente por la clave.

    Observe que el orden es mínimo y luego máximo, al contrario de la
    pregunta 5.

    Ejemplo del formato de la respuesta:

        [("aaa", 1, 9), ("bbb", 1, 9), ...]
    """

    data_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data",
        "data.csv",
    )
    metric_ranges = {}
    with open(data_path, newline="") as data_file:
        for row in csv.reader(data_file, delimiter="\t"):
            for metric in row[4].split(","):
                key, value_text = metric.split(":")
                value = int(value_text)
                if key in metric_ranges:
                    metric_ranges[key][0] = min(metric_ranges[key][0], value)
                    metric_ranges[key][1] = max(metric_ranges[key][1], value)
                else:
                    metric_ranges[key] = [value, value]
    return [
        (key, minimum, maximum)
        for key, (minimum, maximum) in sorted(metric_ranges.items())
    ]


if __name__ == "__main__":
    print(pregunta_06())
