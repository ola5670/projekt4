import pandas as pd
import argparse
from pathlib import Path
import sys
import os

# Dodaj katalog projektu do ścieżki
sys.path.append(os.path.join(os.path.dirname(__file__), '../../scripts'))

from load_data import download_gios_archive, clean_gios_data2, clean_column_names
from analyse_data import map_old_to_new_codes, get_daily_mean, get_daily_exceedances

#from scripts.load_data import download_gios_archive, clean_gios_data2, clean_column_names
#from scripts.analyse_data import map_old_to_new_codes, get_daily_mean, get_daily_exceedances


# ---- CONFIG ----

gios_url_ids = {
    2015: "236",
    2018: "603",
    2021: "486",
    2024: "582"
}

gios_pm25_file = {
    2015: "2015_PM25_1g.xlsx",
    2018: "2018_PM25_1g.xlsx",
    2021: "2021_PM25_1g.xlsx",
    2024: "2024_PM25_1g.xlsx"
}

DAILY_LIMIT = 15


def main(year: int):

    print(f"Processing PM2.5 for year {year}")

    out_dir = Path(f"results/pm25/{year}")
    out_dir.mkdir(parents=True, exist_ok=True)

    # --- download ---
    df_raw = download_gios_archive(year, gios_url_ids[year], gios_pm25_file[year])

    # --- clean ---
    df = clean_gios_data2(df_raw)
    df = clean_column_names(df)

    # --- map station codes ---
    mapping = map_old_to_new_codes()
    df.rename(columns=mapping, inplace=True)

    # --- daily mean ---
    daily_means = get_daily_mean(df)
    daily_means.to_csv(out_dir / "daily_means.csv")

    # --- exceedances ---
    exc_per_station, total_days = get_daily_exceedances(df, DAILY_LIMIT)

    exc_df = exc_per_station.to_frame(name="exceedance_days")
    exc_df.to_csv(out_dir / "exceedance_days.csv")

    print(f"Finished year {year}")
    print(f"total days with exceedance: {total_days}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, required=True)

    args = parser.parse_args()
    main(args.year)