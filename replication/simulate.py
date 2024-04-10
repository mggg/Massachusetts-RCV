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


# helper functions
def count_winners(results: list, majority: str, seats: int) -> int:
    """
    Helper function to count winners from election ranking vector.
    Returns the number of winners from the majority.
    """
    num_winners = 0
    for cand in results[:seats]:
        if cand[0] == majority:
            num_winners += 1

    return num_winners


## Simulation code
# CS both ways: (W=R / C=D) and (W=D / C=R)

parser = argparse.ArgumentParser()
parser.add_argument("--num_districts", type=int, required=True)
parser.add_argument("--num_seats", type=int, required=True)
parser.add_argument("--cand_split", type=str, required=True)
parser.add_argument("--n_elections", type=int, required=True)
args = parser.parse_args()


models = {
    "placket-luce": name_PlackettLuce,
    "bradley-terry": name_BradleyTerry,
    "cambridge": CambridgeSampler,
    "alternating-crossover": AlternatingCrossover,
}

ensemble = []
elect_type = "STV"
if args.num_districts in [40, 160]:
    elect_type = "IRV"

with jsonlines.open(
    f"./plans/{elect_type}/pl_ensembles-{args.num_districts}.jsonl", "r"
) as f:
    for line in f:
        ensemble.append(line)

# make sure to write out the plans used
sample_ensemble = random.sample(ensemble, 10)

plan_dir = "./mass_output/sample_plans"
os.makedirs(plan_dir, exist_ok=True)
with jsonlines.open(plan_dir + "/" f"{args.num_districts}-ensemble.jsonl", "w") as w:
    w.write_all(sample_ensemble)

# fixed ballot generation parameters
cohesion_parameters = {"R": {"R": 0.7, "D": 0.3}, "D": {"D": 0.9, "R": 0.1}}
dirichlet_alphas = {"R": {"R": 1, "D": 1}, "D": {"R": 1, "D": 1}}

rcands = [f"R{i}" for i in range(1, 15)]
dcands = [f"D{i}" for i in range(1, 15)]

total_cands = 14
election = "SEN18"

for plan_idx, plan in enumerate(sample_ensemble):
    plan_data = []
    district_shares = plan[election]
    for demshare in district_shares:

        zone_data = {}
        bloc_proportions = {"R": 1 - demshare, "D": demshare}
        demcands = round(demshare * total_cands)
        zone_data["demshare"] = demshare
        zone_data["seats"] = args.num_seats
        zone_data["raw_outputs"] = []

        if args.cand_split == "EVEN":
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

        for i in range(args.n_elections):
            for modelname, model in models.items():
                generator = model.from_params(
                    slate_to_candidates=slate_to_candidates,
                    bloc_voter_prop=bloc_proportions,
                    cohesion_parameters=cohesion_parameters,
                    alphas=dirichlet_alphas,
                )

                if modelname == "bradley-terry":
                    ballots = generator.generate_profile_MCMC(number_of_ballots=1000)
                else:
                    ballots = generator.generate_profile(number_of_ballots=1000)

                results = STV(
                    ballots,
                    transfer=fractional_transfer,
                    seats=args.num_seats,
                    quota="droop",
                    ballot_ties=False,
                    tiebreak="random",
                ).run_election()

                winners = results.to_dict(keep=["ranking"])

                # save D winners
                if modelname not in zone_data:
                    zone_data[modelname] = []
                zone_data[modelname].append(
                    count_winners(winners["ranking"], "D", args.num_seats)
                )

                # save ranking vector from elections
                zone_data["raw_outputs"].append({modelname: winners["ranking"]})

        plan_data.append(zone_data)

    out_dir = f"./mass_output/results/{elect_type}-{args.num_districts}-{args.num_seats}-result"
    os.makedirs(out_dir, exist_ok=True)

    with jsonlines.open(out_dir + "/" + f"plan-{plan_idx}.jsonl", "w") as w:
        w.write_all(plan_data)
