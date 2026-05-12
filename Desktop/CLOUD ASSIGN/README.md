# Global Patent Concentration Intelligence Dashboard

Prepared by Ainembabazi Martina.

This project reads the raw PatentsView files, cleans them with pandas, loads the results into SQLite, and writes a few reports from the same dataset.

I kept the project split into small scripts so it is easier to rerun and check.

## Project Structure

- `src/pipeline.py` - main ETL + reporting script
- `sql/schema.sql` - database schema
- `sql/queries.sql` - required SQL query set (Q1-Q7)
- `data/raw/` - raw source files (not committed)
- `data/clean/` - cleaned CSV outputs
- `reports/` - analysis report exports

## Input Files

Put the source files in `data/raw/`.

- `patent.tsv` or `patent.csv`
- `inventor.tsv` or `inventor.csv`
- `assignee.tsv` or `assignee.csv`
- `patent_inventor.tsv` or `patent_inventor.csv`
- `patent_assignee.tsv` or `patent_assignee.csv`

The script also accepts `.parquet` versions with the same base names.

## Setup

From the project root:

```powershell
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Run

```powershell
& .\.venv\Scripts\python.exe .\src\pipeline.py
```

If you want to test the pipeline on a smaller slice first:

```powershell
& .\.venv\Scripts\python.exe .\src\pipeline.py --limit 50000
```

Generate a short write-up for the report:

```powershell
& .\.venv\Scripts\python.exe .\src\generate_findings.py
```

Generate the console report (formatted terminal output):

```powershell
& .\.venv\Scripts\python.exe .\src\console_report.py
```

Generate the extra charts:

```powershell
& .\.venv\Scripts\python.exe .\src\visualize.py
```

Run the personalized Streamlit dashboard (extra credit):

```powershell
pip install -r requirements.txt
streamlit run src/dashboard.py
```

## What Gets Created

### Clean Data Files

- `data/clean/clean_patents.csv`
- `data/clean/clean_inventors.csv`
- `data/clean/clean_companies.csv`

### Database

- `data/patents.db`
- `sql/schema.sql`

### Reports

- Console summary report
- `reports/top_inventors.csv`
- `reports/top_companies.csv`
- `reports/country_trends.csv`
- `reports/top_countries.csv`
- `reports/patents_over_time.csv`
- `reports/summary_report.json`
- `reports/findings.md`
- `reports/figures/patents_over_time.png`
- `reports/figures/top_countries.png`

## What This Covers

The project covers the required parts of the assignment:

- Python ETL script
- pandas cleaning
- SQL queries (Q1-Q7)
- Interactive dashboard

### Three Required Report Types

1. **Console Report (Terminal Output)**
   - Run: `python src/console_report.py`
   - Shows: Total Patents, Top Inventors, Top Companies, Top Countries, Concentration Metrics
   - Example output in terminal with formatted sections

2. **CSV Exports (Data Files)**
   - `reports/top_inventors.csv`
   - `reports/top_companies.csv`
   - `reports/top_countries.csv`
   - `reports/country_trends.csv`
   - Structured data ready for import into Excel/other tools

3. **JSON Report (Structured Data)**
   - `reports/summary_report.json`
   - Complete analysis payload with all metrics and rankings
   - Used by dashboard and reporting scripts
- SQLite database
- patents, inventors, companies, and the relationship table
- Q1-Q7 SQL queries in `sql/queries.sql`
- console, CSV, and JSON reporting
- repeatable run steps

## Practical Notes

- Use the full dataset if your machine can handle it, or a smaller subset if you want a faster run.
-- Add a couple of terminal screenshots so the run is easy to verify.
-- Keep the final write-up short and specific. A few real observations are better than a long generic summary.
-- The chart script is there for extra credit, but the main pipeline still works without it.
-- The strongest story in this sample is concentration across inventors, companies, and countries, not a long time trend.

## Suggested Submission Order

1. Run the pipeline and check that the CSV and JSON files are created.
2. Run the findings script and use `reports/findings.md` as the basis for your discussion section.
3. Run the visualization script if you want the extra-credit charts.
4. Add 2 or 3 screenshots of the terminal output before you submit.
