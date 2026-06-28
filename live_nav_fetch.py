import os
import time
import requests
import pandas as pd

OUTPUT_DIR = "data/raw"
BASE_URL = "https://api.mfapi.in/mf/{}"

SCHEMES = {
    125497: "HDFC_Top_100_Direct",
    119551: "SBI_Bluechip",
    120503: "ICICI_Bluechip",
    118632: "Nippon_Large_Cap",
    119092: "Axis_Bluechip",
    120841: "Kotak_Bluechip",
}


def fetch_nav(scheme_code):
    url = BASE_URL.format(scheme_code)
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    payload = response.json()

    if payload.get("status") != "SUCCESS":
        raise ValueError(f"API returned non-success status for scheme {scheme_code}: {payload.get('status')}")

    meta = payload.get("meta", {})
    nav_records = payload.get("data", [])

    df = pd.DataFrame(nav_records)
    if df.empty:
        return df, meta

    df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y")
    df["nav"] = pd.to_numeric(df["nav"], errors="coerce")
    df["scheme_code"] = scheme_code
    df["scheme_name"] = meta.get("scheme_name")
    df["fund_house"] = meta.get("fund_house")
    df = df.sort_values("date").reset_index(drop=True)

    return df, meta


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    all_frames = []

    for scheme_code, label in SCHEMES.items():
        print(f"\nFetching scheme {scheme_code} ({label})...")
        try:
            df, meta = fetch_nav(scheme_code)
        except Exception as exc:
            print(f"  FAILED: {exc}")
            continue

        out_path = os.path.join(OUTPUT_DIR, f"nav_{scheme_code}_{label}.csv")
        df.to_csv(out_path, index=False)
        print(f"  Saved {len(df)} NAV records -> {out_path}")
        print(f"  Fund house: {meta.get('fund_house')} | Category: {meta.get('scheme_category')}")

        all_frames.append(df)
        time.sleep(0.5)

    if all_frames:
        combined = pd.concat(all_frames, ignore_index=True)
        combined_path = os.path.join(OUTPUT_DIR, "nav_live_combined.csv")
        combined.to_csv(combined_path, index=False)
        print(f"\nCombined file with all schemes saved -> {combined_path}")


if __name__ == "__main__":
    main()