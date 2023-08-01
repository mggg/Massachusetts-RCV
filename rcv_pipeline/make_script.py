with open("ma_rcv.sh", "w+") as f:
  for i in range(1, 11): 
    f.writelines(f"python submit_jobs.py -location massachusetts -chaintype tilted -path_to_chain 'massachusetts_0_10_0/neutral-assignments.jsonl' -assignment_num {i}\n")
