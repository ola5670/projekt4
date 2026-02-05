import pandas as pd
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent  # zakłada, że test jest w katalogu tests/
sys.path.append(str(project_root / "src"))

from literature.pubmed_fetch import parse_pubmed_date

def test_parse_pubmed_date():
    """Testuje poprawne parsowanie roku z różnych formatów dat PubMed."""
    dates = [
        "2021 Jan 15",
        "2024 Dec",
        "2023",
        "2022 Jul 02"
    ]
    expected_years = [2021, 2024, 2023, 2022]

    for date_str, expected in zip(dates, expected_years):
        year = parse_pubmed_date(date_str)
        assert year == expected, f"Expected {expected} but got {year} for {date_str}"

def test_pubmed_output_csv(tmp_path):
    """Testuje zapis i wczytanie CSV z dodatkową kolumną Year po parsowaniu dat."""
    # symulacja danych PubMed
    df = pd.DataFrame({
        "Title": ["Paper A", "Paper B"],
        "PubMedDate": ["2021 Jan 15", "2021 Feb 10"]
    })

    # dodanie kolumny z rokiem
    df["Year"] = df["PubMedDate"].apply(parse_pubmed_date)

    # zapis do tymczasowego pliku CSV
    out_file = tmp_path / "pubmed_test.csv"
    df.to_csv(out_file, index=False)

    # wczytanie i sprawdzenie poprawności
    df_read = pd.read_csv(out_file)
    assert "Year" in df_read.columns
    assert df_read["Year"].tolist() == [2021, 2021]
