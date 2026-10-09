import csv
import os


def pregunta_08():
    """
    Repita la pregunta 7, pero ahora cada lista de letras debe contener cada
    letra una sola vez y estar ordenada alfabéticamente. Retorne una lista de
    tuplas `(valor, letras)` ordenada por el valor.

    Ejemplo del formato de la respuesta:

        [(0, ["C"]), (1, ["B", "E"]), (2, ["A", "E"]), ...]
    """

    data_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data",
        "data.csv",
    )
    letters_by_value = {}
    with open(data_path, newline="") as data_file:
        for row in csv.reader(data_file, delimiter="\t"):
            value = int(row[1])
            letters_by_value.setdefault(value, set()).add(row[0])
    return [
        (value, sorted(letters))
        for value, letters in sorted(letters_by_value.items())
    ]


if __name__ == "__main__":
    print(pregunta_08())
