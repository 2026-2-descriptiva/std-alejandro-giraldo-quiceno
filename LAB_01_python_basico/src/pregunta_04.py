import csv
import os


def pregunta_04():
    """
    Cuente cuántos registros hay en cada mes, usando la fecha de la tercera
    columna (`date`). Represente el mes como un texto de dos dígitos y retorne
    una lista de tuplas `(mes, cantidad)` ordenada por el mes.

    Ejemplo del formato de la respuesta:

        [("01", 3), ("02", 4), ("03", 2), ...]
    """

    data_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data",
        "data.csv",
    )
    counts = {}
    with open(data_path, newline="") as data_file:
        for row in csv.reader(data_file, delimiter="\t"):
            month = row[2].split("-")[1]
            counts[month] = counts.get(month, 0) + 1
    return sorted(counts.items())


if __name__ == "__main__":
    print(pregunta_04())
