import os
import glob
import pandas as pd

RAW_DIR = "data/raw"
REPORT_PATH = "reports/data_quality_summary.md"


def load_all_csvs(raw_dir):
    csv_paths = sorted(glob.glob(os.path.join(raw_dir, "*.csv")))
    if not csv_paths:
        print(f"No CSV files found in {raw_dir}.")
        return {}, []

    frames = {}
    anomalies = []

    for path in csv_paths:
        name = os.path.splitext(os.path.basename(path))[0]
        print(f"\n{'=' * 60}\nLoading: {name}\n{'=' * 60}")

        df = pd.read_csv(path)
        frames[name] = df

        print(f"Shape: {df.shape}")
        print("\nDtypes:")
        print(df.dtypes)
        print("\nHead:")
        print(df.head())

        null_cols = df.columns[df.isnull().any()].tolist()
        if null_cols:
            anomalies.append(f"- **{name}**: missing values in columns {null_cols}")

        dup_count = df.duplicated().sum()
        if dup_count > 0:
            anomalies.append(f"- **{name}**: {dup_count} duplicate rows")

        for col in df.select_dtypes(include="object").columns:
            sample = df[col].dropna().astype(str).head(20)
            if sample.str.contains(r"[\d],[\d]|₹|%").any():
                anomalies.append(f"- **{name}.{col}**: looks numeric but stored as text")

        for col in df.columns:
            if "date" in col.lower() and not pd.api.types.is_datetime64_any_dtype(df[col]):
                anomalies.append(f"- **{name}.{col}**: date column not parsed as datetime")

    return frames, anomalies


def explore_fund_master(frames):
    master_key = next((k for k in frames if "fund_master" in k.lower()), None)
    if master_key is None:
        print("\nNo file matching 'fund_master' found - skipping master exploration.")
        return None

    df = frames[master_key]
    print(f"\n{'=' * 60}\nFund Master Exploration: {master_key}\n{'=' * 60}")

    candidate_cols = {
        "fund_house": ["fund_house", "amc", "amc_name"],
        "category": ["category", "scheme_category"],
        "sub_category": ["sub_category", "scheme_sub_category"],
        "risk_grade": ["risk_grade", "risk", "riskometer", "risk_category"],
    }

    for label, options in candidate_cols.items():
        col = next((c for c in options if c in df.columns), None)
        if col:
            uniques = df[col].dropna().unique()
            print(f"\n{label} ({col}) - {len(uniques)} unique values:")
            print(sorted(map(str, uniques)))
        else:
            print(f"\n{label}: no matching column found among {options}")

    return df


def validate_amfi_codes(frames, master_df):
    nav_key = next((k for k in frames if "nav_history" in k.lower()), None)
    if master_df is None or nav_key is None:
        print("\nSkipping AMFI code validation - need both fund_master and nav_history files.")
        return []

    nav_df = frames[nav_key]

    code_col_options = ["scheme_code", "amfi_code", "code"]
    master_code_col = next((c for c in code_col_options if c in master_df.columns), None)
    nav_code_col = next((c for c in code_col_options if c in nav_df.columns), None)

    if not master_code_col or not nav_code_col:
        print("\nCould not find a scheme/AMFI code column in one of the files - check column names.")
        return []

    master_codes = set(master_df[master_code_col].astype(str).str.strip())
    nav_codes = set(nav_df[nav_code_col].astype(str).str.strip())

    missing_in_nav = master_codes - nav_codes
    missing_in_master = nav_codes - master_codes

    summary = []
    summary.append(f"Total scheme codes in fund_master: {len(master_codes)}")
    summary.append(f"Total scheme codes in nav_history: {len(nav_codes)}")
    summary.append(f"Codes in fund_master with NO nav_history: {len(missing_in_nav)}")
    summary.append(f"Codes in nav_history with NO fund_master entry: {len(missing_in_master)}")

    print(f"\n{'=' * 60}\nAMFI Code Validation\n{'=' * 60}")
    for line in summary:
        print(line)

    return summary


def write_report(anomalies, validation_summary):
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w") as f:
        f.write("# Data Quality Summary - Day 1\n\n")
        f.write("## Anomalies found while loading raw CSVs\n\n")
        if anomalies:
            f.write("\n".join(anomalies))
        else:
            f.write("No anomalies detected.")
        f.write("\n\n## AMFI scheme code validation (fund_master vs nav_history)\n\n")
        if validation_summary:
            f.write("\n".join(f"- {line}" for line in validation_summary))
        else:
            f.write("Validation skipped - check that fund_master and nav_history files are present.")
    print(f"\nData quality summary written to {REPORT_PATH}")


if __name__ == "__main__":
    frames, anomalies = load_all_csvs(RAW_DIR)
    master_df = explore_fund_master(frames)
    validation_summary = validate_amfi_codes(frames, master_df)
    write_report(anomalies, validation_summary)
