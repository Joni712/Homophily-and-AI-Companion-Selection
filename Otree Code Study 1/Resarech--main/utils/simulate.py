"""Simulates scores based on measured results"""

import csv
import random
import sys

# data from that experiment
EXP_TIMELIM = 200
EXP_RESULTS = [
    6.38,  # solved < 1
    17.02,  # solved 1-2
    20.21,  # solved 2-3
    29.79,  # solved 3-4
    25.53,  # solved 4-5
    1.07,  # solved > 4
]


def simulate_time(rank):
    """simulate time of solving 1 task based on rank
    the performance is betwean TIME/(rank) and TIME/(rank+1)
    """
    min_time = EXP_TIMELIM / (rank + 1)
    max_time = EXP_TIMELIM / rank if rank > 0 else EXP_TIMELIM + 1
    return random.uniform(min_time, max_time)


TIMELIM = 150
COUNTLIM = 5
COUNT = 200


try:
    FILENAME = sys.argv[1]
except IndexError:
    print("Specify filename in args")
    sys.exit()


with open(FILENAME, "w") as f:
    writer = csv.DictWriter(f, fieldnames=["performance", "score"])
    writer.writeheader()
    for i in range(COUNT):
        rank = random.choices([0, 1, 2, 3, 4, 5], EXP_RESULTS)[0]
        time = 0
        count = 0
        while time < TIMELIM and count < COUNTLIM:
            time += simulate_time(rank)
            count += 1
        perf = time / count
        # print(time, count)
        if time > TIMELIM:
            count -= 1
        writer.writerow({"performance": perf, "score": count})
