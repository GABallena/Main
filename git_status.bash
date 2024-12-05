#!/bin/bash

# Define the absolute path to the Desktop directory
DESKTOP_DIR="/home/gerald-amiel/Desktop"

# List of directories to exclude
EXCLUDE_DIRS=("CAMISIM" "mhm2" "upcxx")

# Get the current date and time for commit messages
CURRENT_DATETIME=$(date +"%Y-%m-%d %H:%M:%S")

# File size limit in MB (GitHub recommended)
SIZE_LIMIT_MB=100

# Loop through each subdirectory in the Desktop directory
for dir in "$DESKTOP_DIR"/*/; do
    dirname=$(basename "$dir")

    # Skip excluded directories
    if [[ " ${EXCLUDE_DIRS[@]} " =~ " $dirname " ]]; then
        echo "Skipping $dirname"
        continue
    fi

    # Check if directory is a git repository
    if [ -d "$dir/.git" ]; then
        echo -e "\n--- Processing Git repository in $dirname ---"

        # Change to repository directory
        (cd "$dir" || exit

        # Check if Git LFS is installed
        if ! command -v git-lfs &> /dev/null; then
            echo "Git LFS not found. Installing..."
            git lfs install
        fi

        # Find and handle large files
        large_files=$(find . -type f -size +"$((SIZE_LIMIT_MB * 1024 * 1024))"c)
        if [[ -n "$large_files" ]]; then
            echo "Large files detected (>${SIZE_LIMIT_MB}MB):"
            echo "$large_files"
            
            # Track large files with Git LFS
            echo "Setting up Git LFS tracking for large files..."
            for file in $large_files; do
                git lfs track "$file"
                git add .gitattributes
            done
        fi

        # Check status and commit
        git_status=$(git status --porcelain)
        if [[ -z "$git_status" ]]; then
            echo "No changes to commit in $dirname."
        else
            echo "Adding changes in $dirname..."
            git add --all .

            echo "Committing changes..."
            git commit -m "Automated commit on $CURRENT_DATETIME"

            echo "Pushing changes..."
            if ! git push; then
                echo "Push failed. You may need to setup Git LFS tracking manually:"
                echo "1. git lfs install"
                echo "2. git lfs track <large-file-pattern>"
                echo "3. git add .gitattributes"
                echo "4. git add <large-files>"
                echo "5. git commit -m 'Add large files via LFS'"
                echo "6. git push"
            fi
        fi
        )
    else
        echo "No .git repository found in $dirname. Skipping."
    fi
done