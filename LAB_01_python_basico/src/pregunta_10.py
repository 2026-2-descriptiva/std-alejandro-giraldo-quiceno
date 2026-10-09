import csv
import os


def pregunta_10():
    """
    Para cada registro del archivo, en el mismo orden en que aparecen,
    retorne una tupla con la letra de la primera columna (`letter`), la
    cantidad de elementos de la cuarta columna (`codes`) y la cantidad de
    pares de la quinta columna (`metrics`). El resultado es una lista con una
    tupla por registro.

    Ejemplo del formato de la respuesta:

        [("E", 3, 5), ("A", 3, 4), ("B", 4, 4), ...]
    """

    data_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data",
        "data.csv",
    )
    result = []
    with open(data_path, newline="") as data_file:
        for row in csv.reader(data_file, delimiter="\t"):
            code_count = len(row[3].split(","))
            metric_count = len(row[4].split(","))
            result.append((row[0], code_count, metric_count))
    return result


if __name__ == "__main__":
    print(pregunta_10())
