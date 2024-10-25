import requests
from bs4 import BeautifulSoup
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

BIOCONDA_REPO_URL = "https://anaconda.org/bioconda/repo"

def setup_session():
    session = requests.Session()
    retries = Retry(
        total=5, 
        backoff_factor=2,  # Gradual backoff
        status_forcelist=[524, 502, 503, 504], 
        allowed_methods=["GET"]
    )
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    return session

def fetch_package_details(session, keywords, exclusion_keywords, output_file):
    page = 1
    while True:
        try:
            print(f"Searching page {page}...")
            response = session.get(f"{BIOCONDA_REPO_URL}?page={page}", timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            package_table = soup.find('table')
            
            # Stop if no more packages are found on the page
            if not package_table:
                print("No more packages found. Ending search.")
                break

            with open(output_file, "a") as f:
                for row in package_table.find_all('tr')[1:]:  # Skip header row
                    columns = row.find_all('td')
                    if len(columns) < 4:
                        continue  # Skip rows that do not have enough columns

                    package_name = columns[0].find('a').text.strip()
                    description = columns[2].text.strip() if len(columns) > 2 else "No description available"
                    updated_date = columns[3].text.strip() if len(columns) > 3 else "No date available"

                    print(f"Processing package: {package_name}")

                    # Stop processing if an outdated package is encountered
                    if any(year in updated_date for year in ["2019", "2018", "2017"]):
                        print(f"Package {package_name} last updated in {updated_date}. Skipping remaining pages.")
                        return  # Exit the function if outdated packages are found

                    if not any(keyword.lower() in description.lower() for keyword in keywords):
                        print(f"No relevant keywords found for: {package_name}")
                        continue

                    if any(ex_keyword.lower() in description.lower() for ex_keyword in exclusion_keywords):
                        print(f"Exclusion keyword found in {package_name}. Skipping.")
                        continue

                    f.write(f"{package_name}\t{description}\t{updated_date}\n")
                    print(f"Added {package_name} to TSV file.")
                    
            page += 1
            time.sleep(5)  # Avoid rate-limiting

        except requests.exceptions.Timeout:
            print(f"Timeout occurred for page {page}. Retrying...")
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error for page {page}: {e}")
            break
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            break

def search_and_write_package_details(keywords, exclusion_keywords, output_file):
    # Open and write the header of the TSV file
    with open(output_file, "w") as f:
        f.write("Package_Name\tDescription\tUpdated_Date\n")

    session = setup_session()
    fetch_package_details(session, keywords, exclusion_keywords, output_file)

# Example usage
keywords = [
    "phylo", "k-mer", "populat", "metagen", "antimicrob", "antibio", "resistance",
    "ortholog", "paralog", "Bayesian", "trim", "read", "mapp", "CARD", "AMR", "Illumina",
    "assembl", "cluster", "MAG", "genom", "pipeline", "alignment", "graph", "tensor",
    "informat", "algorithm", "geograph", "phage", "bootstrap", "statist", "pathogen",
    "quantif", "GPU", "loop", "GATK", "flanking", "slurm"
]

exclusion_keywords = [
    "RNA-seq", "Nanopore", "PacBio", "long-read", "cancer", "16S", "ITS", "single-cell",
    "PCR", "MinION", "server", "Windows", "plant", "mouse", "neural", "epigen", "soma",
    "chrom", "CRISPR", "expression", "cell-culture", "library", "API", "tissue", "MinION"
]

output_file = "bioconda_filtered_packages.tsv"

search_and_write_package_details(keywords, exclusion_keywords, output_file)
