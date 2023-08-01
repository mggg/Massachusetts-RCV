import random
from collections import defaultdict
import os
import sys


def allocate_seats(plan, seats):
    '''
     Proportional way of allocating seats using percents
    '''
    lst_results = {}

    threshold = 0.8 if seats == 5 else 0.75

    dems = ['W', 'C', 'W', 'C', 'W']
    reps = ['W', 'C', 'W', 'W', 'W']

    if seats == 4:
        dems = ['W', 'C', 'W', 'C']
        reps = ['W', 'C', 'W', 'W']

    for election, results in plan.items():
        dist_results  = defaultdict(None)
        for district, percent in enumerate(results):
            # republican majority 
            if percent < 0.5:
                wins = round(seats*(1-percent)) if (1-percent) < threshold else seats-1
                dist_results[district] = (reps[:wins] + dems[:seats-wins], wins, 'Republican')
            # democratic majority
            if percent >= 0.5:
                wins = round(seats*percent) if percent < threshold else seats-1
                dist_results[district] = (dems[:wins] + reps[:seats-wins], wins, 'Democrat')

        lst_results[election] = dist_results

    return lst_results

###############################################################################
            # Below code not used to simulate party list elections #

def below_threshold(plan, seats):
    '''
    Finds elected candidates based on whether a party expects to
    to win t, a majority of seats.ß

    Inputs:
        plan: districting plan
        seats: districtber of seats per district 

    Returns (dict): key, district and value, tuple with elected set and 
    districtber of Democratic seats 
    '''
    results = {}
    district_dists = len(plan['WARREN18'])
    threshold = 0.5 if seats % 2 == 0 else (seats/2+0.5)/seats

    for district in range(1, district_dists+1):
        #set majority and minority part lists 
        party = 'Democrat'
        maj_lst = ['W', 'W', 'W', 'W', 'W'] if seats == 5 else ['W', 'W', 'W', 'W']
        min_lst = ['W', 'W', 'W', 'W', 'W'] if seats == 5 else ['W', 'W', 'W', 'W']
        results[district] = []
        percent = plan['WARREN18'][str(district)]/(plan['WARREN18'][str(district)] + plan['DIEHL18'][str(district)])
        if percent < 0.5:
            party = 'Republican'
        #place POC just beyond threshold for majority party
        maj_lst[int(percent/(1/seats))] = 'C'
        #place POC beyond threshold 
        min_lst[ int((1-percent)/(1-seats))] = 'C'

        for idx, cand in enumerate(maj_lst):
                if (idx+1)/seats <= max(threshold, percent):
                    results[district].append(cand)
                else:
                    results[district] += min_lst[:seats-idx]
                    results[district] = (results[district], idx, party)
                    break

    return results 
     
def random_list(plan, seats):
    '''
    Randomly assigns list 
    '''
    lst_results = {}
    threshold = 0.5 if seats % 2 == 0 else (seats/2+0.5)/seats

    dems = ['W', 'C', 'W', 'C', 'W']
    reps = ['W', 'C', 'W', 'W', 'W']

    if seats == 4:
        dems = ['W', 'C', 'W', 'C']
        reps = ['W', 'C', 'W', 'W']

    for election, results in plan.items():
        dist_results  = defaultdict(list)
        for district, percent in enumerate(results):
        # Republican majority
            if percent < 0.5:
                reps = random.sample(reps, len(reps))
                for idx, cand in enumerate(reps):
                    if (idx+1)/seats <= max(threshold, 1-percent):
                        dist_results[district].append(cand)
                    else:
                        dist_results[district] += dems[:seats-idx]
                        dist_results[district] = (dist_results[district], idx, 'Republican')
                        break

        # Democratic majority
            if percent >= 0.5:
                dems = random.sample(dems, len(dems))
                for idx, cand in enumerate(dems):
                    if (idx+1)/seats <= max(threshold, percent):
                        dist_results[district].append(cand)
                    else:
                        dist_results[district] += reps[:seats-idx]
                        dist_results[district] = (dist_results[district], idx, "Democrat")
                        break

        lst_results[election] = dist_results

    return lst_results

def vary_by_race(plan, seats):
    '''
    Party list vary by district POC population 
    '''
    lst_results = {}
    threshold = 0.5 if seats % 2 == 0 else (seats/2+0.5)/seats

    for election, results in plan.items():
        dist_results  = defaultdict(list)
        poc_per = plan['POCVAP20'][str(district)]/plan['VAP20'][str(district)]
        for district, percent in enumerate(results):
            party = 'Democrat'
            if percent < 0.5:
                party = 'Republican'
            # low POC
            if poc_per < 0.25:
                cands = ['W', 'W', 'C', 'W', 'W'] if seats == 5 else ['W', 'W', 'C', 'W']
                for idx, cand in enumerate(cands):
                    if (idx+1)/seats <= max(threshold, percent):
                        dist_results[district].append(cand)
                    else:
                        dist_results[district] += cands[:seats-idx]
                        dist_results[district] = (dist_results[district], idx, party)
                        break
            # mid POC
            if 0.25 < poc_per <= 0.4:
                cands = ['W', 'C', 'C', 'W', 'W'] if seats == 5 else ['W', 'C', 'C', 'W']
                for idx, cand in enumerate(cands):
                    if (idx+1)/seats <= max(threshold, percent):
                        dist_results[district].append(cand)
                    else:
                        dist_results[district] += cands[:seats-idx]
                        dist_results[district] = (dist_results[district], idx, party)
                        break
            # high poc
            if poc_per > 0.4:
                cands = ['C', 'W', 'C', 'C', 'W'] if seats == 5 else ['C', 'W', 'C', 'C']
                for idx, cand in enumerate(cands):
                    if (idx+1)/seats <= max(threshold, percent):
                        dist_results[district].append(cand)
                    else:
                        dist_results[district] += cands[:seats-idx]
                        dist_results[district] = (dist_results[district], idx, party)
                        break
        
        lst_results[election] = dist_results

    return lst_results



