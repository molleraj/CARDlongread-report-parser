# Long Read HTML Report Parsing

To clone from GitHub:
```bash
# Download as directory named 'LR_extract' (change if desired)
git clone https://gist.github.com/052ba5e4e878953aa0a9711a1776c75e.git LR_extract
cd LR_extract

# Generate list of files using `find`
find /data/CARDPB/data/PPMI/SEQ_REPORTS/example_reports/ -type f -name '*.html' > examplereports.txt

# Execute with file list of html reports (one per line):
python3 LR_extract.py --filelist examplereports.txt > output.tsv

# Alternatively, execute on all html files within a directory
# (does not descend into subdirectories)
python3 LR_extract.py --html_dir /data/CARDPB/data/PPMI/SEQ_REPORTS/example_reports/ > output.tsv
```