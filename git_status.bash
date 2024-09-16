#!/bin/bash
# Define the absolute path to the Desktop directory
DESKTOP_DIR="/home/gerald-amiel/Desktop"

# List of directories to exclude
EXCLUDE_DIRS=("CAMISIM")

# Loop through each subdirectory in the Desktop directory
for dir in "$DESKTOP_DIR"/*/ ; do
    # Get the base name of the directory
    dirname=$(basename "$dir")

    # Check if the directory is in the exclude list
    if [[ " ${EXCLUDE_DIRS[@]} " =~ " $dirname " ]]; then
        echo "Skipping $dirname"
        continue
    fi

    # If the directory contains a .git folder, check the Git status
    if [ -d "$dir/.git" ]; then
        echo "Checking Git status in $dir"
        (cd "$dir" && git status)
    fi
done
