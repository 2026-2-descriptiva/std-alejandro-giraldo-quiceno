import csv
import os


def pregunta_12():
    """
    Para cada letra de la primera columna (`letter`), sume todos los valores
    numéricos de los pares `clave:valor` de la quinta columna (`metrics`).
    Retorne un diccionario `{letra: suma}` con las letras en orden alfabético.

    Ejemplo del formato de la respuesta:

        {"A": 177, "B": 187, "C": 114, ...}
    """

    data_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data",
        "data.csv",
    )
    totals = {}
    with open(data_path, newline="") as data_file:
        for row in csv.reader(data_file, delimiter="\t"):
            letter = row[0]
            metric_total = sum(
                int(metric.split(":")[1]) for metric in row[4].split(",")
            )
            totals[letter] = totals.get(letter, 0) + metric_total
    return dict(sorted(totals.items()))


if __name__ == "__main__":
    print(pregunta_12())
