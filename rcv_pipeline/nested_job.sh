#!/bin/bash
#SBATCH --job-name=massachusetts_tilted_0-40-0
#SBATCH --time=1-00:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem=16000
#SBATCH -o progress/massachusetts_tilted_0-40-0.txt
#SBATCH -e progress/massachusetts_tilted_0-40-0_e.txt
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=cricha10@tufts.edu

python rcv-simulation-jobs.py -location massachusetts -chaintype tilted -mag_list '[0, 40, 0]'
