import requests
import yaml
import os

# Directory containing the YAML files
yaml_dir = "env/"

# Function to check if the package exists on Bioconda
def check_bioconda_package(dependency):
    package_url = f"https://bioconda.github.io/recipes/{dependency}/README.html#package-{dependency}"
    print(f"Checking {package_url}")
    
    response = requests.get(package_url)
    
    # If the page exists (status code 200), consider it a Bioconda package
    if response.status_code == 200:
        print(f"{dependency} is a Bioconda package.")
        return True
    else:
        print(f"{dependency} is NOT a Bioconda package.")
        return False

# Function to collect unique dependencies from the YAML files
def collect_unique_dependencies(yaml_dir):
    unique_dependencies = set()
    
    for yaml_file in os.listdir(yaml_dir):
        if yaml_file.endswith(".yaml"):
            print(f"Processing {yaml_file}...")
            dependencies = parse_yaml_for_dependencies(os.path.join(yaml_dir, yaml_file))
            unique_dependencies.update(dependencies)
    
    return unique_dependencies

# Function to parse the dependencies from a YAML file
def parse_yaml_for_dependencies(yaml_file):
    with open(yaml_file) as f:
        environment = yaml.safe_load(f)
    
    dependencies = environment.get('dependencies', [])
    parsed_dependencies = []
    
    for dep in dependencies:
        if isinstance(dep, str):
            # Handle simple string dependencies
            parsed_dependencies.append(dep.split('=')[0])
        elif isinstance(dep, dict):
            # Handle dictionaries (sometimes conda has complex dependencies)
            for key in dep.keys():
                parsed_dependencies.append(key)
    
    return parsed_dependencies

# Main function to check if each dependency is in Bioconda and output only Bioconda ones to a file
def main():
    unique_dependencies = collect_unique_dependencies(yaml_dir)
    
    # Prepare the output file
    with open('bioconda_only_packages.txt', 'w') as outfile:
        for dependency in unique_dependencies:
            if check_bioconda_package(dependency):
                outfile.write(f"{dependency}\n")
    
    print("Finished writing Bioconda packages to bioconda_only_packages.txt.")

if __name__ == "__main__":
    main()
