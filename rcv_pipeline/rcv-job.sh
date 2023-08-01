#!/bin/bash
#SBATCH --job-name=massachusetts_tilted_racial-w90c60_0-40-0_5
#SBATCH --time=3-00:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem=16000
#SBATCH -o progress/massachusetts_tilted_racial-w90c60_0-40-0_5.txt
#SBATCH -e progress/massachusetts_tilted_racial-w90c60_0-40-0_5_e.txt
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=cricha10@tufts.edu

python multi-config-simulation.py massachusetts tilted 5 '[0, 40, 0]' racial-w90c60
