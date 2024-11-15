#!/bin/bash
# Define the absolute path to the Desktop directory
DESKTOP_DIR="/home/gerald-amiel/Desktop"

# List of directories to exclude
EXCLUDE_DIRS=("CAMISIM", "mhm2", "upcxx")

# Get the current date and time for commit messages
CURRENT_DATETIME=$(date +"%Y-%m-%d %H:%M:%S")

# Loop through each subdirectory in the Desktop directory
for dir in "$DESKTOP_DIR"/*/ ; do
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
