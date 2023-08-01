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
    results = glob.glob(f"output/results/{location}-{mag_str}/{chaintype}*")
    nums = [int(num.split("/")[-1].split(f"{chaintype}-")[-1].split(".")[0]) for num in results]
    all_configs = glob.glob(f"configurations/{location}/*")
    for config in all_configs:
      config = config.split("/")[-1]       

      for i in range(1, 6):
        with open("rcv-job.sh", "w") as f:
          f.writelines("#!/bin/bash\n")
          f.writelines(f"#SBATCH --job-name={location}_{chaintype}_{config}_{mag_str}_{i}\n")
          f.writelines(f"#SBATCH --time=3-00:00:00\n")
          f.writelines(f"#SBATCH --nodes=1\n")
          f.writelines(f"#SBATCH --ntasks-per-node=1\n")
          f.writelines(f"#SBATCH --mem=16000\n")
          f.writelines(f"#SBATCH -o progress/{location}_{chaintype}_{config}_{mag_str}_{i}.txt\n")
          f.writelines(f"#SBATCH -e progress/{location}_{chaintype}_{config}_{mag_str}_{i}_e.txt\n")
          f.writelines(f"#SBATCH --mail-type=FAIL\n")
          f.writelines(f"#SBATCH --mail-user=cricha10@tufts.edu\n\n")
          f.writelines(f"python multi-config-simulation.py {location} {chaintype} {i} '{mag_list}' {config}\n")


        os.system("sbatch -p batch rcv-job.sh")
        #sleep(3)
    return

if __name__=="__main__":
    main()
