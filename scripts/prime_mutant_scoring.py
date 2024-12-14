import torch
from transformers import AutoTokenizer, AutoModel
import pandas as pd
from Bio import SeqIO
from pathlib import Path

def read_seq(seq_file):
    """
    Read the first sequence from a FASTA file.
    """
    for record in SeqIO.parse(seq_file, "fasta"):
        return str(record.seq)

def generate_mutants(sequence):
    """
    Generate all possible single-point mutants for a given sequence.
    """
    amino_acids = "ACDEFGHIKLMNPQRSTVWY"  # All possible amino acids
    mutants = []
    for i, wt in enumerate(sequence):
        for mt in amino_acids:
            if wt != mt:  # Exclude the wild-type residue
                mutants.append(f"{wt}{i+1}{mt}")
    return mutants

@torch.no_grad()
def score_auto(fasta, model, tokenizer, device):
    """
    Automatically generate mutants and compute scores.
    """
    # Read the wild-type sequence
    sequence = read_seq(fasta)
    
    # Generate mutants
    mutants = generate_mutants(sequence)
    
    # Tokenize the sequence
    tokenized_results = tokenizer(sequence, return_tensors="pt")
    input_ids = tokenized_results.input_ids.to(device)
    attention_mask = tokenized_results.attention_mask.to(device)
    
    # Compute logits
    logits = model(input_ids, attention_mask=attention_mask).logits[0, 1:-1, :].log_softmax(dim=-1)
    scores = []

    # Compute scores for each mutant
    for mutant in mutants:
        wt, idx, mt = mutant[0], int(mutant[1:-1]) - 1, mutant[-1]
        score = (logits[idx, tokenizer.get_vocab()[mt]] - logits[idx, tokenizer.get_vocab()[wt]]).item()
        scores.append((mutant, score))
    
    # Convert to DataFrame
    df = pd.DataFrame(scores, columns=["mutant", "predict_score"])
    return df

def main(sequence_folder, output_folder, model_path="AI4Protein/Prime_690M"):
    """
    Main function to process multiple FASTA files and score their mutants.
    """
    # Initialize the model and tokenizer
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = AutoModel.from_pretrained(model_path, trust_remote_code=True).to(device)
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    model.eval()

    # Ensure output folder exists
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    # Process all FASTA files in the sequence folder
    sequence_folder = Path(sequence_folder)
    for fasta_file in sequence_folder.glob("*.fasta"):
        stem = fasta_file.stem
        try:
            # Generate and score mutants
            df = score_auto(fasta_file, model, tokenizer, device)
            
            # Save the results
            output_file = output_folder / f"{stem}_auto.csv"
            df.to_csv(output_file, index=False)
            print(f"Processed {stem}, results saved to {output_file}")
        except Exception as e:
            print(f"Error processing {stem}: {e}")

if __name__ == "__main__":
    import argparse

    # Set up command-line arguments
    parser = argparse.ArgumentParser(description="Generate and score protein mutants using the PRIME model.")
    parser.add_argument("--sequence_folder", type=str, required=True, help="Path to folder containing FASTA files.")
    parser.add_argument("--output_folder", type=str, required=True, help="Path to save output CSV files.")
    parser.add_argument("--model_path", type=str, default="AI4Protein/Prime_690M", help="Path to the pretrained PRIME model.")
    args = parser.parse_args()

    # Run the main function
    main(args.sequence_folder, args.output_folder, args.model_path)
