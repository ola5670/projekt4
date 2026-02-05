import argparse
import pandas as pd
from Bio import Entrez
import yaml
import os
import logging
import sys

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s] %(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def parse_pubmed_date(date_str: str) -> int:
    """
    Parsuje datę PubMed w formatach np. "2021 Jan 15", "2024 Dec", "2023"
    i zwraca rok jako int.
    Jeśli nie uda się sparsować, zwraca 0.
    """
    try:
        year = int(date_str.split()[0])
        if len(str(year)) == 4:
            return year
    except Exception:
        return 0

def load_config(config_path: str):
    """Wczytuje plik YAML z konfiguracją"""
    with open(config_path, 'r', encoding='utf-8') as file:
        cfg = yaml.safe_load(file)
    return cfg

def fetch_pubmed(query: str, year: int, email: str, retmax=100) -> pd.DataFrame:
    """Pobiera publikacje z PubMed dla danego zapytania i roku"""
    Entrez.email = email
    term = f"{query} AND {year}[pdat]"
    logger.debug(f"Running PubMed query: {term} with retmax={retmax}")

    # wyszukiwanie identyfikatorów
    handle = Entrez.esearch(db="pubmed", term=term, retmax=retmax)
    record = Entrez.read(handle)
    handle.close()
    ids = record['IdList']
    logger.debug(f"Found {len(ids)} articles for query '{query}' in year {year}")

    if not ids:
        return pd.DataFrame()

    # pobranie szczegółów
    handle = Entrez.efetch(db="pubmed", id=ids, retmode="xml")
    records = Entrez.read(handle)
    handle.close()
    logger.debug(f"Retrieved {len(records['PubmedArticle'])} articles from efetch")

    data = []
    for rec in records["PubmedArticle"]:
        medline = rec['MedlineCitation']
        article = medline['Article']
        pmid = medline['PMID']
        title = article.get('ArticleTitle', '')
        journal = article['Journal']['Title'] if 'Journal' in article else ''
        pub_year_raw = article['Journal']['JournalIssue']['PubDate'].get('Year', str(year))
        pub_year = parse_pubmed_date(pub_year_raw)
        authors_list = article.get('AuthorList', [])
        authors = ", ".join([f"{a.get('LastName','')} {a.get('Initials','')}" for a in authors_list])
        data.append({
            "PMID": pmid,
            "Title": title,
            "Journal": journal,
            "Year": pub_year,
            "Authors": authors
        })

    df = pd.DataFrame(data)
    logger.debug(f"DataFrame created with {len(df)} rows")
    return df

def summarize_pubmed(df: pd.DataFrame, output_folder: str):
    """Tworzy podsumowania i zapisuje do CSV"""
    os.makedirs(output_folder, exist_ok=True)

    summary_by_year = df.groupby("Year").size().reset_index(name='Counts')
    summary_by_year.to_csv(f"{output_folder}/summary_by_year.csv", index=False)

    top_10_journals = df['Journal'].value_counts().head(10).reset_index()
    top_10_journals.columns = ['Journal', 'Counts']
    top_10_journals.to_csv(f"{output_folder}/top_10_journals.csv", index=False)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--config", type=str, required=True)
    args = parser.parse_args()

    cfg = load_config(args.config)
    pubmed_cfg = cfg['pubmed']
    queries = pubmed_cfg['queries']
    email = pubmed_cfg['email']
    retmax = pubmed_cfg.get('max_results', 100)

    output_folder = f"results/literature/{args.year}"
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    # log per rok
    year_log_file = f"logs/pubmed_{args.year}.log"
    file_handler = logging.FileHandler(year_log_file)
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(levelname)s] %(asctime)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    all_dfs = []
    for query in queries:
        df = fetch_pubmed(query, args.year, email, retmax)
        if not df.empty:
            all_dfs.append(df)

    if all_dfs:
        final_df = pd.concat(all_dfs, ignore_index=True)
        final_df.to_csv(f"{output_folder}/pubmed_papers.csv", index=False)
        summarize_pubmed(final_df, output_folder)
        logger.info(f"PubMed fetch finished for year {args.year}, {len(final_df)} papers saved to {output_folder}")
    else:
        logger.info(f"PubMed fetch finished for year {args.year}, no papers found.")

if __name__ == "__main__":
    main()
