# Project overview
## Analysis
Project 3 focuses on the analysis of PM2.5 air pollution data collected from measurement stations in Poland.
The project is implemented in a *function-oriented design*, where all data loading, preprocessing, analysis, and visualization logic is encapsulated in reusable Python functions located in `scripts`. The notebook `projekt_3_student.ipynb` serves as the execution and presentation layer.

Main objectives: 
- Load and clean air quality measurement data
- Calculate monthly averages of PM2.5 concentrations
- Visualize trends using heatmaps
- Identify days on which PM2.5 concentration exceeded the accepted norm
## Python and github functionality 
We use additional github and python functionality, creating tests, and make them automatically run while doing `push` and `pull` operations.

Main objectives:
- Make tests for download and manipulate data manipulation functions 
- Create script for github that run tests after commit push


# Structure
## Files
```bash
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

```
## Data
### Station code
Measurement stations are identified using a standardized station code format:
```bash
WwPp\*Nn\*
```
Where
- Ww – voivodeship (region) code
- Pp – county (powiat) code
- Nn – station name
- x = [:lower:]
- X = [:upper:]
## Notebook Workflow (projekt_3_student.ipynb)
The notebook follows a structured execution flow:
1. Import required libraries
2. Import functions from load_data.py and analyse_data.py
3. Load and clean the dataset
4. Perform monthly average calculations
5. Generate heatmaps
6. Identify days exceeding PM2.5 norms
7. Present results using tables and plots


# Remarks
## Tests
`test_no_metadata_rows` will not pass on *github.com* because the file with metadata is to big to be loaded. This test only works on local computers.

