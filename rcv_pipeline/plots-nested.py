import json
import geopandas as gpd
import sys
import re
from gerrychain import Graph
from gerrytools.plotting import drawplan

mag_list = sys.argv[-1].replace("[", "").replace("]", "").replace(" ", "").split(",")
bias = sys.argv[-2]
location = sys.argv[-3]


with open(f"output/chains/{location.lower()}-{mag_list[0]}-{mag_list[1]}-{mag_list[2]}-nested/{bias}-assignments.jsonl", "r") as f: 
  for line in f:
    data = json.loads(line)


overlay_list = [t for t in mag_list/4]
data_overlay = []
with open("output/chains/massachusetts-{overlay_list[0]}-{overlay_list[1]}-{overlay_list[2]}/{bias}-assignments.jsonl", "r") as f:
  for line in f:
    data_overlay = json.loads(line)

print(data_overlay)
graph = Graph.from_json(f"data/graphs/{location}.json")

ma_vtd = gpd.read_file("http://data.mggg.org.s3-website.us-east-2.amazonaws.com/vtd-shapefiles/MA_vtd20.zip")

info = {graph.nodes[node]["GEOID20"]: data[str(node)] for node in graph.nodes}
info_overlay = {graph.nodes[node]["GEOID20"]: data_overlay[str(node)] for node in graph.nodes}
ma_vtd["overlay"] = ma_vtd["GEOID20"].map(info_overlay)
ma_vtd["assignment"] = ma_vtd["GEOID20"].map(info)
ma_vtd = ma_vtd.dropna(subset=["assignment"])
ma_vtd_diss = ma_vtd.dissolve(by="assignment").reset_index()
ma_vtd_overlay = ma_vtd.dissolve(by="overlay").reset_index()
ma_vtd_overlay = ma_vtd_overlay.to_crs("epsg:3857")
ax = drawplan(
    ma_vtd_diss, "assignment", overlays=[ma_vtd_overlay], colors=None, numbers=False, lw=1 / 4,
    fontsize=15, edgecolor="black")

write = f"output/figures/nationwide/{location}-{mag_list[0]}-{mag_list[1]}-{mag_list[2]}-nested"
os.makedirs(write, exist_ok = True)
ax.figure.savefig(f"{write}/{bias}.png", dpi = 500, bbox_inches = "tight", transparent=True)
ma_vtd_overlay.plot(column="overlay", facecolor="None", cmap="Set1", lw=2, ax = ax)
ax.set_axis_off()

ax.figure.savefig(f"{write}/{bias}.png", dpi = 500, bbox_inches = "tight", transparent=True)
