#!/bin/bash

# Step 1: Check Dependencies
echo "Running check_dependencies.py..."
if python check_dependencies.py | tee check_dependencies_output.log | tee -a check_dependencies_error.log >&2; then
    echo "check_dependencies.py completed successfully."
else
    echo "Error: check_dependencies.py encountered an issue. Check check_dependencies_error.log for details." >&2
    exit 1
fi

# Step 2: Filter Dependencies with Bioconda Tools
echo "Running bioconda_tools.py..."
if python bioconda_tools.py | tee bioconda_tools_output.log | tee -a bioconda_tools_error.log >&2; then
    echo "bioconda_tools.py completed successfully."
else
    echo "Error: bioconda_tools.py encountered an issue. Check bioconda_tools_error.log for details." >&2
    exit 1
fi

# Step 3: Clean up Binaries based on Bioconda tools
echo "Running cleanup_binaries.py..."
if python cleanup_binaries.py | tee cleanup_binaries_output.log | tee -a cleanup_binaries_error.log >&2; then
    echo "cleanup_binaries.py completed successfully."
else
    echo "Error: cleanup_binaries.py encountered an issue. Check cleanup_binaries_error.log for details." >&2
    exit 1
fi

# Step 4: Create Aliases for Bioinformatics Tools
echo "Running create_aliases.py..."
if python create_aliases.py | tee create_aliases_output.log | tee -a create_aliases_error.log >&2; then
    echo "create_aliases.py completed successfully."
else
    echo "Error: create_aliases.py encountered an issue. Check create_aliases_error.log for details." >&2
    exit 1
fi

# Step 5: Source the updated bashrc to apply aliases
echo "Sourcing ~/.bashrc to apply aliases..."
if source ~/.bashrc; then
    echo "~/.bashrc sourced successfully."
else
    echo "Error: Unable to source ~/.bashrc." >&2
    exit 1
fi

echo "Automation workflow completed!"

