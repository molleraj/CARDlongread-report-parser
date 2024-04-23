#!/usr/bin/env python3

import argparse
import pandas as pd
from bs4 import BeautifulSoup
import glob
from dateutil import parser
import re

def read_html(path):
    # Load the HTML file
    with open(path, 'r') as file:
        html_content = file.read()
    
    # Create a BeautifulSoup object
    soup = BeautifulSoup(html_content, "html.parser")

    return soup

# check if vbz compress
def check_fast5(html_body):
    # convert to string
    body_str = str(html_body)

    # check is vbz compress is present
    if 'vbz_compress' in body_str:
        return 'vbz_compress'
    else:
        return 'off'
        
def get_timev2(html_body, fast5, ret= 'both'):
    if fast5 == 'off':
        # start and end time stamp data stored in first <script> tag
        script_text = html_body.find('script').text
    
        # Regex to find the getElementById function calls and extract both the ID and the time data
        pattern = r"getElementById\('(.+?)'\)\.innerHTML = convertTime\('(.+?)'\);"
        matches = re.findall(pattern, script_text)
        
        # Create a dictionary to hold each ID with its corresponding timestamp
        timestamp_dict = {id: timestamp for id, timestamp in matches}
    
        # store start and end timestamps in vars
        start = timestamp_dict['start-timestamp']
        end = timestamp_dict['end-timestamp']
    
        # Use dateutil's parser to handle the ISO 8601 format automatically
        timestamp_start = parser.isoparse(start).date()
        timestamp_end = parser.isoparse(end).date()
    
        # create data strings
        startdate = f'{timestamp_start.month}.{timestamp_start.day}.{timestamp_start.year}'
        enddate = f'{timestamp_end.month}.{timestamp_end.day}.{timestamp_end.year}'
        
    elif fast5 == 'vbz_compress':
        # start and end time stamp data stored in run-report-header
        script_text = html_body.find('header', {'class':"run-report-header"}).find('div', {'class': 'run-details'}).text
        # Regex to find the end and start dates
        pattern = r'\d+\s*[a-zA-Z]+\s*\d+'
        matches = re.findall(pattern, script_text)

        # store start and end timestamps in vars
        start = matches[0] 
        end = matches[1]

        # Use dateutil's parser to handle the ISO 8601 format automatically
        timestamp_start = parser.parse(start).date()
        timestamp_end = parser.parse(end).date()
        
        # create data strings
        startdate = f'{timestamp_start.month}.{timestamp_start.day}.{timestamp_start.year}'
        enddate = f'{timestamp_end.month}.{timestamp_end.day}.{timestamp_end.year}'

    if ret == 'start':
        return startdate
    elif ret == 'end':
        return enddate
    else:
        return startdate, enddate

def get_promid(html_body, fast5):
    # value located in first <h1> tag in body
    promid_text = html_body.find('h1').text
    if fast5 == 'off':
        # Regex pattern 
        pattern = r'PromethION\s\((\w+\d+)\)'
    
        # search
        match = re.search(pattern, promid_text)
    
        # get value from search
        promid = match.group(1)
    elif fast5 == 'vbz_compress':
        # Regex pattern 
        pattern = r'PromethION\s\d+\s\((\w+\d+)\)'
    
        # search
        match = re.search(pattern, promid_text)
    
        # get value from search
        promid = match.group(1)

    return promid

def get_ex_sam_name(html_body):
    # value located in first <div> tag
    run = html_body.find('div', {'class':'run-details'})
    run_text = run.text

    # Regex pattern
    pattern = r'\·\s*([A-Za-z0-9_]+)'

    # search for text values (formt appears to be experiment name, sample name, and unknown value)
    run_text_list = re.findall(pattern, run_text)

    # get vars
    ex_name = run_text_list[0] # experiment name
    sample_name = run_text_list[1] # sample name

    return {'Experiment Name':ex_name, 'Sample Name': sample_name}

def get_runsum(html_body):
    # narrow down to data output
    tmp_do = html_body.find('section', {'id':'run-summary'}).find('div', {'class':'container data-output'})

    # extract estimated bases/data output(GB) text
    do_text = tmp_do.find('div', class_='header', string='Estimated bases').find_next_sibling('div').text
    do_val = float(do_text.split(' ')[0])

    # estimated N50
    n50_text = tmp_do.find('div', class_='header', string='Estimated N50').find_next_sibling('div').text
    n50_val = float(n50_text.split(' ')[0])
    return {'Data Output': do_val,'N50': n50_val}

def get_flowcell(html_body):
    # narrow down to run setup tag content
    tmp_set = html_body.find('section', {'id':'run-configuration'}).find('div', {'class':'config-section'}).find('div', {'class':'accordion content'})

    # extract flow cell id
    fcid_text = tmp_set.find('div', class_ = 'title', string = 'Flow cell ID').find_next_sibling('div').text

    return fcid_text

def create_obs_row(_soup):
    # extract body contents - everything should be in here
    _body = _soup.body

    # fast5 
    fast5 = check_fast5(_body)
    # Create dictionary for row
    obs_row = {}

    # fill in with values
    ex_sam = get_ex_sam_name(_body)
    obs_row['Experiment_Name'] = ex_sam['Experiment Name']
    obs_row['Sample_Name'] = ex_sam['Sample Name']
    obs_row['Run_Date'] = get_timev2(_body, fast5, 'start')
    obs_row['PROM_ID'] = get_promid(_body, fast5)
    obs_row['Flow_Cell_ID'] = get_flowcell(_body)
    runsum = get_runsum(_body)
    obs_row['Data_output_(Gb)'] = runsum['Data Output']
    obs_row['N50_(kb)'] = runsum['N50']

    return obs_row

def format_row(_row):
    keys = ['Experiment_Name',
            'Sample_Name',
            'Run_Date',
            'PROM_ID',
            'Flow_Cell_ID',
            'Data_output_(Gb)',
            'N50_(kb)']
    values = list( map(_row.get, keys) )
    return('\t'.join([str(x) for x in values]))


# user input
inparser = argparse.ArgumentParser(description = 'Extract data from long read HTML report')
inparser.add_argument('--html_dir', default=None, type=str, help = 'path to directory containing html files, if converting whole directory')
inparser.add_argument('--filelist', default=None, type=str, help = 'text file containing list of all html reports to parse')
args = inparser.parse_args()

# get list of files
if args.html_dir is not None:
    files = glob.glob(f'{args.html_dir}/*.html')
elif args.filelist is not None:
    with open(args.filelist, 'r') as infile:
        files = [x.strip() for x in infile.readlines()]
else:
    quit('ERROR: No directory (--html_dir) or file list (--filelist) provided!')

# Initialize dictionary
_rows = []

for x in files:
    soup = read_html(x)
    row = create_obs_row(soup)
    _rows.append(row)

header = '\t'.join(['Experiment_Name','Sample_Name','Run_Date','PROM_ID','Flow_Cell_ID','Data_output_(Gb)','N50_(kb)'])

if len(_rows) > 0:
    print(header)
    for row in _rows:
        print(format_row(row))

quit()