# scripts/vcf_parser.py

import allel
import pandas as pd
import numpy as np

def load_vcf_subset(vcf_path, snp_ids):
    """
    Extracts genotypes for given rsIDs from a VCF file.

    Parameters:
    -----------
    vcf_path : str
        Path to the .vcf.gz file.
    snp_ids : list of str
        List of rsIDs to extract (e.g. ['rs121913529', 'rs61764370']).

    Returns:
    --------
    pd.DataFrame
        Genotype dosage matrix (samples x SNPs).
    """
    print(f"Loading VCF from {vcf_path} ...")
    try:
        vcf = allel.read_vcf(
            vcf_path,
            fields=["samples", "variants/ID", "calldata/GT"],
            alt_number=1
        )
    except Exception as e:
        print(f"❌ Error reading VCF: {e}")
        return None

    samples = vcf["samples"]
    variant_ids = vcf["variants/ID"]
    genotypes = vcf["calldata/GT"]

    # Mask for SNPs of interest
    snp_mask = np.isin(variant_ids, snp_ids)
    if not np.any(snp_mask):
        print("⚠️ No matching SNPs found in the VCF.")
        return None

    selected_ids = variant_ids[snp_mask]
    selected_genotypes = genotypes[:, snp_mask, :]

    # Convert genotype tuples to dosages (0, 1, 2)
    dosage = selected_genotypes.sum(axis=2)

    df = pd.DataFrame(dosage, columns=selected_ids, index=samples)
    print(f"✅ Loaded {df.shape[1]} SNPs across {df.shape[0]} samples.")

    return df