# SNPxCancer
Machine learning project using 1000 Genomes data to classify populations and explore cancer-associated SNPs

Workflow

1️⃣ Repository Setup & Environment

Repo: SNPxCancer￼
	•	Purpose: Integrate open-source genomic data (1000 Genomes + GWAS Catalog) to explore genetic variants associated with cancer and prepare features for machine learning models.
	•	Core environment:
	•	Python 3.13 + virtual environment (.venv)
	•	Key dependencies: pandas, numpy, scikit-allel, dask
	•	Folder structure:

data/
  raw/          # Unmodified downloaded data
  processed/    # Filtered, subsetted, or reformatted data
notebooks/      # Jupyter notebooks for testing and exploration
scripts/        # Reusable code modules and analysis scripts
results/        # Output figures, tables, and reports

2️⃣ Acquisition of 1000 Genomes Data
	Source: International Genome Sample Resource (1000 Genomes Phase 3)￼
	•	Downloaded files (chromosome 17):
ALL.chr17.phase3_shapeit2_mvncall_integrated_v5b.20130502.genotypes.vcf.gz
ALL.chr17.phase3_shapeit2_mvncall_integrated_v5b.20130502.genotypes.vcf.gz.tbi

	•	Why chr17?
It includes key cancer-associated genes such as BRCA1 and TP53.
	•	Location: data/raw/


3️⃣ VCF Parsing and Testing
	•	Script: scripts/vcf_parser.py
	•	Loads and inspects VCFs using scikit-allel / pysam.
	•	Handles compressed .vcf.gz files and indexing via .tbi.
	•	Designed for modular reuse in filtering and genotype-matrix generation.
	•	Notebook: notebooks/01_test_vcf_parser.ipynb
	•	Demonstrates VCF loading and header exploration on a small subset.
	•	Validates that environment and dependencies are configured correctly.

4️⃣ Retrieval of Cancer-Associated SNPs
	•	Source: GWAS Catalog, EMBL-EBI￼
	•	Downloaded “All Associations v1.0 (TSV)” file
        → gwas-associations.tsv
	•	Purpose: Identify rsIDs (SNPs) linked to cancer-related traits.

5️⃣ rsID Extraction Pipeline
	•	Script: scripts/rsIDs_for_cancer.py
	•	Loads gwas-associations.tsv
	•	Filters the DISEASE/TRAIT column for “cancer” (case-insensitive)
	•	Parses and normalizes all SNP identifiers from the SNPS column
	•	Removes duplicates and non-rs entries
	•	Saves unique rsIDs → cancer_rsids.txt
• Output Example:
rs123456
rs345678
rs789012

•	Location: data/processed/


6️⃣ Version Control & Documentation
	•	All scripts and data management steps committed to GitHub with clear messages.
	•	README and code comments document sources and rationale for each stage.


⚙️ Next Planned Phase (Phase II — Analysis & Modeling)
	1.	Map rsIDs → genomic coordinates (GRCh37) using Ensembl REST.
	The Ensembl REST gave errors given the size of rsIDs so downloads of the variant database were made to the local disk with the following commands

cd data/raw
wget ftp://ftp.ensembl.org/pub/grch37/current/variation/vcf/homo_sapiens/homo_sapiens-chr17.vcf.gz
wget ftp://ftp.ensembl.org/pub/grch37/current/variation/vcf/homo_sapiens/homo_sapiens-chr17.vcf.gz.csi

Used map_rsids_chr17.sh to map

Workflow outline 
SNPxCancer Project — Session Summary (Chromosome 17 Variant Mapping Workflow)
	•	Pivoted the workflow from API-based rsID mapping (Ensembl REST) to a fully offline, reproducible workflow using Ensembl GRCh37 VCF data.
	•	Inspected the Ensembl FTP structure to identify available per-chromosome variant reference files.
	•	Chose chromosome 17 as the focus dataset (oncology relevance – TP53, BRCA1, ERBB2 loci).
	•	Downloaded reference variant catalog:
	•	homo_sapiens-chr17.vcf.gz and its index .csi from Ensembl GRCh37.
	•	Confirmed these contain all rsIDs and coordinates for chr17.
	•	Verified that this approach eliminates the need for the large whole-genome variant file.
	•	Confirmed existing 1000 Genomes chr17 genotypes (ALL.chr17.phase3_shapeit2_mvncall_integrated_v5b.20130502.genotypes.vcf.gz) as the complementary dataset.
	•	Created a bash pipeline (scripts/map_rsids_chr17.sh) to:
	•	Filter the Ensembl chr17 VCF by a list of cancer-associated rsIDs (cancer_rsids.txt).
	•	Output a clean coordinate table cancer_rsids_chr17.tsv (rsID → chromosome → position).
	•	Optionally build .regions and subset the 1000 Genomes VCF.
	•	Installed bcftools via Homebrew for high-speed, offline variant querying.
	•	Executed the mapping script successfully, producing data/processed/cancer_rsids_chr17.tsv, a verified list of cancer-related variants mapped to chr17 coordinates.
	•	Validated reproducibility and data hygiene:
	•	Added .gitignore rules to exclude large .vcf and .gz files from Git.
	•	Retained directory structure with .gitkeep.

Next Steps

	2.	Subset the 1000 Genomes chr17 VCF to include only cancer-relevant variants.
	3.	Generate genotype matrices (samples × variants).
	4.	Annotate variants via ClinVar or Ensembl VEP.
	5.	Engineer features + train ML models predicting cancer association patterns.









Need to add a fetch script for 