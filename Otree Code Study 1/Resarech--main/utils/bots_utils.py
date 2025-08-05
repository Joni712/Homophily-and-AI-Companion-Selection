"""Utils to load bots and names"""

import random
from copy import copy
from dataclasses import dataclass

from .csv_utils import read_csv


@dataclass()
class Bot:
    """A record for a bot"""

    id: str
    race: str
    gender: str
    name: str

    @property
    def imagepath(self):
        """creates (relative) image name for bots avatar"""
        return f"bots/{self.id}.png"

    def __str__(self):
        return f"{self.id}/{self.race}/{self.gender}/{self.name}"


def parse(val: str):
    """create record from string representation"""
    if val is None:
        return Bot(id=None, race=None, gender=None, name=None)
    botid, race, gender, name = val.split("/")
    return Bot(id=botid, race=race, gender=gender, name=name)


def read_bots(filepath):
    """read csv data for bots"""
    return read_csv(filepath, {"id": int, "section": str, "gender": str, "race": str, "name": str})


def read_names(filepath):
    """read csv data of names"""
    return read_csv(filepath, {"gender": str, "name": str})


def merge_names(botsdata, namesdata, *, seed):
    """merge data from bots and names where missing"""
    random.seed(seed)

    data = []
    for gender in ("M", "F"):
        bots = [copy(d) for d in botsdata if d["gender"] == gender]

        names = [d["name"] for d in namesdata if d["gender"] == gender]
        random.shuffle(names)

        bots_u = [d for d in bots if d["name"] == "auto"]
        if len(names) < len(bots_u):
            raise RuntimeError(f"Not enough names for bots of gender {gender}")

        for bot, name in zip(bots_u, names):
            bot["name"] = name

        data.extend(bots)

    return data


def select(data, *, section, seed=None):
    """create list of bot records from data for given section"""
    random.seed(seed)
    results = [
        Bot(id=d["id"], race=d["race"], gender=d["gender"], name=d["name"]) for d in data if d["section"] == section
    ]
    random.shuffle(results)
    return results
