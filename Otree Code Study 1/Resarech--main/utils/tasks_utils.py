"""Tools to manipulate tasks"""

import random
from dataclasses import dataclass

from utils.csv_utils import read_csv


@dataclass
class Task:
    """A record for a task"""

    question: str
    options: list  # of { label, value }
    correct: str


def read(filepath):
    """load raw data for tasks"""
    return read_csv(filepath, {"section", "question", "A", "B", "C", "D", "correct"})


def select(data, /, section, seed=None) -> list:
    """create tasks records from data for specified section
    randomizes order and options according to seed
    """
    tasks = [
        Task(
            datum["question"],
            [
                dict(value="A", label=datum["A"]),
                dict(value="B", label=datum["B"]),
                dict(value="C", label=datum["C"]),
                dict(value="D", label=datum["D"]),
            ],
            datum["correct"],
        )
        for datum in data
        if datum["section"] == section
    ]
    random.seed(seed)
    random.shuffle(tasks)
    for task in tasks:
        random.shuffle(task.options)
    return tasks


def answers(tasks) -> str:
    """encode correct answers of tasks as string like 'ABCDA'"""
    return "".join([t.correct for t in tasks])


def score(given: str, correct: str) -> int:
    """compare string-encoded given answers with correct answers"""
    return sum(a == b for a, b in zip(given, correct))
