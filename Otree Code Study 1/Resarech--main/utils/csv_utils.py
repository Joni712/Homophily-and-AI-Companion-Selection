""" Generic utils to load trials from csv files

It is loaded into a list of dicts representing all loaded rows and columns as dicts' fields.
"""
import csv
from pathlib import Path


def read_csv(filepath, columns):
    """reads data from csv file

    Optionally, converts data to specified column types

    Example:
        POOL = read_csv("stimuli.csv", {'stimulus', 'response'})
        DATA = read_csv("data.csv", { 'response': str, 'response_time': float })

    Args:
        filepath: full path to the file to load
        columns: set of fields to load, or dict of { fld: type }

    Returns:
        list of dicts 
    """
    fields = {f: str for f in columns} if isinstance(columns, set) else dict(columns)

    def parse(row):
        return {f: t(row[f]) if row[f] is not None else None for f, t in fields.items()}

    with open(filepath, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, dialect="excel")

        headers = reader.fieldnames or []
        if not set(fields.keys()) <= set(headers):
            missing = set(fields.keys()) - set(headers)
            raise RuntimeError(f"missing fields in {filepath}: {missing}")

        return [parse(row) for row in reader]


def filter_data(data, **filters):
    def match(rec):
        return all(rec[key] == val for key, val in filters.items())
    return list(filter(match, data)) 
