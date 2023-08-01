import sys
import jsonlines
import warnings
from pathlib import Path
from model_details import (
    Cambridge_ballot_type, BABABA, luce_dirichlet, bradley_terry_dirichlet
)
from ModelingConfiguration import ModelingConfiguration
from ModelingResult import ModelingResult
import os
import json
import jsonlines
from tqdm import tqdm 
import time
import random


districts = []
with jsonlines.open('../output/massachusetts-0-0-8-racial-bh/neutral-1.jsonl') as r:
    for line in r:
        districts.append(line)


models = {
    "plackett-luce": luce_dirichlet,
    "bradley-terry": bradley_terry_dirichlet,
    "crossover": BABABA,
    "cambridge": Cambridge_ballot_type
}

# Get the randomized models and the sampling models.
randomized = [luce_dirichlet, bradley_terry_dirichlet]
sampling = [BABABA, Cambridge_ballot_type]

# concentrations = [([0.5, 0.5, 0.5, 0.5], 'A'), ([1, 1, 1, 1], 'B'), ([0.5, 1, 1, 0.5], 'C'),
#                 ([0.5, 2, 2, 0.5], 'D')]
# keys = ['population', 'VAP20', 'POCVAP20', 'HVAP20', 'BVAP20', 'SEN18']

# num_districts = 10

# all_results = []

# sample_plans = random.sample(plans, 5)

plan_results = []

for zone in districts:
    
    district = []

    for model in zone:

        kwargs = dict(
            poc_share=model['pocshare'],
            poc_support_for_poc_candidates=model['pp'],
            poc_support_for_white_candidates=model['pw'],
            white_support_for_white_candidates=model['ww'],
            white_support_for_poc_candidates=model['wp'],
            seats_open=model['seats'],
            num_poc_candidates=model["poccandidates"],
            num_white_candidates=model["wcandidates"],
            max_ballot_length=None,
            num_ballots=1000,
            num_simulations=100
            )

        model_type = models[model['model']]
        con_name = model['concentrationname']


        if model_type in randomized:
            local, atlarge = model_type(concentrations=model['concentration'], **kwargs)

        if model_type in sampling:
            local, atlarge = model_type(scenarios_to_run=[con_name], **kwargs)
            local = local[con_name]

        mr = ModelingResult(
        pp=model['pp'],
        pw=model['pw'],
        ww=model['ww'],
        wp=model['wp'],
        simulations=100,
        pocshare=model['pocshare'],
        ballots=1000,
        seats=model['seats'],
        candidates=15,
        wcandidates=model['wcandidates'],
        poccandidates=model['poccandidates'],
        concentration=model['concentration'],
        concentrationname=con_name,
        pocwins=local,
        model=model['model'],
            )
        
        district.append(dict(mr))

    plan_results.append(district)

out_path = 'output/bh_testing'

os.makedirs(out_path, exist_ok=True)   

with jsonlines.open(f'{out_path}/test_1.jsonl', mode="w") as w:
     w.write_all(plan_results)





