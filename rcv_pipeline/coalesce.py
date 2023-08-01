import sys
import glob
import json
import jsonlines
import numpy as np 

mag_list = json.loads(sys.argv[-1])
location = sys.argv[-3]
chaintype = sys.argv[-2]

read = f"output/chains/{location}-{mag_list[0]}-{mag_list[1]}-{mag_list[2]}-nested"
write = f"output/chains/{location}-{mag_list[0]}-{mag_list[1]}-{mag_list[2]}-nested"
assignments = glob.glob(f"{read}/*assignments*")
neutral = [n for n in assignments if "neutral" in n]
tilted = [t for t in assignments if "tilted"  in t]
neutral_assignment = {i: {} for i in range(100)}
tilted_assignment =  {i: {} for i in range(100)}
ix = 0
for n, t in zip(neutral, tilted):
  neutral_data = []
  with open(n, "r") as f: 
    for line in f:
      neutral_data.append(json.loads(line))
  tilted_data = []
  with open(t, "r") as f:
    for line in f:
      tilted_data.append(json.loads(line))

  nesting_mag = np.nonzero(mag_list)[0][0]
  renum_dict = {str(i+1): int(((ix)*(4))+(i+1)) for i in range(4)}
  print(renum_dict)
  for i, d in enumerate(neutral_data):
    for k, v in d.items():
       neutral_assignment[i][k] = renum_dict[str(v)]

  for i, d in enumerate(tilted_data):
    for k, v in d.items():
      tilted_assignment[i][k] = renum_dict[str(v)]

  ix += 1
neutral_assignment = list(neutral_assignment.values())
with jsonlines.open(f"{write}/neutral-assignments.jsonl", mode="w") as f:
  f.write_all(neutral_assignment)

tilted_assignment = list(tilted_assignment.values())
with jsonlines.open(f"{write}/tilted-assignments.jsonl", mode="w") as f:
  f.write_all(tilted_assignment)

data = glob.glob(f"{read}/*")
neutral_data = [d for d in data if "assignment" not in d and "neutral" in d]
tilted_data = [d for d in data if "assignment" not in d and "tilted" in d]

neutral_record = [{"population": {}, "POCVAP20": {}, "VAP20": {}, "MAGNITUDE": {}, "SEATS": 0, "PREFERENCE": 0, "STEP": 0} for i in range(100)]
tilted_record = [{"population": {}, "POCVAP20": {}, "VAP20": {}, "MAGNITUDE": {}, "SEATS": 0, "PREFERENCE": 0, "STEP": 0} for i in range(100)]

ix = 0
first_time = True
for n_data, t_data in zip(neutral_data, tilted_data):
  
  n_record = []
  with open(n_data, "r") as f: 
    for line in f:
      n_record.append(json.loads(line))
  
  t_record = []
  with open(t_data, "r") as f:
    for line in f:
      t_record.append(json.loads(line))
  #nesting_mag = np.nonzero(mag_list)[0][0]
  renum_dict = {str(i+1): int(((ix)*(4))+(i+1)) for i in range(4)}
  curr_step =0
  for  n, t in zip(n_record, t_record):
    if curr_step < 100:
      for col in ["population", "POCVAP20", "VAP20", "MAGNITUDE"]:
        for k, v in n[col].items(): 
          neutral_record[curr_step][col][renum_dict[str(k)]] = v 
       
        for k, v in t[col].items():
          tilted_record[curr_step][col][renum_dict[str(k)]] = v

      tilted_record[curr_step]["SEATS"] += t["SEATS"]
      neutral_record[curr_step]["SEATS"] += n["SEATS"]
      tilted_record[curr_step]["STEP"] = t["STEP"]
      neutral_record[curr_step]["STEP"] = n["STEP"]
      curr_step += 1
    
  ix += 1
for record in tilted_record:
  pref = 0
  print(record)
  for poc, vap in zip(list(record["POCVAP20"].values()), list(record["VAP20"].values())):
    pref += (poc/vap)/(1+record["MAGNITUDE"][1])  
  record["PREFERENCE"] = pref

for record in neutral_record:
  pref = 0
  for poc, vap in zip(list(record["POCVAP20"].values()), list(record["VAP20"].values())):
    pref += (poc/vap)/(1+record["MAGNITUDE"][1])
  record["PREFERENCE"] = pref

with jsonlines.open(f"{write}/tilted.jsonl", mode="w") as w:
        w.write_all(tilted_record)

with jsonlines.open(f"{write}/neutral.jsonl", mode="w") as w:
        w.write_all(neutral_record)
