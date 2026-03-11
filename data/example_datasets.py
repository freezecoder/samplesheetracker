"""
Challenging example datasets for testing the Sample Sheet Tracker.

Each dataset is a dict with:
    name        — display name shown in the UI selectbox
    description — short blurb explaining the scenario
    ref_df      — pd.DataFrame (the reference database)
    query_df    — pd.DataFrame (the query sheet)
    ref_id_col  — column name for IDs in ref_df
    ref_name_col— column name for names in ref_df (or None)
    query_id_col— column name for IDs in query_df
    challenges  — list[str] of bullet-point notes on what makes this hard
"""
from __future__ import annotations

import pandas as pd


# =============================================================================
# Dataset 1 — Genomics Run (96-well plate)
# =============================================================================
# Reference: clean GNM-2024-NNN IDs with batch/type metadata
# Query: 30 IDs from multiple instruments/operators, with all sorts of chaos

def _make_genomics() -> dict:
    import random
    random.seed(42)

    tissues = ["Liver", "Kidney", "Brain", "Lung", "Heart", "Spleen", "Thymus", "Bone Marrow"]
    batches = ["BATCH-A", "BATCH-B", "BATCH-C"]

    ref_rows = []
    for i in range(1, 61):
        ref_rows.append({
            "SampleID":   f"GNM-2024-{i:03d}",
            "SampleName": f"{random.choice(tissues)}-{i:03d}",
            "Batch":      random.choice(batches),
            "Type":       random.choice(["WGS", "WES", "RNA-seq", "ATAC-seq"]),
            "Concentration_ng_uL": round(random.uniform(10.0, 250.0), 1),
        })
    ref_df = pd.DataFrame(ref_rows)

    # Build a challenging query with 30 IDs
    query_rows = [
        # Perfect match
        {"QueryID": "GNM-2024-001", "Source": "Instrument-A"},
        {"QueryID": "GNM-2024-002", "Source": "Instrument-A"},
        # Case difference
        {"QueryID": "gnm-2024-010", "Source": "Operator-1"},
        {"QueryID": "GNM-2024-015", "Source": "Operator-2"},
        # Dash → underscore (common Excel auto-format issue)
        {"QueryID": "GNM_2024_020", "Source": "Exported-CSV"},
        {"QueryID": "GNM_2024_025", "Source": "Exported-CSV"},
        # No separators at all (LIMS export quirk)
        {"QueryID": "GNM2024030", "Source": "LIMS-Export"},
        {"QueryID": "GNM2024035", "Source": "LIMS-Export"},
        # Missing leading zero on last segment
        {"QueryID": "GNM-2024-5",  "Source": "Manual-Entry"},
        {"QueryID": "GNM-2024-8",  "Source": "Manual-Entry"},
        # Single character typo
        {"QueryID": "GNM-2024-041", "Source": "Sequencer-B"},   # should match 041
        {"QueryID": "GNM-2O24-042", "Source": "Sequencer-B"},   # O vs 0
        # Transposed digits
        {"QueryID": "GNM-2024-054", "Source": "Manual-Entry"},  # 054 exact
        {"QueryID": "GNM-2024-504", "Source": "Manual-Entry"},  # 504 → fuzzy to 054?
        # Extra lab prefix added by downstream system
        {"QueryID": "LAB_GNM-2024-045", "Source": "Downstream-LIMS"},
        {"QueryID": "SEQ_GNM-2024-050", "Source": "Downstream-LIMS"},
        # Mixed case + extra spaces (copy-paste from PDF report)
        {"QueryID": "  GNM - 2024 - 055  ", "Source": "PDF-Export"},
        {"QueryID": " Gnm-2024-060 ",        "Source": "PDF-Export"},
        # Hyphen vs space
        {"QueryID": "GNM 2024 033", "Source": "Instrument-C"},
        # Correct but with trailing/leading underscores
        {"QueryID": "_GNM-2024-038_", "Source": "Scripted-Pipeline"},
        # Genuinely absent from reference
        {"QueryID": "GNM-2024-999", "Source": "Unknown"},
        {"QueryID": "CTRL-POS-001", "Source": "Control"},
        {"QueryID": "CTRL-NEG-001", "Source": "Control"},
        {"QueryID": "WATER-BLANK",  "Source": "Control"},
        # Completely wrong system
        {"QueryID": "PT-ALPHA-001", "Source": "Wrong-DB"},
        # Numeric only
        {"QueryID": "2024001",      "Source": "Numeric-LIMS"},
        # Unicode lookalike (common in copy-paste from PDFs)
        {"QueryID": "GNM‐2024‐003", "Source": "PDF-Unicode"},  # non-breaking hyphen
        # Blank / null
        {"QueryID": "",             "Source": "Missing"},
        {"QueryID": "N/A",          "Source": "Missing"},
        {"QueryID": "GNM-2024-022", "Source": "Instrument-A"},
    ]
    query_df = pd.DataFrame(query_rows)

    return {
        "name":         "Genomics Run — 96-Well Plate",
        "description":  "60-sample reference from a sequencing run. Query contains IDs from "
                        "5 different instruments/operators, each introducing different formatting "
                        "errors: dash/underscore swaps, missing leading zeros, typos, extra "
                        "prefixes, unicode hyphens, and control samples not in the database.",
        "ref_df":       ref_df,
        "query_df":     query_df,
        "ref_id_col":   "SampleID",
        "ref_name_col": "SampleName",
        "query_id_col": "QueryID",
        "challenges": [
            "Dash ↔ underscore ↔ no-separator variants of the same ID",
            "Missing leading zeros (GNM-2024-5 vs GNM-2024-005)",
            "Unicode non-breaking hyphens from PDF copy-paste",
            "Operator-added prefixes (LAB_, SEQ_)",
            "Control samples (CTRL-POS, WATER-BLANK) that should not match",
            "Empty and 'N/A' entries",
            "Transposed digits (504 vs 054)",
        ],
    }


# =============================================================================
# Dataset 2 — Clinical Trial Specimens
# =============================================================================
# Reference: structured PT-COHORT-NNN IDs across two cohorts
# Query: typical clinical data quality issues — word order, abbreviations, blanks

def _make_clinical() -> dict:
    cohorts = {
        "ALPHA": ("Liver biopsy", 30),
        "BETA":  ("Blood draw", 25),
        "GAMMA": ("CSF", 15),
    }

    ref_rows = []
    for cohort, (tissue, count) in cohorts.items():
        for i in range(1, count + 1):
            ref_rows.append({
                "PatientID":  f"PT-{cohort}-{i:03d}",
                "FullName":   f"Patient {cohort[0]}{i:02d}",
                "Cohort":     cohort,
                "Tissue":     tissue,
                "Visit":      f"V{(i % 3) + 1}",
                "Consented":  "Yes",
            })
    ref_df = pd.DataFrame(ref_rows)

    query_rows = [
        # Perfect
        {"SampleID": "PT-ALPHA-001", "CollectedBy": "Nurse-01"},
        {"SampleID": "PT-BETA-005",  "CollectedBy": "Nurse-02"},
        # Lowercase
        {"SampleID": "pt-alpha-010", "CollectedBy": "Nurse-01"},
        # Word order reversed (common when staff key by hand)
        {"SampleID": "ALPHA-PT-015", "CollectedBy": "Nurse-03"},
        {"SampleID": "BETA PT 003",  "CollectedBy": "Nurse-02"},
        # Missing cohort separator
        {"SampleID": "PTALPHA020",   "CollectedBy": "Auto-Import"},
        {"SampleID": "PTBETA010",    "CollectedBy": "Auto-Import"},
        # Abbreviated cohort name
        {"SampleID": "PT-ALP-025",   "CollectedBy": "Nurse-04"},
        {"SampleID": "PT-BET-012",   "CollectedBy": "Nurse-04"},
        # Extra spaces around dashes (Excel quirk)
        {"SampleID": "PT - ALPHA - 007", "CollectedBy": "Nurse-01"},
        # Unicode accented letter (PDF export)
        {"SampleID": "PT-ÁLPHA-008", "CollectedBy": "PDF-System"},
        # Wrong cohort separator style
        {"SampleID": "PT_ALPHA_030", "CollectedBy": "LIMS-A"},
        {"SampleID": "PT/BETA/020",  "CollectedBy": "LIMS-B"},
        # ID with visit suffix appended (not in reference)
        {"SampleID": "PT-ALPHA-002-V2", "CollectedBy": "Nurse-05"},
        # Gamma cohort (smaller, often missed)
        {"SampleID": "PT-GAMMA-001", "CollectedBy": "Nurse-06"},
        {"SampleID": "PT-GAMMA-015", "CollectedBy": "Nurse-06"},
        {"SampleID": "pt gamma 007", "CollectedBy": "Nurse-06"},
        # Single character typo in cohort name
        {"SampleID": "PT-ALTHA-004", "CollectedBy": "Nurse-07"},   # ALTHA vs ALPHA
        {"SampleID": "PT-BETTA-008", "CollectedBy": "Nurse-07"},   # BETTA vs BETA
        # Number padding difference
        {"SampleID": "PT-ALPHA-1",   "CollectedBy": "Manual"},
        {"SampleID": "PT-BETA-5",    "CollectedBy": "Manual"},
        # Legitimately missing from database (enrolled after reference export)
        {"SampleID": "PT-ALPHA-031", "CollectedBy": "Nurse-01"},
        {"SampleID": "PT-DELTA-001", "CollectedBy": "New-Cohort"},
        # Blank / junk
        {"SampleID": "",             "CollectedBy": "Unknown"},
        {"SampleID": "N/A",          "CollectedBy": "Unknown"},
        {"SampleID": "PENDING",      "CollectedBy": "Unknown"},
        # Duplicate (same ID appears twice in query — real-world re-draw)
        {"SampleID": "PT-BETA-015",  "CollectedBy": "Nurse-02"},
        {"SampleID": "PT-BETA-015",  "CollectedBy": "Nurse-08"},
        # Completely different system
        {"SampleID": "GNM-2024-001", "CollectedBy": "Wrong-DB"},
    ]
    query_df = pd.DataFrame(query_rows)

    return {
        "name":         "Clinical Trial Specimens",
        "description":  "70-sample reference across three patient cohorts (ALPHA, BETA, GAMMA). "
                        "Query sheet simulates real-world clinical data entry problems: reversed "
                        "word order, abbreviated cohort names, unicode accents, slash separators, "
                        "missing patients, and duplicated draw events.",
        "ref_df":       ref_df,
        "query_df":     query_df,
        "ref_id_col":   "PatientID",
        "ref_name_col": "FullName",
        "query_id_col": "SampleID",
        "challenges": [
            "Reversed word order (ALPHA-PT-015 vs PT-ALPHA-015)",
            "Abbreviated cohort name (ALP vs ALPHA)",
            "Unicode accented letters from PDF system",
            "Slash separator (PT/BETA/020) instead of dash",
            "Visit suffix appended to ID (PT-ALPHA-002-V2)",
            "Duplicate query IDs (re-draw events)",
            "Patients from a new cohort (DELTA) not in reference",
        ],
    }


# =============================================================================
# Dataset 3 — Biobank Short IDs
# =============================================================================
# Reference: BB-NNN short alphanumeric IDs with tissue/storage metadata
# Query: maximum short-ID ambiguity — easy to falsely match

def _make_biobank() -> dict:
    import random
    random.seed(7)

    tissues    = ["Adipose", "Muscle", "Skin", "Blood", "Urine", "Saliva", "Stool", "Plasma"]
    storage    = ["-80C", "-196C (LN2)", "RT", "4C"]
    sites      = ["Site-London", "Site-Manchester", "Site-Edinburgh", "Site-Bristol"]

    ref_rows = []
    for i in range(1, 101):
        ref_rows.append({
            "BioID":       f"BB-{i:03d}",
            "SampleName":  f"{random.choice(tissues)}-{i:03d}",
            "StorageSite": random.choice(sites),
            "StorageTemp": random.choice(storage),
            "Volume_mL":   round(random.uniform(0.5, 5.0), 2),
            "Aliquots":    random.randint(1, 8),
        })
    ref_df = pd.DataFrame(ref_rows)

    query_rows = [
        # Exact
        {"ID": "BB-001", "Lab": "UCL"},
        {"ID": "BB-050", "Lab": "UCL"},
        {"ID": "BB-100", "Lab": "UCL"},
        # Lowercase
        {"ID": "bb-010", "Lab": "Oxford"},
        {"ID": "Bb-020", "Lab": "Oxford"},
        # No dash
        {"ID": "BB001",  "Lab": "Imperial"},
        {"ID": "BB055",  "Lab": "Imperial"},
        # Space instead of dash
        {"ID": "BB 030", "Lab": "Cambridge"},
        {"ID": "BB 075", "Lab": "Cambridge"},
        # Underscore instead of dash
        {"ID": "BB_040", "Lab": "Bristol"},
        # Extra leading zero (BB-0010 vs BB-010)
        {"ID": "BB-0010", "Lab": "Edinburgh"},
        {"ID": "BB-0050", "Lab": "Edinburgh"},
        # Missing leading zero (BB-10 vs BB-010)
        {"ID": "BB-10",  "Lab": "Manchester"},
        {"ID": "BB-5",   "Lab": "Manchester"},
        # One letter typo in prefix
        {"ID": "BC-001", "Lab": "Manual"},   # BC vs BB
        {"ID": "BB-O1O", "Lab": "Manual"},   # letter O instead of zero
        {"ID": "BB-06O", "Lab": "Manual"},   # trailing O vs 0
        # Wrong prefix entirely
        {"ID": "BK-001", "Lab": "Wrong-Site"},
        {"ID": "SB-050", "Lab": "Wrong-Site"},
        # IDs beyond the reference range (101–110, don't exist)
        {"ID": "BB-101", "Lab": "New-Batch"},
        {"ID": "BB-105", "Lab": "New-Batch"},
        {"ID": "BB-110", "Lab": "New-Batch"},
        # Very short / ambiguous
        {"ID": "BB",     "Lab": "Truncated"},
        {"ID": "B",      "Lab": "Truncated"},
        {"ID": "001",    "Lab": "Truncated"},
        # Mix of correct with extra suffix
        {"ID": "BB-025-A", "Lab": "Aliquot-Tracking"},  # aliquot label
        {"ID": "BB-080-B", "Lab": "Aliquot-Tracking"},
        # Blank / junk
        {"ID": "",       "Lab": "Unknown"},
        {"ID": "N/A",    "Lab": "Unknown"},
        # Correct
        {"ID": "BB-090", "Lab": "UCL"},
    ]
    query_df = pd.DataFrame(query_rows)

    return {
        "name":         "Biobank Short IDs",
        "description":  "100-sample biobank reference with short 'BB-NNN' IDs. Short IDs are the "
                        "hardest case: a 2-letter difference between BB-001 and BC-001 is just "
                        "enough for a fuzzy match, but also creates collision risk. Tests the "
                        "threshold between correct fuzzy matching and false positives.",
        "ref_df":       ref_df,
        "query_df":     query_df,
        "ref_id_col":   "BioID",
        "ref_name_col": "SampleName",
        "query_id_col": "ID",
        "challenges": [
            "Short IDs — high collision risk between BB-001 and BC-001",
            "Letter O vs digit 0 (BB-O1O)",
            "Extra leading zero (BB-0010 vs BB-010)",
            "Aliquot suffix (BB-025-A) — should match BB-025 but might not",
            "IDs beyond reference range (BB-101 to BB-110)",
            "Truncated/partial IDs ('BB', 'B', '001')",
            "Multiple separator styles: dash, space, underscore, none",
        ],
    }


# =============================================================================
# Dataset 4 — Proteomics Multi-Site Study
# =============================================================================
# Reference: complex hierarchical IDs encoding site + participant + timepoint
# Query: various levels of ID truncation, site code swaps, date-formatted IDs

def _make_proteomics() -> dict:
    import random
    random.seed(99)

    sites        = ["LON", "NYC", "BER", "TOK", "SYD"]
    timepoints   = ["T0", "T1", "T2", "T3"]
    proteins     = ["Proteome", "Phospho", "Glyco", "Ubiquitin"]

    ref_rows = []
    pid = 1
    for site in sites:
        for participant in range(1, 13):  # 12 participants per site
            for tp in timepoints[:3]:     # T0, T1, T2 only
                ref_rows.append({
                    "SpecimenID":  f"{site}-P{participant:02d}-{tp}",
                    "SiteName":    f"Site-{site}",
                    "Participant": f"P{participant:02d}",
                    "Timepoint":   tp,
                    "Panel":       random.choice(proteins),
                    "QC_Pass":     random.choice(["Yes", "Yes", "Yes", "No"]),
                })
                pid += 1
    ref_df = pd.DataFrame(ref_rows)

    query_rows = [
        # Exact
        {"Specimen": "LON-P01-T0",  "Analyst": "Dr. Smith"},
        {"Specimen": "NYC-P05-T1",  "Analyst": "Dr. Jones"},
        {"Specimen": "BER-P10-T2",  "Analyst": "Dr. Müller"},
        # Lowercase
        {"Specimen": "lon-p01-t1",  "Analyst": "Dr. Smith"},
        # Dot separator instead of dash
        {"Specimen": "LON.P02.T0",  "Analyst": "Auto-Export"},
        {"Specimen": "NYC.P06.T2",  "Analyst": "Auto-Export"},
        # Slash separator
        {"Specimen": "BER/P03/T1",  "Analyst": "LIMS-B"},
        # Space separator
        {"Specimen": "TOK P04 T0",  "Analyst": "Operator-1"},
        # Missing timepoint prefix
        {"Specimen": "SYD-P07-0",   "Analyst": "Operator-2"},   # T0 → 0
        {"Specimen": "LON-P08-2",   "Analyst": "Operator-2"},   # T2 → 2
        # Site code typo
        {"Specimen": "LND-P01-T0",  "Analyst": "Manual"},       # LND vs LON
        {"Specimen": "NWY-P05-T1",  "Analyst": "Manual"},       # NWY vs NYC
        # Participant zero-padding missing
        {"Specimen": "LON-P1-T0",   "Analyst": "Manual"},
        {"Specimen": "BER-P5-T2",   "Analyst": "Manual"},
        # Timepoint at start instead of end
        {"Specimen": "T1-LON-P03",  "Analyst": "Rearranged"},
        {"Specimen": "T0-BER-P11",  "Analyst": "Rearranged"},
        # Extra institution code prepended
        {"Specimen": "UCL_LON-P04-T0",  "Analyst": "UCL-LIMS"},
        {"Specimen": "MPI_BER-P09-T2",  "Analyst": "MPI-LIMS"},
        # T3 timepoint — only in query (not in reference, which has T0-T2)
        {"Specimen": "LON-P01-T3",  "Analyst": "Dr. Smith"},
        {"Specimen": "NYC-P05-T3",  "Analyst": "Dr. Jones"},
        # Completely wrong format
        {"Specimen": "BB-001",      "Analyst": "Wrong-DB"},
        {"Specimen": "GNM-2024-001","Analyst": "Wrong-DB"},
        # Blank
        {"Specimen": "",            "Analyst": "Unknown"},
        {"Specimen": "N/A",         "Analyst": "Unknown"},
        # Good matches from other sites
        {"Specimen": "TOK-P11-T1",  "Analyst": "Dr. Tanaka"},
        {"Specimen": "SYD-P12-T2",  "Analyst": "Dr. Wilson"},
    ]
    query_df = pd.DataFrame(query_rows)

    return {
        "name":         "Proteomics Multi-Site Study",
        "description":  "180-sample reference encoding site + participant + timepoint in a "
                        "3-part hierarchical ID. Query contains IDs from 5 sites with separator "
                        "swaps (dot, slash, space), word-order rearrangements, missing timepoint "
                        "prefixes, and samples from a T3 timepoint not yet in the reference.",
        "ref_df":       ref_df,
        "query_df":     query_df,
        "ref_id_col":   "SpecimenID",
        "ref_name_col": "SiteName",
        "query_id_col": "Specimen",
        "challenges": [
            "Dot and slash separators (LON.P02.T0, BER/P03/T1)",
            "Timepoint word-order swap (T1-LON-P03 vs LON-P03-T1)",
            "Site code typos (LND vs LON, NWY vs NYC)",
            "T3 timepoint absent from reference (post-cutoff samples)",
            "Institution prefix prepended by downstream LIMS",
            "Timepoint abbreviation stripped (T0 → 0, T2 → 2)",
        ],
    }


# =============================================================================
# Public registry
# =============================================================================

EXAMPLE_DATASETS: list[dict] = [
    _make_genomics(),
    _make_clinical(),
    _make_biobank(),
    _make_proteomics(),
]

DATASET_NAMES: list[str] = [d["name"] for d in EXAMPLE_DATASETS]


def get_dataset(name: str) -> dict | None:
    for d in EXAMPLE_DATASETS:
        if d["name"] == name:
            return d
    return None
