import pandas as pd

df = pd.read_csv("/Users/samdonato/Desktop/SNPxCancer/data/raw/gwas-associations.tsv", sep="\t", low_memory=False)
print(f"Loaded {df.shape[0]} rows and {df.shape[1]} columns.")
print(df.columns.tolist())

cancer_df = df[df['DISEASE/TRAIT'].str.contains("cancer", case=False, na=False)]
print(f"Found {cancer_df.shape[0]} rows related to cancer.")


# Drop NaNs in the SNPs column
rsid_series = cancer_df['SNPS'].dropna()

# Split multiple rsIDs per entry and flatten
rsids = rsid_series.str.split(r'[,\s;]').explode()

# Remove entries that don't look like proper rsIDs (e.g. non-rs terms)
rsids = rsids[rsids.str.match(r'rs\d+')]

# Get unique ones
unique_rsids = rsids.drop_duplicates().sort_values().tolist()

print(f"Extracted {len(unique_rsids)} unique rsIDs related to cancer.")

with open("cancer_rsids.txt", "w") as f:
    for rsid in unique_rsids:
        f.write(f"{rsid}\n")