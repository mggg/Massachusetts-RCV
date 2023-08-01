import jsonlines
import numpy as np

def count_freq(plan_file, models, subsample):
    '''
    Finds frequency for one jsonline files
    '''
    plan = []
    totals = {}

    with jsonlines.open(plan_file) as r:
        for line in r:
            plan.append(line)

    num_sims = plan[0][0]['simulations']

    # Store concentration, model and pocwins per plan
    per_dist = {}
    for idx, district in enumerate(plan):
        per_dist[idx] = []
        for simulation in district:
            per_dist[idx].append((simulation['concentrationname'], simulation['model'],
                                simulation['pocwins']))

    #Add statewide seats for each model and concentration type
    # TODO: probably does not need its own loop 
    for results in per_dist.values():
        for subtype in results:
            con, model, pocwins = subtype
            model_id = f'{model}, {con}'
            if model_id not in totals:
                totals[model_id] = np.zeros(subsample)
            totals[model_id] += np.array(pocwins[:subsample])

    freq = {model: {} for model in models} 

    # sum by model (pt, bl, camrbidge)
    for model_type, wins in totals.items(): 
        # first_model,first_value= next(iter(totals.items()))
        # print("first model:", first_model)
        # print("first_value:")
        # print("model_type:", model_type)
        model = model_type.split(",")[0]
        if model in models:
            for seats in wins:
                if seats not in freq[model]:
                    freq[model][seats] = 0
                freq[model][seats] += 1   

    freq['Combined'] = combined_freq(freq)
    
    return freq

def combined_freq(freq):
    '''
    Finds frequency of seats for combined
    '''
    combined = {}
    
    for counts in freq.values():
        for seat, freq in counts.items():
            if seat not in combined:
                combined[seat] = 0
            combined[seat] += freq

    return combined 


def find_percents(freq):
    '''
    Calculates percentage share for each number of seats.
    '''
    for model, seats in freq.items():
        total = sum(seats.values())
        for seat in seats:
            freq[model][seat] = freq[model][seat]/total

    return freq


def merge_dictionaries(ensemble):
    '''
    Combines list of jsonline outputs into one dictionary
    '''
    rv = {}

    for part in ensemble:
        for model, subdict in part.items():
            if model not in rv:
                rv[model] = {}
            for seat, count in subdict.items():
                if seat not in rv[model]:
                    rv[model][seat] = 0
                rv[model][seat] += count 

    return rv 

def rename(mag_lst):
    seat_map = {0:3, 1:4, 2:5}
    for idx, val in enumerate(mag_lst):
        if val != 0:
            return f'{val}x{seat_map[idx]}'
        
        
def statewide_seats(plan_path):
    '''
    Finds statewide seats won in a given plan, across all model types
    '''
    plan = []
    totals = {}

    with jsonlines.open(plan_path) as r:
        for line in r:
            plan.append(line)

    num_sims = plan[0][0]['simulations']

    # Store concentration, model and pocwins per plan
    per_dist = {}
    for idx, district in enumerate(plan):
        per_dist[idx] = []
        for simulation in district:
            per_dist[idx].append((simulation['concentrationname'], simulation['model'],
                                simulation['pocwins']))

    #Add statewide seats for each model and concentration type
    # TODO: probably does not need its own loop 
    for results in per_dist.values():
        for subtype in results:
            con, model, pocwins = subtype
            model_id = f'{model}, {con}'
            if model_id not in totals:
                totals[model_id] = np.zeros(100)
            totals[model_id] += np.array(pocwins[:100])

    return totals
    
