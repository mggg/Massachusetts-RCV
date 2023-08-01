import geopandas as gpd
from gerrychain import Graph
from gerrychain import Graph, Election, updaters, Partition, constraints, MarkovChain
from gerrychain.updaters import Tally
from gerrychain.proposals import recom
from gerrychain.tree import recursive_tree_part
from gerrychain.accept import always_accept
import numpy as np
from functools import partial
import sys
import os
import json
import jsonlines

if len(sys.argv) == 2:
    num_districts = int(sys.argv[-1])
elif len(sys.argv) < 2:
    raise ValueError('Must input number of desired districts (e.g 8, 10, 32, 40)')
elif len(sys.argv) == 3:
    num_districts = int(sys.argv[-2])
    for_irv = True


ma = gpd.read_file('data/MA_vtd20/MA_vtd20.shp')
ma_graph = Graph.from_json('data/massachusetts.json')

#TODO: merge election data into ma_ma_graph
elections = ['SEN18D', 'SEN18R', 'GOV14D', 'GOV14R', 'GOV18D', 'GOV18R', 'SEN20GKOCO', 'SEN20GEMAR', 'PRES20GJBI', 'PRES20GDTR']

for node in ma_graph.nodes:
    geo_id = ma_graph.nodes[node]['GEOID20']
    for election in elections:
        ma_graph.nodes[node][election] = ma[ma['GEOID20'] == geo_id][election].iloc[0]

# Set variables 
election_names = ["SEN18", "GOV14", "GOV18", "SEN20", "PRES20"] 

if for_irv:
    election_names = ['SEN18']

#UPDATE this
election_columns = [['SEN18D', 'SEN18R'], 
                    ['GOV14D', 'GOV14R'], 
                    ['GOV18D', 'GOV18R'], 
                    ['SEN20GEMAR', 'SEN20GKOCO'], 
                    ['PRES20GJBI', 'PRES20GDTR']]

pop_tol = 0.05
pop_col = "TOTPOP20"
steps = 100000
INTERVAL = 10

#Iterate through this

total_population = sum([ma_graph.nodes[n][pop_col] for n in ma_graph.nodes()])

pop_target = total_population/num_districts
myproposal = partial(recom, pop_col=pop_col, pop_target=pop_target, epsilon=pop_tol, node_repeats=2)

myupdaters = {"population": updaters.Tally(pop_col, alias="population"),
                "POCVAP20": Tally("POCVAP20", "POCVAP20"),
                "BVAP20": Tally('BVAP20', 'BVAP20'),
                'HVAP20': Tally('HVAP20', 'HVAP20'),
                "VAP20": Tally("VAP20", "VAP20")}

elections = [
        Election(
            election_names[i],
            {"Democratic": election_columns[i][0], "Republican": election_columns[i][1]},
        )
        for i in range(len(election_names))
    ]

election_updaters = {election.name: election for election in elections}
myupdaters.update(election_updaters)


if for_irv: 
    with open('data/good_seed_2.json', 'r') as f:
        assignment = json.loads(f.read())

    clean_assign = {}
    for key, value in assignment.items():
        if int(key) in ma_graph.nodes:
            clean_assign[int(key)] = value

    initial_partition = Partition(ma_graph, assignment=clean_assign, updaters=myupdaters)

if not for_irv:
    first = recursive_tree_part(ma_graph, range(num_districts), total_population/num_districts, pop_col, pop_tol)

    initial_partition = Partition(ma_graph, first, myupdaters)


myconstraints = [
    constraints.within_percent_of_ideal_population(initial_partition, pop_tol)
    ]

chain = MarkovChain(
            proposal=myproposal,
            constraints=myconstraints,
            accept=always_accept,
            initial_state=initial_partition,
            total_steps=steps
        )

demos = ['population', 'VAP20', 'POCVAP20', 'HVAP20', 'BVAP20'] 
## TODO: keep track of POCVAP and VAP
results = []
for idx, step in enumerate(chain):
    if idx%INTERVAL == 0:
        print(f'Step:{idx}/100000')
    election_data = {e: None for e in election_names}
    for e in election_names:
        election_data[e] = step[e].percents('Democratic')
    demo_data = {d: None for d in demos}
    for d in demos:
        demo_data[d] = step[d]
    results.append({**election_data, **demo_data}) 

# store results as jsonl file
out_path = 'data/results'
if for_irv:
    out_path = 'data/results/IRV'

os.makedirs(out_path, exist_ok=True)   

with jsonlines.open(f'{out_path}/pl_ensembles-{num_districts}.jsonl', mode="w") as w:
        w.write_all(results)