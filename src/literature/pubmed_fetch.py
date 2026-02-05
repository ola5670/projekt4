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
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


def parse_pubmed_date(date_str: str) -> int:
    """
    Parse PubMed date strings such as:
        - "2021 Jan 15"
        - "2024 Dec"
        - "2023"
    and return publication year as int.
    """
    try:
        year = int(date_str.split()[0])
        if len(str(year)) == 4:
            return year
    except Exception:
        return 0


def load_config(config_path: str):
    """
    Load YAML configuration file.
    """
    with open(config_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

def fetch_pubmed(query: str, year: int, email: str, retmax=100) -> pd.DataFrame:
    """
    Fetch PubMed publications for a given query and year.
    """
    Entrez.email = email
    term = f"{query} AND {year}[pdat]"
    logger.debug(f"Running PubMed query: {term} with retmax={retmax}")

    # Search PubMed for matching article IDs
    handle = Entrez.esearch(db="pubmed", term=term, retmax=retmax)
    record = Entrez.read(handle)
    handle.close()
    ids = record['IdList']

    logger.debug(f"Found {len(ids)} articles for query '{query}' in year {year}")

    # If no results were found, return empty dataframe with proper columns
    if not ids:
        return pd.DataFrame(columns=["PMID", "Title", "Journal", "Year", "Authors"])

    # Fetch full metadata records for all found IDs
    handle = Entrez.efetch(db="pubmed", id=ids, retmode="xml")
    records = Entrez.read(handle)
    handle.close()
    logger.debug(f"Retrieved {len(records['PubmedArticle'])} articles from efetch")

    data = []

    # Extract relevant metadata fields from XML response
    for rec in records["PubmedArticle"]:
        medline = rec['MedlineCitation']
        article = medline['Article']

        pmid = medline['PMID']
        title = article.get('ArticleTitle', '')
        journal = article['Journal']['Title'] if 'Journal' in article else ''

        # Raw publication year extracted from PubDate
        pub_year_raw = article['Journal']['JournalIssue']['PubDate'].get(
            'Year', str(year)
        )

        # Normalize year using a deterministic parser
        pub_year = parse_pubmed_date(pub_year_raw)

        # Extract authors list and join into a single string
        authors_list = article.get('AuthorList', [])
        authors = ", ".join(
            [f"{a.get('LastName', '')} {a.get('Initials', '')}" for a in authors_list]
        )

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
    """
    Generate summary CSV files:
    """
    os.makedirs(output_folder, exist_ok=True)

    # If no data create empty but valid CSV outputs
    if df.empty:
        logger.warning("No data available for summarization. Creating empty summary files.")

        pd.DataFrame(columns=["Year", "Counts"]).to_csv(
            f"{output_folder}/summary_by_year.csv", index=False
        )
        pd.DataFrame(columns=["Journal", "Counts"]).to_csv(
            f"{output_folder}/top_10_journals.csv", index=False
        )
        return

    summary_by_year = df.groupby("Year").size().reset_index(name='Counts')
    summary_by_year.to_csv(f"{output_folder}/summary_by_year.csv", index=False)

    top_10_journals = df['Journal'].value_counts().head(10).reset_index()
    top_10_journals.columns = ['Journal', 'Counts']
    top_10_journals.to_csv(f"{output_folder}/top_10_journals.csv", index=False)

def main():
    
    parser = argparse.ArgumentParser(description="Fetch PubMed literature for a given year.")
    parser.add_argument("--year", type=int, required=True, help="Publication year")
    parser.add_argument("--config", type=str, required=True, help="Path to YAML config file")
    args = parser.parse_args()

    cfg = load_config(args.config)
    pubmed_cfg = cfg['pubmed']
    queries = pubmed_cfg['queries']
    email = pubmed_cfg['email']
    retmax = pubmed_cfg.get('max_results', 100)

    # Output directory per year – guarantees no overwriting of other years
    output_folder = f"results/literature/{args.year}"
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    # Setup per-year logging file
    year_log_file = f"logs/pubmed_{args.year}.log"
    file_handler = logging.FileHandler(year_log_file)
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(levelname)s] %(asctime)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.info(f"Starting PubMed pipeline for year {args.year}")

    all_dfs = []

    # Run PubMed queries sequentially and collect results
    for query in queries:
        df = fetch_pubmed(query, args.year, email, retmax)
        all_dfs.append(df)

    # Merge all query results into one DataFrame
    final_df = pd.concat(all_dfs, ignore_index=True)

    # Always write outputs even if empty
    final_df.to_csv(f"{output_folder}/pubmed_papers.csv", index=False)
    summarize_pubmed(final_df, output_folder)

    logger.info(
        f"PubMed processing finished for year {args.year}. "
        f"Total papers: {len(final_df)}"
    )

if __name__ == "__main__":
    main()
