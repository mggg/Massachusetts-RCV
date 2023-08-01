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
import time
import random


if len(sys.argv) == 3:
    num_cands = int(sys.argv[-1])
    dist_code = str(sys.argv[-2])
else: 
    raise ValueError("No distric number provided.")

for i in range(1, 6):
    districts = []
    ## change file path with correct numbers 
    with jsonlines.open(f"../original/massachusetts-{dist_code}-racial-basic/neutral-{i}.jsonl") as r: 
        for line in r:
            districts.append(line)

    models = {
        "plackett-luce": luce_dirichlet,
        "bradley-terry": bradley_terry_dirichlet,
        "crossover": BABABA,
        "cambridge": Cambridge_ballot_type
    }

    randomized = [luce_dirichlet, bradley_terry_dirichlet]
    sampling = [BABABA, Cambridge_ballot_type]

    if num_cands == 12:
        poc_cands = 6
        open_seats = 4
    if num_cands == 15:
        poc_cands = 7
        open_seats = 5

    plan_results = []

    for idx, zone in enumerate(districts):
        
        district = []

        for model in zone:

            kwargs = dict(
                poc_share=model['pocshare'],
                poc_support_for_poc_candidates=model['pp'],
                poc_support_for_white_candidates=model['pw'],
                white_support_for_white_candidates=model['ww'],
                white_support_for_poc_candidates=model['wp'],
                seats_open=open_seats,
                num_poc_candidates=poc_cands, #change to 6 if 10x4, or 40X4
                num_white_candidates=num_cands-poc_cands, #change to 6 if 10x4, or 40X4
                max_ballot_length=None,
                num_ballots=1000,
                num_simulations=100
                )

            model_type = models[model['model']]
            con_name = model['concentrationname']

            # print(f'Running Zone {idx} - Model: {str(model_type)}')
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
            seats=open_seats,
            candidates=num_cands, #change to 12 if 10x4, or 40X4
            wcandidates=num_cands-poc_cands, #change to 6 if 10x4, or 40X4
            poccandidates=poc_cands, #change to 6 if 10x4, or 40X4
            concentration=model['concentration'],
            concentrationname=con_name,
            pocwins=local,
            model=model['model'],
                )
            
            district.append(dict(mr))

        plan_results.append(district)

    # change outpath to match numbers 
    out_path = f'output/equal_cands/massachusetts-{dist_code}-equal_cands'

    os.makedirs(out_path, exist_ok=True)   

    with jsonlines.open(f'{out_path}/neutral-{i}.jsonl', mode="w") as w:
        w.write_all(plan_results)