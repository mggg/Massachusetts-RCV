
import jsonlines
import json
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.font_manager import FontProperties
from matplotlib.lines import Line2D
from pathlib import Path
import us
import os
import sys
import pandas as pd
import numpy as np
from collections import Counter
import regex as re
from plot_helper import count_freq, find_percents, merge_dictionaries, rename


if len(sys.argv) == 2:
    model_type = sys.argv[-1]
else: 
    raise ValueError("Additional arguments were provided, but are invalid. Assuming this is not a nested configuration.")
# Get the location for the chain and the bias.

mag_str = re.search(r'\b\d+-\d+-\d+\b', model_type).group()
mag_list = list(map(int, mag_str.split('-')))
location = us.states.lookup('Massachusetts', field="name")
focus = { us.states.FL, us.states.IL, us.states.MA, us.states.MD, us.states.TX }

# Get the configuration for the state.
poc = pd.read_csv("data/demographics/pocrepresentation.csv")

statewide = pd.read_csv("data/demographics/summary.csv")

demo = pd.read_csv("data/demographics/nationwide.csv")
mas_dem = demo[demo['STATE'] == 'Massachusetts']

summary = statewide.merge(poc, on="STATE")\
    .set_index("STATE")\
    .to_dict("index")

state = summary[location.name.title()]

REDUCEDTURNOUT = True
turnoutsuffix = ""
if REDUCEDTURNOUT: turnoutsuffix = "_low_turnout"
# Load the plans for the ensemble.
output = Path("output/")

#output/may-16-results
planpath = Path(output/model_type)


ensembletypes = ["neutral"]

totmembers = (mag_list[0]*3) + (mag_list[1]*4) + (mag_list[2]*5)

# Create a mapping for configurations.
concentrations = {
    "A": [0.5]*4,               # Voters more or less agree on candidate order for each group.
    "B": [1]*4,       # Every voter is equally likely to vote for every candidate. 
    "C": [0.5, 1, 1, 0.5],      # POC voters agree on POC preferred candidates, White voters agree on White preferred candidates. 
    "D": [0.5,2,2,0.5],         # POC voters agree on POC pref, and white voters agree on White pref, stronger disagreement otherwise.
    # "E": [1]*4                  # No agreement or disagreement --- it's pandemonium.
}

# Bucket for ensembles.
ensembles = []
subsample = 100
models = ["plackett-luce", "bradley-terry", "cambridge"]

for ensembletype in ensembletypes:
    # Bucket for plans.
    plans = []
    # Check to see whether we have the complete results.
    tpath = planpath/f"{ensembletype}-1.jsonl"
    representatives = totmembers
    if tpath.exists() or True:

        for plan in range(1,2):
            part = count_freq(f"../{planpath}/{ensembletype}-{plan}.jsonl", models, subsample)
            ensembles.append(part)

all_results = merge_dictionaries(ensembles)
modelresults= find_percents(all_results)
# rename crossover to alt. crossover 
# modelresults["alt. crossover"] = modelresults["crossover"]
# del modelresults["crossover"]
# del modelresults["alt. crossover"]

#reorder dictionary 
modelresults = { model: modelresults[model] 
    for model in ["plackett-luce", "bradley-terry", "cambridge", "Combined"]
    }
# Create plots.
fig, ax = plt.subplots(figsize=(15, 7.5))

# Plotting! Here, we want to make circles at the appropriate height by summing
# over the seat totals from the *plans*. Set some defaults, like the max radius
# of the circles.
r = 1/2
y = 3.65
ymax = 13
xmax, xmin = 0, 10000

# Some defaults for circles.
cdefs = dict(
    linewidth=3/4,
    edgecolor="grey",
    zorder=1
)

for name, model in modelresults.items():
    for x, share in model.items():
        # Get the appropriate radius relative to the max radius.
        sr = r*np.sqrt(share)
        # Plot a circle!
        if 'partisan' in model_type:
            color = 'darkslategray' if name == "Combined" else 'tab:red'
        else:
            color = "darkslategray" if name == "Combined" else "mediumpurple"
        C = Circle((x, ymax-(y+1) if name == "Combined" else ymax-y), sr+0.15, facecolor=color)
        ax.add_patch(C)

        if xmax < x: xmax = x
        if xmin > x: xmin = x
    
    y+=2

# Set proportionality line and Biden support line!
if 'partisan' not in model_type:
    bh_share = (mas_dem["BVAP20"].iloc[0] + mas_dem["HVAP20"].iloc[0])/mas_dem['VAP20'].iloc[0]

    ax.axvline(totmembers*state["POCVAP20%"], color="gold", alpha=1/2)
    ax.axvline(totmembers*bh_share, color="olivedrab", alpha=1/2)
    ax.axvline(totmembers*(state["2018_WARREN_D"]/(state["2018_WARREN_D"] + state["2018_WARREN_R"])), 
        color="peru", alpha=1/2)
    ax.axvline(totmembers*(state["2020_PRES_D"]/(state["2020_PRES_D"]+state["2020_PRES_R"])),
        color="slategray", alpha=1/2)


if 'partisan' in model_type:
    ax.axvline(totmembers*(state["2018_WARREN_R"]/(state["2018_WARREN_D"] + state["2018_WARREN_R"])), 
        color="olivedrab", alpha=1/2)

    ax.axvline(totmembers*(state["2020_PRES_R"]/(state["2020_PRES_R"]+state["2020_PRES_R"])),
        color="slategray", alpha=1/2)


# Re-set the xmin value if the number of POC representatives is smaller than everything!
# Really unlikely that the current number is bigger than everything.
xmin = 0

# Set labels!
#pos = list(range(1, x+1))
labellocs = [2, 5, 7, 9]

# Set label and ticklabel font properties.
lfp = FontProperties(family="DejaVu Sans")
lfd = {"fontproperties": lfp}
fp = FontProperties(family="DejaVu Sans")



#xticks = list(range(xmin, xmax+1))

if totmembers < 10:
  xticks = list(range(round(totmembers*0.75)))
  ax.set_xticks(xticks, [str(int(x)) for x in xticks])
elif 10 <= totmembers <= 50:
  xticks = list(range(round(totmembers*0.75)))
  ax.set_xticks(xticks[::5],
                [str(int(x)) for x in range(round(totmembers*0.75)) if x%5 == 0])
else:
  xticks = list(range(round(totmembers*0.75)))
  ax.set_xticks(xticks[::10],
                [str(int(x)) for x in range(round(totmembers*0.75)) if x%10 == 0])
  


# Set aspects equal.
ax.set_aspect("equal")

for tickset in [ ax.get_xticklabels()]:
    for tick in tickset:
        tick.set_fontproperties(fp)

# Set axis labels.
ax.set_xlabel("Statewide Seats", fontdict=lfd)

# Add a legend?
if 'partisan' in model_type:
    handles = [
        Line2D([0],[0], color="k", alpha=3/4, label=f"Trump proportionality ({round((state['2020_PRES_R']/(state['2020_PRES_D'] + state['2020_PRES_R']))*100)}%)"),
        Line2D([0],[0], color="forestgreen", alpha=3/4, label=f"Diehl proportionality ({round((state['2018_WARREN_R']/(state['2018_WARREN_D'] + state['2018_WARREN_R']))*100)}%)")
    ]

else:
    handles = [
            Line2D([0],[0], color="gold", alpha=3/4, label=f"POC proportionality ({round((state['POCVAP20%'])*100)}%)"),
            Line2D([0],[0], color="forestgreen", alpha=3/4, label=f"BH proportionality ({round((bh_share)*100)}%)"),
            Line2D([0],[0], color="k", alpha=3/4, label=f"Biden proportionality ({round((state['2020_PRES_D']/(state['2020_PRES_D']+state['2020_PRES_R']))*100)}%)"),
            Line2D([0],[0], color="peru", alpha=3/4, label=f"Warren proportionality ({round((state['2018_WARREN_D']/(state['2018_WARREN_D'] + state['2018_WARREN_R']))*100)}%)")
        ]

ax.legend(
    prop=FontProperties(family="DejaVu Sans", size=7),
    title_fontproperties=FontProperties(family="DejaVu Sans", size=9),
    title="Detailed seat projection", handles=handles, ncol=2,
    borderaxespad=0, loc="lower center", bbox_to_anchor=(0.5, 1.05)
)

# Take away x-tick values and x-tick markers.
ax.axes.get_yaxis().set_visible(False)

# Set plot limits.
ax.set_xlim(0, round(totmembers*0.75))
ax.set_ylim(0, y)
# chnage set_xlim to resize plots

for m, loc in zip(modelresults.keys(), reversed(labellocs)):
    if m == "crossover": m = "alt. crossover"
    ax.text(
        xmin-6/5, loc, m.title(), fontsize=10, ha="right", va="center", fontdict=lfd
    ) # change xmin to lowerbound-3 

bbox = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
width, height = bbox.width, bbox.height


save_state = str(location.name)

figpath = f"plots_no_AC/{save_state.lower()}"
plot_name = re.sub(r'\b\d+-\d+-\d+\b', rename(mag_list), model_type)

os.makedirs(figpath, exist_ok=True)
## TODO: rename file path 
plt.savefig(f"{figpath}/{plot_name}.png", dpi=600, bbox_inches="tight")


        