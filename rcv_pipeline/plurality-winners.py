import sys
import json
from gerrytools.plotting import * 
import matplotlib.pyplot as plt

"""
ReCom run to make 100K with k=40, C wins iff War>.65 and BH>.3
ReCom outputs as above, C wins iff BH>.4
"""

location = sys.argv[-2]
totmembers = int(sys.argv[-1])

data = []
with open(f"output/records/{location}-{totmembers}-vanilla/neutral.jsonl", "r") as f:
  for line in f:
    data.append(json.loads(line))

all_wins_65 = []
all_wins_40 = []
box_scores = [[] for i in range(50)]
for plan in data:
  num_wins_65 = 0
  num_wins_40 = 0
  all_bh = []
  for district in plan.keys(): 
    if plan[district]["WARREN18%"] > 0.65 and plan[district]["BHVAP20%"] > 0.3:
      num_wins_65 += 1
    if plan[district]["BHVAP20%"] > 0.4: 
      num_wins_40 += 1
    all_bh.append(plan[district]["BHVAP20%"])
  all_bh = sorted(all_bh)[-50:]
  [box_scores[i].append(all_bh[i]) for i in range(50)]  
  all_wins_65.append(num_wins_65)
  all_wins_40.append(num_wins_40)

scores_65 = {"ensemble": all_wins_65, "proposed": [], "citizen": []}
scores_40 = {"ensemble": all_wins_40, "proposed": [], "citizen": []}

fig, ax1 = plt.subplots(1, 1, figsize = (7.5, 5))

hist_ax = histogram(ax1, scores_65, label="# Districts with Warren share > 0.65, BH share > 0.3", fontsize = 10)

hist_ax.figure.savefig(f"output/figures/nationwide/{location.capitalize()}/vanilla-{totmembers}-65-3.png", dpi=500, bbox_inches ="tight")

fig, ax2 = plt.subplots(1, 1, figsize=(7.5, 5))
hist_ax2 = histogram(ax2, scores_40, label="# Districts with BH share > 0.4", fontsize = 10)

hist_ax2.figure.savefig(f"output/figures/nationwide/{location.capitalize()}/vanilla-{totmembers}-40.png", dpi = 500, bbox_inches ="tight")

box_dict = {"ensemble": box_scores, "proposed": [], "citizen": []}
fig, ax3 = plt.subplots(1, 1, figsize = (15, 10))
box_ax = boxplot(ax3, box_dict, labels = ["BHVAP20 Share", ""], ticksize=5)
box_ax.figure.savefig(f"output/figures/nationwide/{location.capitalize()}/vanilla-{totmembers}-bh-box.png", dpi = 500, bbox_inches = "tight")
