# Long Read Sequencing Report Parsing

These Python scripts automate the process of collecting key sequencing statistics from weekly and cohort-wide sequencing runs and generate QC analytics as an Excel spreadsheet.

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
