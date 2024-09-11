#!/bin/bash

# Step 0: Create env folder with yamls

[ ! -d env ] && mkdir env

for env in $(conda env list | awk '{print $1}' | tail -n +4); do
    echo "Exporting $env..."
    conda env export --name $env --no-builds > env/${env}.yaml
done

# Step 1: Check Dependencies
echo "Running check_dependencies.py..."
if python check_dependencies.py; then
    echo "check_dependencies.py completed successfully."
else
    echo "Error: check_dependencies.py encountered an issue." >&2
    exit 1
fi

# Step 2: Filter Dependencies with Bioconda Tools
echo "Running bioconda_tools.py..."
if python bioconda_tools.py; then
    echo "bioconda_tools.py completed successfully."
else
    echo "Error: bioconda_tools.py encountered an issue." >&2
    exit 1
fi

echo "Automation workflow completed!"
