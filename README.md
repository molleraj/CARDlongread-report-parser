# Long Read Sequencing Report Parsing

These Python scripts automate the process of collecting key sequencing statistics from weekly and cohort-wide sequencing runs and generate QC analytics as an Excel spreadsheet.

```longread_extract_from_json.py``` takes a list of Oxford Nanopore sequencing report JSON files as inputs and returns a table with the following fields per JSON:

Experiment Name, Sample Name, Run Date, PROM ID, Flow Cell ID, Data output (Gb), N50 (kb), MinKNOW Version, Passed Modal Q Score, Failed Modal Q Score, Starting Active Pores, Second Pore Count

Example usage (```python longread_extract_from_json.py -h```):
```
usage: longread_extract_from_json.py [-h] [--json_dir JSON_DIR] [--filelist FILELIST] [--output OUTPUT_FILE]

Extract data from long read JSON report

optional arguments:
  -h, --help            show this help message and exit
  --json_dir JSON_DIR   path to directory containing JSON files, if converting whole directory
  --filelist FILELIST   text file containing list of all JSON reports to parse
  --output OUTPUT_FILE  Output long read JSON report summary table in tab-delimited format
```

```longread_extract_summary_statistics.py``` then generates a spreadsheet from the output table of ```longread_extract_from_json.py``` containing a sequencing statistics summary table and both violin plot and scatter plot visualizations of data output, read N50, and starting active pores (active pores after starting sequencing).

Example usage (```python longread_extract_summary_statistics.py -h```):
```
usage: longread_extract_summary_statistics.py [-h] [-input INPUT_FILE] [-output OUTPUT_FILE] [-plot_title PLOT_TITLE] [--plot_cutoff | --no-plot_cutoff] [-run_cutoff RUN_CUTOFF]

This program gets summary statistics from long read sequencing report data.

optional arguments:
  -h, --help            show this help message and exit
  -input INPUT_FILE     Input tab-delimited tsv file containing features extracted from long read sequencing reports.
  -output OUTPUT_FILE   Output long read sequencing summary statistics XLSX
  -plot_title PLOT_TITLE
                        Title for each plot in output XLSX (optional)
  --plot_cutoff, --no-plot_cutoff
                        Include cutoff lines in violin plots (optional; default true; --no-plot_cutoff to override) (default: True)
  -run_cutoff RUN_CUTOFF
                        Minimum data output per flow cell run to include (optional, 1 Gb default)
```

To clone from GitHub:
```bash
# Download this repo
git clone https://github.com/NIH-CARD/longread-report-parser.git
cd longread-report-parser

# Generate list of files using `find`
find /data/CARDPB/data/PPMI/SEQ_REPORTS/example_reports/ -type f -name '*.html' > examplereports.txt

# Execute with file list of html reports (one per line):
python3 extract.py --filelist examplereports.txt > output.tsv

# Alternatively, execute on all html files within a directory
# (does not descend into subdirectories)
python3 extract.py --html_dir /data/CARDPB/data/PPMI/SEQ_REPORTS/example_reports/ > output.tsv
```
