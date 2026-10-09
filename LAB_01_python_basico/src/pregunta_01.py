import csv
import os


def pregunta_01():
    """
    Calcule la suma de los valores de la segunda columna (`value`) del
    archivo descomprimido `data/data.csv` y retorne el resultado como un
    número entero.

    Ejemplo del formato de la respuesta:

        214
    """

    data_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data",
        "data.csv",
    )
    with open(data_path, newline="") as data_file:
        return sum(int(row[1]) for row in csv.reader(data_file, delimiter="\t"))


if __name__ == "__main__":
    print(pregunta_01())