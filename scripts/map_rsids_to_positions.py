#! /usr/bin/env python3
"""
maps rsIDs to genomic positions using Ensembl REST API

Read a list of rdIDs (One per line) from a file and resolve them to GRCh37 coordinates
using the Ensembl REST API. Filter for variants in chr17 and save the results to a TSV file.

Input:
../cancer_rsids.txt
Outputs:
../data/processed/cancer_rsids_positions.tsv

Example output:
rs123456	1234567890	1234567890
rs345678	1234567890	1234567890
rs789012	1234567890	1234567890

"""

import sys
import time
import requests
import pandas as pd
from pathlib import Path

# ------- Configuration -------
INPUT_RSIDS_FILE = Path(__file__).parent.parent / "data/processed/cancer_rsids.txt"
OUTFILE_ALL = Path(__file__).parent.parent / "data/processed/cancer_rsids_all.tsv"
OUTFILE_CHR17 = Path(__file__).parent.parent / "data/processed/cancer_rsids_chr17.tsv"

ENSEMBL_BASE = "https://grch37.rest.ensembl.org"
VAR_ENDPOINT = "/variation/homo_sapiens/{rsid}?content-type=application/json"

SLEEP_EVERY = 20
SLEEP_SECS = 0.2

def fetch_rsid_info(rsid: str):
    """Query Ensembl REST for a single rdID."""
    url = ENSEMBL_BASE + VAR_ENDPOINT.format(rsid=rsid)
    r = requests.get(url, headers={"Content-Type": "application/json"})
    if not r.ok:
        print(f"❌ Error for rsID {rsid}: {r.text}")
        return None
    try:
        return r.json()
    except Exception:
        return None

def main():
    # make sure output dir exists
    Path("../data/processed").mkdir(parents=True, exist_ok=True)

    # read rsIDs
    with open(INPUT_RSIDS_FILE) as f:
        rsids = [line.strip() for line in f if line.strip()]

    print(f"Loaded {len(rsids)} rsIDs from {INPUT_RSIDS_FILE}")

    records = []
    for i, rsid in enumerate(rsids, start=1):
        data = fetch_rsid_info(rsid)
        if not data:
            continue

        # Ensembl can return multiple mappings (different assemblies, patches, etc.)
        mappings = data.get("mappings", [])
        for m in mappings:
            # we only want GRCh37 entries (should already be, since we're on grch37 REST)
            assembly = m.get("assembly_name")
            if assembly != "GRCh37":
                continue

            chrom = m.get("seq_region_name")
            pos = m.get("start")
            # Sometimes Ensembl returns non-numeric chromosomes (e.g. X, Y, MT) — that's fine.
            records.append(
                {
                    "rsid": rsid,
                    "chrom": str(chrom),
                    "pos": int(pos) if pos is not None else None,
                }
            )

        # be nice to the API
        if i % SLEEP_EVERY == 0:
            time.sleep(SLEEP_SECS)

    if not records:
        print("No records were retrieved from Ensembl. Exiting.")
        return

    df = pd.DataFrame(records).dropna(subset=["pos"])
    df = df.drop_duplicates(subset=["rsid", "chrom", "pos"]).sort_values(["chrom", "pos"])
    df.to_csv(OUTFILE_ALL, sep="\t", index=False)
    print(f"✅ Saved ALL mapped rsIDs to: {OUTFILE_ALL} (n={len(df)})")

    # filter to chr17 only (because your 1000G VCF is chr17)
    df_chr17 = df[df["chrom"] == "17"].copy().sort_values("pos")
    df_chr17.to_csv(OUTFILE_CHR17, sep="\t", index=False)
    print(f"✅ Saved chr17-only rsIDs to: {OUTFILE_CHR17} (n={len(df_chr17)})")


if __name__ == "__main__":
    main()