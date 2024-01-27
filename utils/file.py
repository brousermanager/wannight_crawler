import csv
import pandas as pd


#   FUNZIONI TXT
def readTxt(fileName: str) -> list:
    with open(fileName) as file:
        return file.read().splitlines()


#   FUNZIONI CSV
def writeCsvRow(fileName: str, row: list) -> None:
    with open(fileName, mode='a', newline='', errors='ignore') as file:
        writer = csv.writer(file)
        writer.writerow(row)


def readCsv(fileName: str) -> list:
    res = []
    with open(fileName, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            res.append(row)
    res.pop(0)
    return res


def read_csv_row_by_row(file_path: str) -> list:
    res = []
    df = pd.read_csv(file_path, on_bad_lines=ignore_bad_lines,
                     engine='python', encoding='Windows-1252')
    for row in df.iterrows():
        res.append(row[1])
    return res


def ignore_bad_lines(line) -> None:
    return None
