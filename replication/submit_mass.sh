#!/bin/bash

job_name="mass_irv_$(date '+%d-%m-%Y@%H:%M:%SET')"

max_concurrent_jobs=10

running_script_name="mass_irv.sh"

# ==================
# RUNNING PARAMETERS
# ==================

n_elections=100

output_dir="mass_output"
log_dir="mass_logs"


num_districts_array = ("40" "160" "8" "32")

num_seats_array = ("1" "1", "5", "5")

# Assign R/D candidates evenly or based on share
cand_splits = ("EVEN" "PP")


mkdir -p "${output_dir}"
mkdir -p "${log_dir}"

job_ids=()
job_index=0

echo "========================================================"
echo "The job name is: $job_name"
echo "========================================================"


# This function will generate a label for the log and output file
generate_file_label() {
    local num_seats="$1"
    local num_districts="$2"
    local cand_split="$3"
    local n_elections="$4"

    echo "seats_${num_seats// /-}"\
        "ndist_${num_districts// /-}"\
        "split_${cand_split// /-}"\
        "n_elec_${n_elections// /-}"\
        | tr ' ' '_'
}

for i in "${!num_districts_array[@]}"; do
for j in "${!cand_splits[@]}"; do
    num_districts="${num_districts_array[$i]}"
    num_seats="${num_seats_array[$i]}"
    cand_split="${cand_splits[$j]}"

    file_label=$(generate_file_label \
                "$num_seats" \
                "$num_districts" \
                "$cand_split" \
                "$n_elections"
            )
            
            log_file="${log_dir}/${file_label}.log"
            output_file="${output_dir}/${file_label}.txt"

    while [[ ${#job_ids[@]} -ge $max_concurrent_jobs ]] ; do
                # Check once per minute if there are any open slots
                sleep 60
                # We check for the job name, and make sure that squeue prints
                # the full job name up to 100 characters
                job_count=$(squeue --name=$job_name --Format=name:100 | grep $job_name | wc -l)
                if [[ $job_count -lt $max_concurrent_jobs ]]; then
                    break
                fi
            done

            # Some logging for the 
            for job_id in "${job_ids[@]}"; do
                if squeue -j $job_id 2>/dev/null | grep -q $job_id; then
                    continue
                else
                    job_ids=(${job_ids[@]/$job_id})
                    echo "Job $job_id has finished or exited."
                fi
            done

            # This output will be of the form "Submitted batch job 123456"
            job_output=$(sbatch --job-name=${job_name} \
                --output="${log_file}" \
                --error="${log_file}" \
                $running_script_name \
                    "$num_seats" \
                    "$num_districts" \
                    "$cand_split" \
                    "$n_elections" \
                    "$output_file" \
                    "$log_file"
            )
            # Extract the job id from the output. The awk command
            # will print the last column of the output which is
            # the job id in our case
            # 
            # Submitted batch job 123456
            #                     ^^^^^^
            job_id=$(echo "$job_output" | awk '{print $NF}')
            echo "Job output: $job_output"
            # Now we add the job id to the list of running jobs
            job_ids+=($job_id)
            # Increment the job index. Bash allows for sparse
            # arrays, so we don't need to worry about any modular arithmetic
            # nonsense
            job_index=$((job_index + 1))

done
done

printf "No more jobs need to be submitted. The queue is\n%s\n" "$(squeue --name=$job_name)"
# Check once per minute until the job queue is empty
while [[ ${#job_ids[@]} -gt 0 ]]; do
    sleep 60
    for job_id in "${job_ids[@]}"; do
        if squeue -j $job_id 2>/dev/null | grep -q $job_id; then
            continue
        else
            job_ids=(${job_ids[@]/$job_id})
            echo "Job $job_id has finished or exited."
        fi
    done

    job_ids=("${job_ids[@]}")
done

echo "All jobs have finished."