import jsonlines
import argparse
import random
import os
from votekit import (
    name_BradleyTerry,
    name_PlackettLuce,
    CambridgeSampler,
    AlternatingCrossover,
)
from votekit.elections import STV, fractional_transfer


## STV (5 seat), IRV (1 seat)
## Even R/D split, based on population
## Dirichlet alpha=1
# CS both ways: (W=R / C=D) and (W=D / C=R)
# 10 plans - 100 simulations
ELECTION = "SEN18"
NUM_SIMS = 100

parser = argparse.ArgumentParser()
parser.add_argument("--seats", type=int, required=True)
parser.add_argument("--num_districts", type=int, required=True)
parser.add_argument("--even_split", action="store_true")
args = parser.parse_args()

# _R = (W=R / C=D), _D = (W=D / C=R)
models = {
    "placket-luce": name_PlackettLuce,
    "bradley-terry": name_BradleyTerry,
    "cambridge_R": CambridgeSampler,
    "cambridge_D": CambridgeSampler,
    "alternating-crossover": AlternatingCrossover,
}

ensemble = []
elect_type = 'STV'
if args.num_districts in [40, 160]:
    elect_type = "IRV"

with jsonlines.open(f"./plans/{elect_type}/pl_ensembles-{args.num_districts}.jsonl", "r") as f:
    for line in f:
        ensemble.append(line)

# make sure to write out the plans used
sample_ensemble = random.sample(ensemble, 10)

# fixed ballot generation parameters
cohesion_parameters = {"R": {"R": 0.7, "D": .3}, "D": {"D": 0.9, "R": 0.1}}
dirichlet_alphas = {"R": {"R": 1, "D": 1}, "D": {"R": 1, "D": 1}}

rcands = [f"R{i}" for i in range(1, 15)]
dcands = [f"D{i}" for i in range(1, 15)]

total_cands = 14

os.makedirs("./output", exist_ok=True)
with jsonlines.open(
    f"./output/{elect_type}-{args.num_districts}-{args.seats}-results.jsonl", "w"
) as w:
    for plan in sample_ensemble:
        plan_data = []
        district_shares = plan[ELECTION]
        for demshare in district_shares:
            zone_data = {}
            bloc_proportions = {"R": 1-demshare, "D": demshare}
            demcands = round(demshare * total_cands)
            zone_data["demshare"] = demshare
            if args.even_split:
                zone_data["demcands"] = 7
                zone_data["rcands"] = 7
                slate_to_candidates = {"R": rcands[:7], "D": dcands[:7]}
            else:
                zone_data["demcands"] = demcands
                zone_data["rcands"] = total_cands - demcands
                slate_to_candidates = {
                    "R": rcands[: total_cands - demcands],
                    "D": dcands[:demcands],
                }

            for i in range(NUM_SIMS):
                for modelname, model in models.items():
                    print("Starting process for:", modelname)
                    params = {}

                    # if modelname == "cambridge_R":
                    #     params["historical_majority"] = "R"
                    #     params["historical_minority"] = "D"
                    # elif modelname == "cambridge_D":
                    #     params["historical_majority"] = "D"
                    #     params["historical_minority"] = "R"

                    generator = model.from_params(
                        slate_to_candidates=slate_to_candidates,
                        bloc_voter_prop=bloc_proportions,
                        cohesion_parameters=cohesion_parameters,
                        alphas=dirichlet_alphas,
                        **params
                    )
                    if modelname == 'bradley-terry':
                        ballots = generator.generate_profile_MCMC(number_of_ballots=1000)
                    else:
                        ballots = generator.generate_profile(number_of_ballots=1000)

                    print("Made ballots for", modelname)
                    results = STV(
                        ballots,
                        transfer=fractional_transfer,
                        seats=args.seats,
                        quota="droop",  # Added from chris' code
                        ballot_ties=False,
                        tiebreak="random",  # Added from chris' code
                    ).run_election()

                    # maybe condense
                    winners = results.to_dict(keep=['ranking'])
                    print("Ran Election")

                    if modelname not in zone_data:
                        zone_data[modelname] = []
                    zone_data[modelname].append(winners)

            plan_data.append(zone_data)
        w.write(plan_data)
