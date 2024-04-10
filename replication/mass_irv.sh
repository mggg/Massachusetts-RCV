#!/bin/bash

#SBATCH --time=05:00:00
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem=8G
#SBATCH --mail-type=NONE
#SBATCH --mail-user=NONE


num_districts=$1
num_seats=$2
cand_split=$3
n_elections=$4
output_file=$5
log_file=${6}

echo --num_districts "$num_districts"
echo --num_seats "$num_seats"
echo --cand_split "$even_split"
echo --n_elections "$n_elections"
echo --output_file "$output_file"
echo --log_file "$log_file"

{
    python simulate.py \
        --num_districts "$num_districts" \
        --num_seats "$num_seats" \
        --cand_split "$cand_split"
        --n_elections "$n_elections" \
} > "${output_file}"

sacct -j $SLURM_JOB_ID --format=JobID,JobName,Partition,State,ExitCode,Start,End,Elapsed,NCPUS,NNodes,NodeList,ReqMem,MaxRSS,AllocCPUS,Timelimit,TotalCPU >> "$log_file" 2>> "$log_file"
