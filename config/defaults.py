DEFAULT_ID_COLUMN_CANDIDATES = [
    "sample_id", "sampleid", "id", "sample id", "sample",
    "barcode", "specimen_id", "accession",
]

DEFAULT_NAME_COLUMN_CANDIDATES = [
    "sample_name", "name", "sample name", "description", "label",
]

DEFAULT_FUZZY_THRESHOLD = 80

DEFAULT_REFERENCE_EXTENSIONS = (".xlsx", ".xls", ".csv")

STRATEGY_LABELS = {
    "exact":      "Exact",
    "exact_norm": "Normalized Exact",
    "substring":  "Substring",
    "fuzzy":      "Fuzzy",
    "manual":     "Manual Override",
    "no_match":   "No Match",
}

UNMATCHED_REASONS = {
    "no_candidates":    "No similar IDs found in reference database",
    "below_threshold":  "Best fuzzy match score below threshold",
    "empty_id":         "Query ID is empty or missing",
}
