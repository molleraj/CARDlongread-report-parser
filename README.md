# Long Read Sequencing Report Parsing

These Python scripts automate the process of collecting key sequencing statistics from weekly and cohort-wide sequencing runs and generate QC analytics as an Excel spreadsheet.

```longread_extract_from_json.py``` takes a list of Oxford Nanopore sequencing report JSON files as inputs and returns a table with the following fields per JSON:
Experiment Name, Sample Name, Run Date, PROM ID, Flow Cell ID, Data output (Gb), N50 (kb), MinKNOW Version, Passed Modal Q Score, Failed Modal Q Score, Starting Active Pores, Second Pore Count

```longread_extract_summary_statistics.py```

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
