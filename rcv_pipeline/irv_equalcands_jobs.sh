#!/bin/bash
#SBATCH --job-name=massachusetts_equalcands_sims
#SBATCH --time=2-00:00:00
#SBATCH --nodes=1
#SBATCH --cpus-per-task=8
#SBATCH --ntasks-per-node=1
#SBATCH --mem=64000
#SBATCH --output=mass_equalcands.%j.out 
#SBATCH --error=mass_equalcands.%j.err
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=jgibso04@tufts.edu

module load anaconda/2021.05

source activate /cluster/tufts/mggg/jgibso04/condaenv/mass-rcv

python irv_simulation.py 40

python irv_simulation.py 160

python equal_cands.py 0-0-8 15

python equal_cands.py 0-0-32 15

python equal_cands.py 0-10-0 12

python equal_cands.py 0-40-0 12

conda deactivate