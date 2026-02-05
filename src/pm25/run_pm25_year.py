import pandas as pd
import argparse
from pathlib import Path
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../scripts'))

from load_data import download_gios_archive, clean_gios_data2, clean_column_names
from analyse_data import map_old_to_new_codes, get_daily_mean, get_daily_exceedances

#from scripts.load_data import download_gios_archive, clean_gios_data2, clean_column_names
#from scripts.analyse_data import map_old_to_new_codes, get_daily_mean, get_daily_exceedances

DAILY_LIMIT = 15

gios_url_ids = {
    2015: "236",
    2018: "603",
    2019: "584",
    2021: "486",
    2024: "582"
}

gios_pm25_file = {
    2015: "2015_PM25_1g.xlsx",
    2018: "2018_PM25_1g.xlsx",
    2019: "2019_PM25_1g.xlsx",
    2021: "2021_PM25_1g.xlsx",
    2024: "2024_PM25_1g.xlsx"
}


def main(year: int, cities_to_filter: list):
    """
    Main processing pipeline for PM2.5 data: Download, Clean, Filter, and Analyze.
    """

    #Check if the requested year is supported by the GIOŚ metadata mapping
    if year not in gios_url_ids:
        available_years = sorted(list(gios_url_ids.keys()))
        print(f"ERROR: Year {year} is not supported by the PM2.5 script.")
        print(f"Available years: {available_years}")
        sys.exit(1)

    print(f"Processing PM2.5 for year {year}")

    out_dir = Path(f"results/pm25/{year}")

    out_dir.mkdir(parents=True, exist_ok=True)
    df_raw = download_gios_archive(year, gios_url_ids[year], gios_pm25_file[year])
    df = clean_gios_data2(df_raw)
    df = clean_column_names(df)
    mapping = map_old_to_new_codes()
    df.rename(columns=mapping, inplace=True)

    # Keep only stations belonging to selected cities
    if cities_to_filter:
        date_col = df.columns[0]  # Preserve the timestamp column
        station_cols = df.columns[1:]
        
        selected_stations = []
        for col in station_cols:
            for city in cities_to_filter:
                city_clean = city.strip().lower()
                prefix = city_clean[:3] # Matching via prefix 
                
                # Check for full name or common 3-letter abbreviations used in station codes
                if city_clean in col.lower() or prefix in col.lower():
                    selected_stations.append(col)
                    break
        
        if not selected_stations:
            print(f"WARNING: No stations found for cities: {cities_to_filter}. Keeping all data.")
        else:
            # Subset the DataFrame to include only the selected stations
            df = df[[date_col] + selected_stations]
            print(f"Stations filtered. Selected {len(selected_stations)} stations for: {cities_to_filter}")

    # Calculate daily means for all selected stations
    daily_means = get_daily_mean(df)
    daily_means.to_csv(out_dir / "daily_means.csv")

    # Determine exceedance days based on the DAILY_LIMIT
    exc_per_station, total_days = get_daily_exceedances(df, DAILY_LIMIT)

    # Save the exceedance count per station to a CSV file
    exc_df = exc_per_station.to_frame(name="exceedance_days")
    exc_df.to_csv(out_dir / "exceedance_days.csv")

    print(f"Finished year {year}")
    print(f"Total days with exceedance (filtered): {total_days}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process PM2.5 air quality data from GIOŚ.")
    parser.add_argument("--year", type=int, required=True, help="Year to process")
    parser.add_argument("--cities", type=str, default="", help="Comma-separated list of cities to filter")

    args = parser.parse_args()
    
    # Convert comma-separated string from config/Snakemake into a Python list
    cities_list = [c.strip() for c in args.cities.split(",") if c.strip()]
    
    main(args.year, cities_list)