import csv
import os


def pregunta_05():
    """
    Para cada letra de la primera columna (`letter`), encuentre el valor
    máximo y el valor mínimo de la segunda columna (`value`). Retorne una lista
    de tuplas `(letra, máximo, mínimo)` ordenada alfabéticamente por la letra.

    Ejemplo del formato de la respuesta:

        [("A", 9, 2), ("B", 9, 1), ...]
    """

    data_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data",
        "data.csv",
    )
    value_ranges = {}
    with open(data_path, newline="") as data_file:
        for row in csv.reader(data_file, delimiter="\t"):
            letter = row[0]
            value = int(row[1])
            if letter in value_ranges:
                value_ranges[letter][0] = max(value_ranges[letter][0], value)
                value_ranges[letter][1] = min(value_ranges[letter][1], value)
            else:
                value_ranges[letter] = [value, value]
    return [
        (letter, maximum, minimum)
        for letter, (maximum, minimum) in sorted(value_ranges.items())
    ]


if __name__ == "__main__":
    print(pregunta_05())
