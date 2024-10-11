import requests
from bs4 import BeautifulSoup
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

BIOCONDA_REPO_URL = "https://anaconda.org/bioconda/repo"

def setup_session():
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[524, 502, 503, 504], allowed_methods=["GET"])
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
            if not package_table:
                print("Package table not found on the page. Ending search.")
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

                    if any(old_date in updated_date for old_date in ["2019", "2018", "2017"]):
                        print(f"Package {package_name} last updated in {updated_date}. Stopping page processing.")
                        break  # Stop processing this page

                    matched = any(keyword.lower() in description.lower() for keyword in keywords)
                    if not matched:
                        print(f"No inclusion keywords matched for package: {package_name}")
                        continue

                    excluded = any(ex_keyword.lower() in description.lower() for ex_keyword in exclusion_keywords)
                    if excluded:
                        print(f"Exclusion keyword found in package: {package_name}. Skipping.")
                        continue

                    f.write(f"{package_name}\t{description}\t{updated_date}\n")
                    print(f"Added {package_name} to TSV file.")
                    
            page += 1
            time.sleep(5)  # Sleep to avoid hitting server-side rate limiting
        except requests.exceptions.Timeout:
            print(f"Timeout occurred for page {page}. Retrying...")
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error for page {page}: {e}")
            break
        except requests.exceptions.RequestException as e:
            print(f"Request failed for page {page}: {e}")
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
    "Solexa", "assembl", "synten", "HGT", "plasmid", "cluster", "MAG", "annotat", "refin", 
    "genom", "coding", "script", "taxon", "sequenc", "motif", "KEGG", "COG", "evolution",
    "model", "R", "pangenom", "pipeline", "Nextflow", "Snakemake",
    "alignment", "graph", "tensor", "informat", "algorithm", "geograph", "SV", "structural variant", 
    "phage", "vir", "bootstrap", "statist", "infer", "pathogen", "strain", "infect", "variant", 
    "non-coding", "correct", "quality", "transpos", "mobile gen", "HMM", "Hidden Markov", 
    "gene transfer", "translat", "contam", "compar", "GO term", "marker", "identif", "benchmark",
    "cross-validat", "core", "dynamic", "best", "targeted", "accurat", "pathogen", "AU", "calling",
    "reproducib", "epidem", "variant", "coverage", "resolution", "quantif", "parallel", "GPU", "loop",
    "GATK", "entropy", "indices", "flanking", "slurm"
]


exclusion_keywords = [
    "RNA-seq", "Nanopore", "PacBio", "single-cell", "sex", "long-read", "ONT", "-seq", "spectro", "format", "ITS",
    "amplicon", "ChIP", "cancer", "DESeq", "long read", "server", "SingleCell", "16S", "18S", "convert",
    "single cell", "client", "GALAXY", "Windows", "photo", "mitochondr", "plastid", "organel", "organ", "tumor",
    "chemi", "third gen", "Hi-C", "PCR", "polymerase", "circRNA", "small RNA", "primer", 
    "MinION", "Cytomet", "expression", "chrom", "mouse", "thaliana", "Affy", "DEG", "soma", "post-transcription",
    "post-translation", "Multi-Omics", "exon", "intron", "zebrafish", "elegans", "chicken", "yeast", "splicing",
    "plant", "data package", "growth-rate", "neuro", "mice", "cell-culture", "Brain", "cell-line", "social", "cell-cycle",
    "tandem", "oma", "diploid", "add", "RNA", "net", "antibody", "pneumophila", "MS", "cloud", "AWS", "hybrid", "spectro",
    "MS/MS", "LC/MS", "ancient", "cloud", "meta-omic", "sapiens", "Delayed", "Fluor", "fluor", "Qubit", "Elut", "1000 Genomes",
    "cytes", "cytol", "NMR", "Gender", "Cyto", "Enrichment", "GSEA", "engine", "resource consumption", "biob", "invasive", "mtDNA",
    "human", "OS", "interactome", "Interactome", "Drosophila", "scrofa", "Xenopus", "purpuratus", "taurus", "Anopheles", "Rattus", "Ligand",
    "filamentous", "Filamentous", "Blot", "Blotting", "Gel", "Electrophore", "Medical image", "CLIP", "genome database", "Browser",
    "image process", "HTTP", "string", "Lite", "disorder", "HTML", "date", "Clip", "cloning", "Influenza", "Arabidopsis", "probes",
    "Sanger", "melanogaster", "reactome", "plankton", "pigment.*", "Proteom,*", "Access", "IDE", "Assay", "Differential", "Epithelial",
    "Mesenchymal", "Timer", "QSEA", "paper", "leukemia", "fibroblasts", "Cell-Lines", "import", "arrays", "Wrapper", "utility", "supervised",
    "unsupervised", "Semi-Supervised", "Unsupervised", "Supervised", "FACS", "Candida", "polymorphic", "Digital", "fetal.*", "Bacillus", "Gallus",
    "Zea", "japonicus", "Pongo", "Caeno.*", "gallopovo", "domestica", "rerio", "musculus", "Bombyx", "to MeSH", "Example", "example", "Falcon",
    

    "metabol", "extracellular", "neural", "learning", "AI", "intelligen", "GUI", "interface", "web-base", 
    "ploidy", "homozyg", "transcriptom", "GWAS", "CRISPR", "lncRNA", "isotop", "No Summary", "methylation",
    "epigen", "-MS", "Biobb", "dock", "web", "binding", "tissue", "microarray", "barcod", "folding", 
    "intensit", "acylation", "epista", "mass", "implementation", "transcrip", "HLA", "immun", "structur",
    "tutorial", "protein-protein", "Design Info", "ATLAS", "UCSC", "GenBank", "pharmaco", "regulator", "transcription factor",
    "qPCR", "physical", "enrichment", "2bit", "crypto", "CLIP", "mlst", "Mlst", "long", "ribo" "cell cycle", "bisulfute",
    "Bisulfite", "Micro Array", "Pathway", "repositor", "V(D)J", "Regulat", "regulon", "NCBI", "methyl", "Regulon", "Ensembl",
    "Nxt", "T cell", "B cell", "oligomer", "Oligomer", "Isoform", "isoform", "TxDb", "promoter", "Methyl", "beads", "cellular",
    "cell-type", "Pathway", "Translation", "Transcription", "10X", "survival", "cohort", "lipid", "peptid", "nucleosome", "nuclear",
    "Redis", "ase", "long", "building", "DBBJ", "cgMLST", "ChIA", "oligomer", "Pore-C", "WBGS", "Submission", "API", "submission",
    "zyme", "convenien", "Proteom", "images", "plast" "Polishing", "polishing", "assay", "assays", "zenodo", "Dryad", "language",
    "endogenous", "pars", "writ", "compression", "utilities", "::", "wrapper", "Utilities", "Storage", "gene editing", "genome editing"
    "genomics", "Genomics", "SARS", "Excel", "accession.*", "helper", "library", "module", "modules", "interactive", "FTP", "library", 
    "DDBJ", "url", "hybrid.*", "YAML", "yaml", "FASTA", "FASTQ", "Center", "VCF", "vcf", "CAZ.*"
    
]

output_file = "bioconda_filtered_packages.tsv"

search_and_write_package_details(keywords, exclusion_keywords, output_file)
