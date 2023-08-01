import json
import geopandas as gpd
import sys
import re
from gerrychain import Graph
from gerrytools.plotting import drawplan
from pathlib import Path
import os
import us

loc_add = 0
nested_str = ""
if len(sys.argv) > 4: 
  if len(sys.argv) == 5 and sys.argv[-1] == "--nested":
    nested_str = "-nested"
    loc_add = -1
  else:
    raise ValueError("Additional arguments were provided, but are invalid. Assuming this is not a nested configuration.")

mag_list = json.loads(sys.argv[-1+loc_add])
bias = sys.argv[-2+loc_add]
location = sys.argv[-3+loc_add]

mag_str = f"{mag_list[0]}-{mag_list[1]}-{mag_list[2]}

read = Path(f"output/chains/{location.lower()}-{mag_str}{nested_str}/")
write = Path(f"output/figures/nationwide/{location.lower()}-{mag_str}{nested_str}/")

with open(read/f"{bias}-assignments.jsonl", "r") as f:
  data = [json.loads(line) for line in f]

#The example plan will be the last one in the ensemble.
data = data[-1]

graph = Graph.from_json(f"data/graphs/{location.lower()}.json")

# Read in the VTD shapefile for the specific location
state = us.states.lookup(location.capitalize())
state_vtd = gpd.read_file(f"http://data.mggg.org.s3-website.us-east-2.amazonaws.com/vtd-shapefiles/{str(state.abbr).upper()}_vtd20.zip")

# Map the assignmnet data from the ensemble output to the state's GEOIDs.
info = {graph.nodes[node]["GEOID20"]: data[str(node)] for node in graph.nodes}

state_vtd["assignment"] = state_vtd["GEOID20"].map(info)

state_vtd = staet_vtd.dissolve(by="assignment").reset_index()


ax = drawplan(
    state_vtd, "assignment", overlays=[], colors=None, numbers=False, lw=1 / 2,
    fontsize=15, edgecolor="black")

os.makedirs(write, exist_ok = True)
ax.figure.savefig(write/f"{bias}.png", dpi=500, bbox_inches="tight", transparent=True)
