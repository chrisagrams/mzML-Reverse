from pin_parser import pin_to_df
from argparse import ArgumentParser
import numpy as np
import pandas as pd

parser = ArgumentParser()
parser.add_argument("input_pin")
args = parser.parse_args()

def update_protein_string(protein_str):
    """
    Process a single protein string by appending 'rev_' to each token.
    Expects the protein string to use semicolons as delimiters.
    """
    if pd.isnull(protein_str) or not isinstance(protein_str, str) or not protein_str.strip():
        return protein_str
    trailing = protein_str.endswith(";")
    proteins = [p for p in protein_str.split(";") if p]
    updated = ";".join("rev_" + p for p in proteins)
    if trailing:
        updated += ";"
    return updated

def update_proteins(protein_val):
    """
    Check if protein_val is a list. If so, process each element of the list.
    Otherwise, process the string directly.
    """
    if isinstance(protein_val, list):
        return [update_protein_string(p) for p in protein_val]
    else:
        return update_protein_string(protein_val)

if __name__ == "__main__":
    df = pin_to_df(args.input_pin)
    
    df["Label"] = np.where(df["ScanNr"] % 2 == 0, 1, -1)

    df.loc[df["Label"] == -1, "Proteins"] = df.loc[df["Label"] == -1, "Proteins"].apply(update_proteins)

    df.to_csv("output.tsv", sep="\t")