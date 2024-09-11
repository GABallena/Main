import os

# Path to your Conda environments directory
conda_envs_path = "/home/gerald-amiel/miniconda3/envs"

# Path to your filtered Bioconda packages list
bioconda_only_list_path = "bioconda_only_packages.txt"

# Read Bioconda-only packages from the list
with open(bioconda_only_list_path, "r") as f:
    bioconda_packages = set(line.strip() for line in f.readlines())

# Function to remove binaries in the environment matching Bioconda packages
def remove_binaries(env_path, packages):
    bin_dir = os.path.join(env_path, "bin")
    if os.path.exists(bin_dir):
        for binary in os.listdir(bin_dir):
            # If the binary matches a Bioconda package, delete it
            for package in packages:
                if package in binary:
                    binary_path = os.path.join(bin_dir, binary)
                    try:
                        print(f"Removing {binary_path}...")
                        os.remove(binary_path)
                    except Exception as e:
                        print(f"Error removing {binary_path}: {e}")

# Loop through Conda environments and remove matching binaries
for env in os.listdir(conda_envs_path):
    env_path = os.path.join(conda_envs_path, env)
    if os.path.isdir(env_path):
        print(f"Processing environment: {env}")
        remove_binaries(env_path, bioconda_packages)

print("Cleanup completed.")
