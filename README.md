# Task 4 – Analiza PM2.5 i PubMed

## Opis

Pipeline wykonuje analizę danych PM2.5 oraz literatury naukowej z PubMed dla wybranych lat. Wyniki są zapisywane w osobnych katalogach per rok, co pozwala zachować dane historyczne i nie nadpisywać wcześniejszych wyników.

## Struktura katalogów wyników

results/
├── pm25/
│   ├── 2021/ (daily_means.csv, exceedance_days.csv)
│   └── 2024/ ...
├── literature/
│   ├── 2021/ (pubmed_papers.csv, summary_by_year.csv, top_10_journals.csv)
│   └── 2024/ ...
└── report_task4.md

W pliku config/task4.yaml ustawiasz lata do analizy oraz dane PubMed:
1. years:
  - 2021
  - 2024

2. pubmed:

    - email: "twoj_email@example.com"
   
    - queries:

     - "PM2.5 air pollution"
     - "particulate matter health"
    - max_results: 200

## Uruchamianie pipeline

Uruchomienie pipeline dla wszystkich lat z configu:

```bash
<<<<<<< HEAD
snakemake -s Snakefile_task4 --cores 2
=======
**
├── data
│   ├── PM25_combined_2014_2019_2024.csv
│   └── PM25_combined_2015_2018_2021_2024.csv
├── main.py
├── projekt_1_student.ipynb
├── projekt_3_student.ipynb
├── requirements.txt
├── scripts
│   ├── analyse_data.py
│   └── load_data.py
└── test_cleaning.py**mini_project_ZTPDB_1
├── Snakefile_task4
├── config/
│   └── task4.yaml
├── src/
│   ├── pm25/
│   │   └── run_pm25_year.py
│   └── literature/
│       └── pubmed_fetch.py
├── results/
│   ├── pm25/
│   │   └── {YEAR}/
│   ├── literature/
│   │   └── {YEAR}/
│   └── report_task4.md
├── scripts/        
├── tests/
├── README.md

>>>>>>> 79b18243505a5df165a89e81694150f6a9e4d128
```
Pipeline liczy PM2.5 dla wskazanych lat.

Pobiera dane PubMed i generuje podsumowania.
Tworzy raport results/report_task4.md.

# Scenariusze użycia

Pierwsze uruchomienie
years: [2021, 2024] → pipeline policzy wszystkie lata i wygeneruje raport.

Aktualizacja konfiguracji
- Zmiana configu na years: [2019, 2024] → pipeline:

  - policzy brakujące dane PM2.5 dla 2019,

  - pobierze/analitykę PubMed dla 2019,

  - wygeneruje raport agregujący 2019 i 2024.

Snakemake pominie lata już policzone (tu: 2024).

# Testy

Pipeline posiada testy pytest w katalogu tests/.

Przykładowy test sprawdza parsowanie roku z dat PubMed:
```bash
pytest tests/test_pubmed_fetch.py -v
```
Test sprawdza, czy:

- różne formaty dat PubMed są poprawnie konwertowane na rok,

- zapis i wczytanie CSV z kolumną Year działa poprawnie.

## Deterministyczność

Kod pubmed_fetch.py działa deterministycznie przy tym samym configu i wejściu – ten sam zestaw publikacji i format wyjścia.

Wszystkie dane są zapisywane w katalogach per rok, co gwarantuje, że istniejące wyniki nie są nadpisywane.

## Logi

Każdy rok PubMed generuje własny log w logs/pubmed_{year}.log.

Standardowe logi PM2.5 są wyświetlane na stdout.

## Weryfikacja

Weryfikacja braku redundancji (pomijania roku 2024) odbywa się poprzez analizę sekcji Job stats. Przy ponownym uruchomieniu dla lat [2021, 2024], liczba zadań (count) dla reguł pm25_year oraz pubmed_year wynosi 1, co dowodzi, że Snakemake przetwarza tylko nowo dodany rok 2021, uznając wyniki dla 2024 za aktualne