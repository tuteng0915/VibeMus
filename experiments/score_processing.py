"""Process score JSONs to compute stats and accepted sample IDs."""

import json
import matplotlib.pyplot as plt
import numpy as np

with open('score of demo.json') as f:
    demo = json.load(f)

with open('score of control group 1.json') as f:
    control1 = json.load(f)

with open('score of control group 2.json') as f:
    control2 = json.load(f)

avgd = []

avg1 = []

avg2 = []

accepted = []

for i in demo:
    if demo[i].get('Average', 0.0) == 0.0:
        continue
    if control1[i].get('Average', 0.0) == 0.0:
        continue
    if control2[i].get('Average', 0.0) == 0.0:
        continue
    avgd.append(demo[i]['Average'])
    avg1.append(control1[i]['Average'])
    avg2.append(control2[i]['Average'])
    accepted.append(i)

print(f'experimantal group: avg={np.mean(avgd)}, std={np.std(avgd)}')

print(f'control group 1: avg={np.mean(avg1)}, std={np.std(avg1)}')

print(f'control group 2: avg={np.mean(avg2)}, std={np.std(avg2)}')

with open('accepted.json', 'w') as f:
    json.dump(accepted, f)
