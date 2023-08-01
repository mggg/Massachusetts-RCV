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


plans = []
with jsonlines.open('output/plans/IRV/pl_ensembles-40.jsonl') as r:
    for line in r:
        plans.append(line)


models = {
    "plackett-luce": luce_dirichlet,
    "bradley-terry": bradley_terry_dirichlet,
    "crossover": BABABA,
    "cambridge": Cambridge_ballot_type
}

# Get the randomized models and the sampling models.
randomized = [luce_dirichlet, bradley_terry_dirichlet]
sampling = [BABABA, Cambridge_ballot_type]

keys = ['population', 'VAP20', 'POCVAP20', 'HVAP20', 'BVAP20', 'SEN18']

num_districts = 40

all_results = []

sample_plans = random.sample(plans, 5)

for plan_id, plan in enumerate(sample_plans):

    plan_results = []

    concentration = [0.5, 2, 2, 0.5]
    concentration_name = 'D'

    for district in range(num_districts):
        print(f"Simulating Plan {plan_id}: {district}/{num_districts}")

        district_results = []

        demshare = plan['SEN18'][district]

        demcands = round(demshare*8)
     
        kwargs = dict(
            poc_share=demshare,
            poc_support_for_poc_candidates=0.9,
            poc_support_for_white_candidates=0.1,
            white_support_for_white_candidates=0.8,
            white_support_for_poc_candidates=0.2,
            seats_open=1,
            num_poc_candidates=demcands,
            num_white_candidates=8-demcands,
            max_ballot_length=None,
            num_ballots=1000,
            num_simulations=5
        )

        district_results = []
        for model_name, model in models.items():

            if model in randomized:
                local, atlarge = model(concentrations=concentration, **kwargs)

                mr = ModelingResult(
                pp=0.9,
                pw=0.1,
                ww=0.8,
                wp=0.2,
                simulations=5,
                pocshare=demshare,
                ballots=1000,
                seats=1,
                candidates=8,
                wcandidates=8-demcands,
                poccandidates=demcands,
                concentration=concentration,
                concentrationname=concentration_name,
                pocwins=local,
                model=model_name,
            )
                district_results.append(dict(mr))

            if model in sampling:

                local, atlarge = model(scenarios_to_run=[concentration_name], **kwargs)
                local = local[concentration_name]

                mr = ModelingResult(
                pp=0.9,
                pw=0.1,
                ww=0.8,
                wp=0.2,
                simulations=5,
                pocshare=demshare,
                ballots=1000,
                seats=1,
                candidates=8,
                wcandidates=8-demcands,
                poccandidates=demcands,
                concentration=concentration,
                concentrationname=concentration_name,
                pocwins=local,
                model=model_name,
            )

                district_results.append(dict(mr))

        plan_results.append(district_results)

    out_path = 'output/irv_results'

    os.makedirs(out_path, exist_ok=True)   

    with jsonlines.open(f'{out_path}/{num_districts}-plan-{plan_id}.jsonl', mode="w") as w:
        w.write_all(plan_results)





