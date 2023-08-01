#!/bin/bash
#SBATCH --job-name=massachusetts_vanilla_160_5
#SBATCH --time=2-00:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem=64000
#SBATCH -o progress/massachusetts_vanilla_160_5.txt
#SBATCH -e progress/massachusetts_vanilla_160_5_e.txt
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=cricha10@tufts.edu

python vanilla-sim.py massachusetts 160 5 racial-basic
