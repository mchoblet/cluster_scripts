#!/bin/bash

"""
mchoblet, 04.11.24
bashscript to recursively compress all files in a given folder.
checks for compression inorder to not recompress files.
"""


#SBATCH --account=bsmfc
#SBATCH --job-name=compress
#SBATCH --time=48:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=64GB
#SBATCH --partition=shared
#SBATCH --output=compress.log

module purge
module load EasyBuild/2023a
module load NCO 

# Function to check if a file is compressed and compress if needed
compress_file() {
    local file="$1"
    
    # Check if file is already compressed
    is_compressed=$(ncks --hdn --cdl -M "$file" | grep -E "deflate_level|deflate shuffle")

    if [[ -z "$is_compressed" ]]; then
        start_time=$(date +%s)
        
        # Create a temporary compressed file
        tmp_file="${file}.tmp.nc"
        ncks -4 -L 4 "$file" -o "$tmp_file"
        
        # Check if compression was successful
        if [[ $? -eq 0 ]]; then
            # Replace the original file with the compressed one
            mv "$tmp_file" "$file"
            end_time=$(date +%s)
            
            # Calculate the time taken
            time_taken=$((end_time - start_time))
            echo "File $file compressed successfully in $time_taken seconds."
        else
            rm -f "$tmp_file"
        fi
    fi
}

# Check if at least one directory is passed
if [[ $# -eq 0 ]]; then
    echo "Error: No directories provided."
    exit 1
fi

# Loop through all directories provided as arguments
for target_directory in "$@"; do
    # Check if directory exists
    if [[ ! -d "$target_directory" ]]; then
        echo "Error: Directory $target_directory does not exist."
        continue
    fi

    # Loop through all .nc files in the current target directory
    for file in "$target_directory"/*.nc; do
        if [[ -f "$file" ]]; then
            compress_file "$file"
        fi
    done
done

