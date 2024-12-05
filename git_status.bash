#!/bin/bash

# Define the absolute path to the Desktop directory
DESKTOP_DIR="/home/gerald-amiel/Desktop"

# List of directories to exclude
EXCLUDE_DIRS=("CAMISIM" "mhm2" "upcxx")

# Get the current date and time for commit messages
CURRENT_DATETIME=$(date +"%Y-%m-%d %H:%M:%S")

# File size limit in MB
SIZE_LIMIT_MB=100

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

        # Find files larger than the limit and exclude them
        large_files=$(find . -type f -size +"$((SIZE_LIMIT_MB * 1024 * 1024))"c)
        if [[ -n "$large_files" ]]; then
            echo "Skipping files larger than ${SIZE_LIMIT_MB}MB:"
            echo "$large_files"
            for file in $large_files; do
                git update-index --skip-worktree "$file"
            done
        fi

        # Check the Git status
        git_status=$(git status --porcelain)
        if [[ -z "$git_status" ]]; then
            echo "No changes to commit in $dirname."
        else
            # Add all changes except large files
            echo "Adding changes in $dirname, excluding large files..."
            git add --all .

            # Commit with timestamp message
            echo "Committing changes in $dirname..."
            git commit -m "Automated commit on $CURRENT_DATETIME"

            # Push to the remote repository
            echo "Pushing changes from $dirname..."
            git push
        fi
        )
    else
        echo "No .git repository found in $dirname. Skipping."
    fi
done
