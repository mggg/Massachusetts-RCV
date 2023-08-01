
from gerrychain.accept import always_accept
from gerrychain.chain import MarkovChain
from gerrychain.proposals import ReCom
from gerrychain.partition import MultiMemberPartition
from gerrychain.graph import Graph
from gerrychain.tree import recursive_tree_part
from gerrychain.updaters import Tally, cut_edges
from gerrychain.constraints import within_percent_of_ideal_population_per_representative
from pathlib import Path
import jsonlines
import json
import sys
import math
import random
import numpy as np
import geopandas as gpd
import warnings
warnings.filterwarnings("ignore")

from accept import (
    mh, mmpreference, districts as magnituder, totalseats, annealing,
    logistic, step, logicycle
)

from AnnealingConfiguration import AnnealingConfiguration

# Get the location we're working on and whether it's a "tilted" chain or not. The
# second argument should be either "tilted" or "neutral." The third argument is the
# magnitude list desired for this ensemble and the fourth argument is the magnitude
# list of the pre-existing ensemble to be used for nesting
assignment_num = sys.argv[-3]
nested_mag_list = json.loads(sys.argv[-1])
mag_list = json.loads(sys.argv[-2])
location = sys.argv[-5]
chaintype = sys.argv[-4]
tilted = chaintype == "tilted"

# Read in configuration information if we're running a tilted chain.
if tilted:
    with open("config.json") as r: config = json.load(r)
    configuration = AnnealingConfiguration(**config[location])

# Set some defaults.
POPCOL = "TOTPOP20"
EPSILON = 0.05
ITERATIONS = 1000
ASSIGNMENTS = True
SAMPLE = int(ITERATIONS*(1/10))
SAMPLEINDICES = list(np.random.choice(range(0, ITERATIONS), size=SAMPLE, replace=False))
TEST = False

# For each of the locations, create relatively large ensembles. From these, we'll
# subsample.
# Read in the dual graph and the groupings.
G = Graph.from_json(f"./data/graphs/{location}.json")
with open("./groupings.json") as f: info = json.load(f)


data = []
with open(f"output/chains/{location}-{nested_mag_list[0]}-{nested_mag_list[1]}-{nested_mag_list[2]}/tilted-assignments.jsonl", "r") as f:
  for line in f:
    data.append(json.loads(line))

data = data[-1]

plan_info = {G.nodes[node]["GEOID20"]: data[str(node)] for node in G.nodes}

ma_vtd = gpd.read_file("http://data.mggg.org.s3-website.us-east-2.amazonaws.com/vtd-shapefiles/MA_vtd20.zip")
ma_vtd["assignment"] = ma_vtd.GEOID20.map(plan_info)
ma_mini = ma_vtd[ma_vtd.assignment == float(assignment_num)]
ma_mini["POCVAP20"] = ma_mini["VAP20"]-ma_mini["WVAP20"]
mini_graph = Graph.from_geodataframe(ma_mini)
sys.stderr.write("made mini graph")

# Explode the districts.
districts = info[location]["districts"]
grouping = mag_list #info[location]["nested"]

# For the grouping with the most five-member districts, create a dictionary
# that maps district numbers to their magnitudes.
magnitudes = {}
last = 1
for magnitude, number in zip([3, 4, 5], grouping):
    for i in range(number):
        magnitudes[last] = magnitude
        last += 1

members = sum(magnitudes.values())
districts = list(magnitudes.keys())


# Find the ideal population.
totpop = sum(d[POPCOL] for _, d in mini_graph.nodes(data=True))
ideal = totpop/members

data = []
assignments = []
if TEST:
  seatcounts = []
  anneal = []
  preference = []

# Create an assignment.
assignment, magnitudes = recursive_tree_part(
  mini_graph, districts, ideal, POPCOL, EPSILON, magnitudes=magnitudes
)

# Updater for getting magnitude counts; also get the statewide POCVAP share.
counter = magnituder(totpop, members)
pocvap = sum(d["POCVAP20"] for _, d in mini_graph.nodes(data=True))
vap = sum(d["VAP20"] for _, d in mini_graph.nodes(data=True))

# Create updaters.
updaters = {
      "population": Tally(POPCOL, "population"),
      "cut_edges": cut_edges,
      "POCVAP20": Tally("POCVAP20", "POCVAP20"),
      "VAP20": Tally("VAP20", "VAP20"),
      "PREFERENCE": mmpreference("POCVAP20", "VAP20", pocvap/vap),
      "MAGNITUDE": lambda P: { d: counter(P["population"][d]) for d in P.parts },
      "SEATS": totalseats,
      "STEP": step
}

if tilted:
      updaters.update({
          "ANNEAL": annealing(
              "SEATS",
              logicycle(
                  configuration.max,              # maximum (minimum) temperature
                  configuration.growth,           # logistic growth rate
                  ITERATIONS,
                  configuration.midpoint,         # where the cycle hits its "peak"
                  cycles=configuration.cycles,    # number of cycles across the chain
                  cold=configuration.cold         # number of steps we stay at the max (min) temp per cycle
              ),
              step="STEP",
              maximize=True
          )
      })

# Create the initial partition.
initial = MultiMemberPartition(     
  mini_graph, assignment=assignment, updaters=updaters, magnitudes=magnitudes
)

# Create the chain differently based on the type of chain we're running.
proposal = ReCom(POPCOL, ideal, EPSILON, multimember=True)
constraints = [
     within_percent_of_ideal_population_per_representative(initial, EPSILON)
]

def tentative(score):
    def _(P):
        return min(P[score], 1) >= random.random()
    return _

chain = MarkovChain(
    proposal=proposal, constraints=constraints, accept=tentative("ANNEAL") if tilted else always_accept,
    initial_state=initial, total_steps=ITERATIONS
)

# Create an empty list for plot data.
collectible = [
    "population", "POCVAP20", "VAP20", "MAGNITUDE", "PREFERENCE", "SEATS",
    "STEP"
] + (["ANNEAL"] if tilted else [])

  
# Iterate over the chain and collect statistics.
for i, partition in enumerate(chain.with_progress_bar()):
    data.append({
          updater: partition[updater]
          for updater in collectible
    })

    # If we're testing for annealing configurations, get them here.
    if TEST:
        seatcounts.append(partition["SEATS"])
        preference.append(partition["PREFERENCE"])
        if tilted: anneal.append(partition["ANNEAL"])

    # Also collect assignments!
    if ASSIGNMENTS and i in SAMPLEINDICES: assignments.append(dict(partition.assignment))

# Write to file.
out = Path(f"./output/chains/{location}-{grouping[0]*nested_mag_list[0]}-{grouping[1]*nested_mag_list[1]}-{grouping[2]*nested_mag_list[2]}-nested")

# If we aren't testing -- i.e. if this is a live run -- we save the data and the
# corresponding assignments to the appropriate location. Otherwise, we save the
# test data collected.
if not out.exists(): out.mkdir()


if not TEST:
    with jsonlines.open(out/f"{chaintype}-{assignment_num}.jsonl", mode="w") as w:
        w.write_all(data)

    if ASSIGNMENTS:
        with jsonlines.open(out/f"{chaintype}-assignments-{assignment_num}.jsonl", mode="w") as w:
            w.write_all(assignments)
else:
    with open(out/f"{chaintype}-seats-{assignment_num}.json", "w") as w: json.dump(seatcounts, w)
    with open(out/f"{chaintype}-anneal-{assignment_num}.json", "w") as w: json.dump(anneal, w)
    with open(out/f"{chaintype}-preference-{assignment_num}.json", "w") as w: json.dump(preference, w)
        
