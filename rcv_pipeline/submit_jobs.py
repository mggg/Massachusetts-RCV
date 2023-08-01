import os
import click
from time import sleep
import json
import glob



@click.command()
@click.option('-chaintype')
@click.option('-mag_list')
@click.option('-location')
def main(location, chaintype, mag_list):
    mag_list = json.loads(mag_list)
    
    mag_str = f"{mag_list[0]}-{mag_list[1]}-{mag_list[2]}"
    run_id = f"{location}_{chaintype}_{mag_str}"
    with open("job.sh", "w") as f:
      f.writelines("#!/bin/bash\n")
      f.writelines(f"#SBATCH --job-name={location}_{chaintype}_{mag_str}\n")
      f.writelines(f"#SBATCH --time=1-00:00:00\n")
      f.writelines(f"#SBATCH --nodes=1\n")
      f.writelines(f"#SBATCH --ntasks-per-node=1\n")
      f.writelines(f"#SBATCH --mem=16000\n")
      f.writelines(f"#SBATCH -o progress/{location}_{chaintype}_{mag_str}.txt\n")
      f.writelines(f"#SBATCH -e progress/{location}_{chaintype}_{mag_str}_e.txt\n")
      f.writelines(f"#SBATCH --mail-type=FAIL\n")
      f.writelines(f"#SBATCH --mail-user=cricha10@tufts.edu\n\n")
      
      #f.writelines(f"python sample.py {location} {chaintype} '{mag_list}'\n")                    
      #f.writelines(f"python score-records.py {location} {chaintype} '{mag_list}'\n")
      #f.writelines(f"python make-partisan-config.py {location} '{mag_list}'\n")
      #f.writelines(f"python make-config.py {location} '{mag_list}'\n")
      #f.writelines(f"python plots-example-plan.py {location} {chaintype} '{mag_list}'\n")

      f.writelines(f"python rcv-simulation-jobs.py -location {location} -chaintype {chaintype} -mag_list '{mag_list}'\n")
      #f.writelines(f"python plots-by-model-combined.py {location} '{mag_list}'\n")


    os.system("sbatch -p batch job.sh")
    sleep(2)
    return

if __name__=="__main__":
    main()
