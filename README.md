# NIA CARD Long Read Sequencing Report Parsing and Visualization

These Python scripts automate the process of collecting key sequencing statistics from weekly and cohort-wide sequencing runs and generate QC analytics as an Excel spreadsheet. They take run output JSON files as input and pull sequencing statistics from exact locations in each JSON hierarchical data structure. The scripts have been written to handle JSON files from MinKNOW version 24.02.19 and earlier. Please report any bugs in the Issues tab to further improve the parser.

## Usage

```longread_extract_from_json.py``` takes a list of Oxford Nanopore sequencing report JSON files as inputs (or a directory containing all JSON files to analyze) and returns a table with the following fields per JSON:

Experiment Name, Sample Name, Run Date, PROM ID, Flow Cell ID, Data output (Gb), N50 (kb), MinKNOW Version, Passed Modal Q Score, Failed Modal Q Score, Starting Active Pores, Second Pore Count

Below is sample output from the script:
```
Experiment Name	Sample Name	Run Date	PROM ID	Flow Cell ID	Data output (Gb)	N50 (kb)	MinKNOW Version	Passed Modal Q Score	Failed Modal Q Score	Starting Active Pores
Chile_404	Chile_404	2024-05-14	PC24B302	PAW33034	141.083	23.39	24.02.10	NA	NA	7465
Chile_406	Chile_406	2024-05-01	PC24B302	PAW73369	131.699	22.79	24.02.10	NA	NA	7339
Chile_509	Chile_509	2024-05-14	PC24B302	PAW61512	117.861	17.12	24.02.10	NA	NA	7515
Chile_511	Chile_511	2024-05-08	PC24B302	PAW71368	133.097	20.69	24.02.10	NA	NA	7226
Chile_516	Chile_516	2024-05-01	PC24B302	PAW71977	129.544	23.63	24.02.10	NA	NA	7516
```

The file list should contain paths to each report on each line, like so:
```
/data/CARD_AUX/LRS_temp/CHILE/SEQ_REPORTS/Chile_404/PAW33034/other_reports_PAW33034/report_PAW33034_20240514_2123_c7d4ac03.json
/data/CARD_AUX/LRS_temp/CHILE/SEQ_REPORTS/Chile_406/PAW73369/other_reports_PAW73369/report_PAW73369_20240501_1949_4e83275d.json
/data/CARD_AUX/LRS_temp/CHILE/SEQ_REPORTS/Chile_509/PAW61512/other_reports_PAW61512/report_PAW61512_20240514_2128_5a659d71.json
/data/CARD_AUX/LRS_temp/CHILE/SEQ_REPORTS/Chile_511/PAW71368/other_reports_PAW71368/report_PAW71368_20240508_2046_20d811c8.json
/data/CARD_AUX/LRS_temp/CHILE/SEQ_REPORTS/Chile_516/PAW71977/other_reports_PAW71977/report_PAW71977_20240501_1947_c6a80210.json
```

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

```longread_extract_summary_statistics.py``` then generates a spreadsheet from the output table of ```longread_extract_from_json.py``` containing a sequencing statistics summary table and both violin plot and scatter plot visualizations of data output, read N50, and starting active pores (active pores after starting sequencing). Individual runs (lines in TSV table) are highlighted indicating whether they are an initial run, top up, reconnection, or recovery.

Example data visualizations corresponding to data snippets shown earlier:
<br></br>
<img width="720" alt="image" src="https://github.com/user-attachments/assets/f576c444-65c7-4c66-9a1a-a6a7ebdfa6e4">
<br></br>
<img width="720" alt="image" src="https://github.com/user-attachments/assets/5e4c3038-d747-4373-b59d-dde6db8dabf3">
<br></br>
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
## Tutorial

To clone from GitHub and do a test run:
```bash
# Download this repo
git clone https://github.com/molleraj/longread-report-parser.git
cd longread-report-parser

# Test on pregenerated set of 50 random PPMI JSON files (use exact file provided)
# Random JSON file set generated like so with Linux coreutils shuf (shuffle) command
# shuf -n 50 full_PPMI_json_report_list_090524.txt > random_50_test_PPMI_json_paths_090524.txt
# random_50_test_PPMI_json_paths_090524.txt included in repository as example_json_reports.txt

# Execute with file list of json reports (one per line):
python3 longread_extract_from_json.py --filelist example_json_reports.txt --output example_output.tsv

# Alternatively, execute on all html files within a directory
# (does not descend into subdirectories)
python3 longread_extract_from_json.py --json_dir /data/CARDPB/data/PPMI/SEQ_REPORTS/example_json_reports/ --output example_output.tsv

# Make sequencing QC analytics spreadsheet from above QC output table (example_output.tsv)
python3 longread_extract_summary_statistics.py -input example_output.tsv -output example_summary_spreadsheet.xlsx -plot_title "PPMI tutorial example"
```

Example sequencing QC visualizations from summary spreadsheet:
