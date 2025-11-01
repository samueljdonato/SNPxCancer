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
	2.	Subset the 1000 Genomes chr17 VCF to include only cancer-relevant variants.
	3.	Generate genotype matrices (samples × variants).
	4.	Annotate variants via ClinVar or Ensembl VEP.
	5.	Engineer features + train ML models predicting cancer association patterns.