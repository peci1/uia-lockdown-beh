import csv
import math
import sys

km_per_run = 6.0
num_slots = 16


class Runner:
    def __init__(self, name, short):
        self.name = name
        self.short = short
        self.can_run = [0] * ((num_slots + 1) * 3)

    def __str__(self):
        return "{} ({})".format(self.name, self.short)

    def __repr__(self):
        return str(self)


def load_data(file):
    lines = []
    with open(file, 'r', newline='') as f:
        reader = csv.reader(f, delimiter=',', quotechar='"')
        for line in reader:
            lines.append(line[1:])

    runners = []
    for line in lines[2:13]:
        name = line[0]
        short = line[1]
        runner = Runner(name, short)
        runner.can_run[0:(num_slots)] = map(bool, line[2:(num_slots + 2)])
        runner.can_run[num_slots] = runner.can_run[num_slots - 1]
        runners.append(runner)

    for line in lines[20:31]:
        short = line[1]
        runner = [r for r in runners if r.short == short][0]
        runner.can_run[(num_slots + 1):(2 * num_slots + 1)] = map(bool, line[2:(num_slots + 2)])
        runner.can_run[2 * num_slots + 1] = runner.can_run[2 * num_slots]

    for line in lines[38:49]:
        short = line[1]
        runner = [r for r in runners if r.short == short][0]
        runner.can_run[(2 * num_slots + 2):(3 * num_slots + 2)] = map(bool, line[2:(num_slots + 2)])
        runner.can_run[3 * num_slots + 2] = runner.can_run[3 * num_slots + 1]

    return runners


def eval_permutation(runners):
    if not max(runners[0].can_run[0:5]) or not max(runners[1].can_run[1:6] or not max(runners[2].can_run[2:7]) or not max(runners[3].can_run[3:8])):
        return 0, 0, []

    used_slots = 0
    runner_id = 0
    total_km = 0

    slot_assignments = [''] * (3 * (num_slots + 1))

    while total_km < 200 and used_slots < 3 * (num_slots + 1):
        runner = runners[runner_id]

        ok = True
        while not runner.can_run[used_slots]:
            used_slots += 1
            if used_slots >= 3 * (num_slots + 1):
                ok = False
                break

        if not ok:
            break

        total_km += km_per_run if used_slots % (num_slots + 1) != 0 else km_per_run / 2
        slot_assignments[used_slots] = runner.short
        used_slots += 1

        runner_id = (runner_id + 1) % len(runners)

    return total_km, used_slots, slot_assignments


def eval_first_runner(first, all):
    if not max(first.can_run[0:5]):
        return 0, 0, []
    
    others = [r for r in all if r.short != first.short]

    best_used_slots = 3 * (num_slots + 1) + 1
    best_slot_assignments = list()
    best_km = 0
    
    num_perms = math.factorial(len(all)-1)
    
    i = 0
    for perm in permutations(others):
        i += 1
        if i % 10000 == 0:
            print("{}/{}".format(i/1000, num_perms/1000))
        runners = [first] + list(perm)
        total_km, used_slots, slot_assignments = eval_permutation(runners)
        if used_slots < best_used_slots and total_km >= 200:
            best_used_slots = used_slots
            best_km = total_km
            best_slot_assignments = slot_assignments
            
    return best_km, best_used_slots, best_slot_assignments


f = "D:/Download/Vyzva 2 vypocty - Kdy muzu.csv"
if len(sys.argv) > 1:
    f = sys.argv[1]

runners = load_data(f)

from itertools import permutations
import multiprocessing
from joblib import Parallel, delayed

best_used_slots = 3*(num_slots+1)+1
best_slot_assignments = list()
best_km = 0

num_perms = math.factorial(len(runners))
print("Num permutations: {}".format(num_perms))

num_cores = multiprocessing.cpu_count()

results = Parallel(n_jobs=num_cores)(delayed(eval_first_runner)(runner, runners) for runner in runners)

for result in results:
    total_km, used_slots, slot_assignments = result
    if used_slots < best_used_slots and total_km >= 200:
        best_used_slots = used_slots
        best_km = total_km
        best_slot_assignments = slot_assignments

print(best_used_slots, best_km, best_slot_assignments)

full_slots = [s for s in best_slot_assignments if len(s) > 0]
print(' '.join(full_slots[0:len(runners)]))
