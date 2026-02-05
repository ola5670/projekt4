# Task 4 – Analiza PM2.5 i PubMed

## Opis

Pipeline wykonuje analizę danych PM2.5 oraz literatury naukowej z PubMed dla wybranych lat. Wyniki są zapisywane w osobnych katalogach per rok, co pozwala zachować dane historyczne i nie nadpisywać wcześniejszych wyników.

## Struktura katalogów wyników

```
results/
├── pm25/
│   ├── 2021/ (daily_means.csv, exceedance_days.csv)
│   └── 2024/ ...
├── literature/
│   ├── 2021/ (pubmed_papers.csv, summary_by_year.csv, top_10_journals.csv)
│   └── 2024/ ...
└── report_task4.md
```

W pliku config/task4.yaml ustawiasz lata do analizy oraz dane PubMed:
1. years:
   - 2021
   -  2024
   
2. cities

3. pubmed:

    - email: "twoj_email@example.com"
   
    - queries:

     - "PM2.5 air pollution"
     - "particulate matter health"
    - max_results: 200

## Uruchamianie pipeline'u

Uruchomienie pipeline'u dla wszystkich lat z konfiguracji:
```
snakemake -s Snakefile_task4 --cores 2
```
Pipeline:
- liczy PM2.5 dla wskazanych lat,
- pobiera dane PubMed i generuje podsumowania,
- tworzy raport results/report_task4.md.

## Scenariusze użycia

### Pierwsze uruchomienie
years: [2021, 2024] → pipeline policzy wszystkie lata i wygeneruje raport.

### Aktualizacja konfiguracji
- Zmiana konfiguracji na years: [2019, 2024] → pipeline:

  - policzy brakujące dane PM2.5 dla 2019,

  - pobierze oraz wykona analizę PubMed dla 2019,

  - wygeneruje raport agregujący 2019 i 2024.

Snakemake pominie lata już policzone (tu: 2024).

## Testy

Pipeline zawiera testy pytest w katalogu tests/.

Przykładowy test sprawdza parsowanie roku z dat PubMed:
pytest tests/test_pubmed_fetch.py -v
Test sprawdza, czy:

- różne formaty dat PubMed są poprawnie konwertowane na rok,

- zapis i wczytanie CSV z kolumną Year działa poprawnie.

## Deterministyczność

Kod pubmed_fetch.py działa deterministycznie przy tym samym configu i wejściu – ten sam zestaw publikacji i format wyjścia.

Wszystkie dane są zapisywane w osobnych katalogach dla każdego roku, co gwarantuje, że istniejące wyniki nie są nadpisywane.

## Logi

Każdy rok PubMed generuje własny log w logs/pubmed_{year}.log.

Standardowe logi PM2.5 są wyświetlane na stdout.

## Weryfikacja

Weryfikacja braku redundancji (pomijania roku 2024) odbywa się poprzez analizę sekcji Job stats. Przy ponownym uruchomieniu dla lat [2021, 2024], liczba zadań (count) dla reguł pm25_year oraz pubmed_year wynosi 1, co potwierdza, że Snakemake przetwarza tylko nowo dodany rok 2021, uznając wyniki dla 2024 za aktualne.