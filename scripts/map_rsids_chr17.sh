#!/usr/bin/env bash
# Map rsIDs -> (chr,pos) on GRCh37 using Ensembl's chr17 reference VCF.
# Requires: bcftools, tabix

set -euo pipefail

# -------- defaults (repo layout) --------
RSIDS_FILE="data/processed/cancer_rsids.txt"                  # one rsID per line
REF_VCF="data/raw/homo_sapiens-chr17.vcf.gz"                  # Ensembl GRCh37 chr17 variant catalog
OUT_TSV="data/processed/cancer_rsids_chr17.tsv"               # rsid \t chrom \t pos
MAKE_REGIONS=false                                            # also emit a bcftools -R regions file
REGIONS_FILE="data/processed/cancer_rsids_chr17.regions"      # chrom \t start-end
SUBSET_1000G=""                                               # optional: path to 1000G chr17 VCF to subset
OUT_SUBSET="data/processed/chr17_cancer_variants.vcf.gz"

usage() {
  cat <<EOF
Usage: $0 [-r RSIDS_FILE] [-v REF_VCF] [-o OUT_TSV] [--make-regions]
          [--subset-1000g PATH_TO_1000G_CHR17_VCF] [--out-subset OUT_VCF_GZ]

Defaults:
  -r ${RSIDS_FILE}
  -v ${REF_VCF}
  -o ${OUT_TSV}

Flags:
  --make-regions                  Produce regions file: ${REGIONS_FILE}
  --subset-1000g <vcf.gz>         Also subset the 1000 Genomes chr17 VCF to mapped positions
  --out-subset <vcf.gz>           Output path for subset VCF (default: ${OUT_SUBSET})
EOF
}

# -------- parse args --------
while [[ $# -gt 0 ]]; do
  case "$1" in
    -r|--rsids) RSIDS_FILE="$2"; shift 2;;
    -v|--ref) REF_VCF="$2"; shift 2;;
    -o|--out) OUT_TSV="$2"; shift 2;;
    --make-regions) MAKE_REGIONS=true; shift 1;;
    --subset-1000g) SUBSET_1000G="$2"; shift 2;;
    --out-subset) OUT_SUBSET="$2"; shift 2;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown arg: $1"; usage; exit 1;;
  esac
done

# -------- checks --------
command -v bcftools >/dev/null 2>&1 || { echo "bcftools not found"; exit 1; }
command -v tabix >/dev/null 2>&1 || { echo "tabix not found"; exit 1; }

[[ -f "$RSIDS_FILE" ]] || { echo "Missing rsIDs file: $RSIDS_FILE"; exit 1; }
[[ -f "$REF_VCF" ]] || { echo "Missing reference VCF: $REF_VCF"; exit 1; }

# Ensure reference VCF is indexed (.tbi or .csi)
if [[ ! -f "${REF_VCF}.tbi" && ! -f "${REF_VCF}.csi" ]]; then
  echo "Index not found for $REF_VCF — building with tabix..."
  tabix -p vcf "$REF_VCF"
fi

mkdir -p "$(dirname "$OUT_TSV")"

# -------- map rsIDs -> (chr,pos) --------
# Filters the reference VCF by rsID list and emits a coordinate table.
# The Ensembl chr17 VCF is already restricted to chr17, so no -r needed.
echo "Mapping rsIDs using $REF_VCF ..."
bcftools view \
  -i "ID=@${RSIDS_FILE}" \
  "$REF_VCF" \
  -Ou \
| bcftools query -f '%ID\t%CHROM\t%POS\n' \
> "$OUT_TSV"

echo "Wrote $(wc -l < "$OUT_TSV" | tr -d ' ') rows to $OUT_TSV"

# -------- optional: regions file --------
if $MAKE_REGIONS; then
  mkdir -p "$(dirname "$REGIONS_FILE")"
  # chrom \t start-end (POS-POS), suitable for bcftools -R
  awk 'BEGIN{OFS="\t"} {print $2, $3"-"$3}' "$OUT_TSV" > "$REGIONS_FILE"
  echo "Wrote regions file: $REGIONS_FILE"
fi

# -------- optional: subset 1000G chr17 --------
if [[ -n "$SUBSET_1000G" ]]; then
  [[ -f "$SUBSET_1000G" ]] || { echo "Missing 1000G VCF: $SUBSET_1000G"; exit 1; }
  # Ensure 1000G VCF is indexed
  if [[ ! -f "${SUBSET_1000G}.tbi" && ! -f "${SUBSET_1000G}.csi" ]]; then
    echo "Index not found for $SUBSET_1000G — building with tabix..."
    tabix -p vcf "$SUBSET_1000G"
  fi
  # If regions not already created, generate on the fly
  TMP_REG="$(mktemp)"
  awk 'BEGIN{OFS="\t"} {print $2, $3"-"$3}' "$OUT_TSV" > "$TMP_REG"

  mkdir -p "$(dirname "$OUT_SUBSET")"
  bcftools view \
    -R "$TMP_REG" \
    -Oz -o "$OUT_SUBSET" \
    "$SUBSET_1000G"
  tabix -p vcf "$OUT_SUBSET"
  echo "Wrote subset VCF: $OUT_SUBSET"

  rm -f "$TMP_REG"
fi