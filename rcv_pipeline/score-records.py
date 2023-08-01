
import jsonlines
import us
import sys
from pathlib import Path
import json
import os

# the first argument here is the location to score, the second 
# is denotes whether you're scoring a neutral or tilted ensemble. 
# the third is the list of district magnitudes.

# there's an optional fourth argument denoting whether you're
# scoring an ensemble that was nested into a different plan. 

nested=False
nested_str = ""
loc_add = 0

if len(sys.argv) > 4:
  if sys.argv[-1] == "--nested" and len(sys.argv) == 5:
    nested = True
    nested_str = "-nested"
    loc_add = -1
  else:
    raise ValueError("Additional arguments were provided, but are invalid. Assuming this is not a nested configuration.")

mag_list = json.loads(sys.argv[-1+loc_add]) 
location = us.states.lookup(sys.argv[-3+loc_add].title(), field="name")
bias = sys.argv[-2+loc_add]

mag_str = f"{mag_list[0]}-{mag_list[1]}-{mag_list[2]}"

read = Path(f"./output/chains/{location.name.lower()}-{mag_str}{nested_str}/{bias}.jsonl")
write = Path(f"./output/records/{location.name.lower()}-{mag_str}{nested_str}")

# Cread in plan data and create an empty list of records.
with jsonlines.open(read) as r: plans = list(r)
records = []

# Get the number of districts in the state.
districts = sum(plans[0]["MAGNITUDE"].values())

# For each of the plans, "invert" the dictionaries so organized by district->properties,
# not properties->district.
for plan in plans:
    dkeys = list(plan["population"])

    # Get all the standard stuff.
    record = {
        district: {
            prop: plan[prop][district]
            for prop in ["population", "POCVAP20", "VAP20", "MAGNITUDE"]
        }
        for district in dkeys
    }

    # Get the POCVAP percentage.
    for district in dkeys:
        record[district]["POCVAP20%"] = record[district]["POCVAP20"]/record[district]["VAP20"]

    # Get the number of "POC seats"
    for district in dkeys:
        threshold = 1/(record[district]["MAGNITUDE"]+1)
        record[district]["POCSEATS"] = record[district]["POCVAP20%"]//threshold

    records.append(record)

# Write back to file.
os.makedirs(write, exist_ok = True)
with jsonlines.open(write/f"{bias}.jsonl", mode="w") as w: w.write_all(records)
