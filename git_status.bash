#!/bin/bash

# Define the absolute path to the Desktop directory
DESKTOP_DIR="/home/gerald-amiel/Desktop"

# List of directories to exclude
EXCLUDE_DIRS=("CAMISIM" "mhm2" "upcxx")

# Get the current date and time for commit messages
CURRENT_DATETIME=$(date +"%Y-%m-%d %H:%M:%S")

# File size limit in MB (GitHub hard limit is 100 MB per file)
SIZE_LIMIT_MB=100

# Convert size limit to bytes
SIZE_LIMIT_BYTES=$((SIZE_LIMIT_MB * 1024 * 1024))

# Function to check and handle large files
handle_large_files() {
    local dir="$1"

    # Find files larger than the limit
    large_files=$(find "$dir" -type f -size +"$SIZE_LIMIT_BYTES"c)
    if [[ -n "$large_files" ]]; then
        echo "Found large files in $dir exceeding ${SIZE_LIMIT_MB}MB:"
        echo "$large_files"

        # Install Git LFS if not already installed
        if ! command -v git-lfs &>/dev/null; then
            echo "Git LFS not found. Installing..."
            sudo apt update && sudo apt install -y git-lfs
            git lfs install
        fi

        # Track large files using Git LFS
        for file in $large_files; do
            echo "Tracking $file with Git LFS..."
            (cd "$dir" && git lfs track "$file")
        done

        # Commit the updated .gitattributes
        (cd "$dir" && git add .gitattributes && git commit -m "Track large files with Git LFS")
    fi
}

# Loop through each subdirectory in the Desktop directory
for dir in "$DESKTOP_DIR"/*/; do
    # Get the base name of the directory
    dirname=$(basename "$dir")

    # Check if the directory is in the exclude list
    if [[ " ${EXCLUDE_DIRS[@]} " =~ " $dirname " ]]; then
        echo "Skipping $dirname"
        continue
    fi

    # Check if the directory contains a .git folder
    if [ -d "$dir/.git" ]; then
        echo -e "\n--- Processing Git repository in $dirname ---"

        # Change to the repository directory
        (cd "$dir"

        # Check for large files
        handle_large_files "$dir"

        # Check the Git status
        git_status=$(git status --porcelain)
        if [[ -z "$git_status" ]]; then
            echo "No changes to commit in $dirname."
        else
            # Add all changes
            echo "Adding changes in $dirname..."
            git add .

            # Commit with timestamp message
            echo "Committing changes in $dirname..."
            git commit -m "Automated commit on $CURRENT_DATETIME"

            # Push to the remote repository
            echo "Pushing changes from $dirname..."
            git push
        fi
        )

        # Add a delay to avoid overwhelming resources or servers
        echo "Sleeping for 10 seconds..."
        sleep 10
    else
        echo "No .git repository found in $dirname. Skipping."
    fi
done
