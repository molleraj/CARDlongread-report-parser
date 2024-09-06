#!/usr/bin/env python3
# long read sequencing report JSON parser
# output fields are Experiment Name, Sample Name, Run Date, PROM ID, Flow Cell ID, Data output (Gb), N50 (kb), MinKNOW Version
# look for Q score in the future and possibly also total reads
import json
import pandas as pd
import numpy as np
import argparse
import dataclasses
# get fields from json
def get_fields_from_json(input_json_dict):
    # define fields_from_json class
    @dataclasses.dataclass
    class fields_from_json:
        experiment_name : ''
        sample_name : ''
        run_date : ''
        prom_id : ''
        flow_cell_id : ''
        minknow_version : ''
        data_output : float = 0
        n50 : float = 0
        modal_q_score_passed : float = 0
        modal_q_score_failed : float = 0
        starting_active_pores : float = 0
        second_active_pore_count : float = 0
    # get elements from json-based dictionary
    fields_from_json.experiment_name = input_json_dict['protocol_run_info']['user_info']['protocol_group_id']
    fields_from_json.sample_name = input_json_dict['protocol_run_info']['user_info']['sample_id']
    fields_from_json.run_date = input_json_dict['protocol_run_info']['start_time'][0:10]
    fields_from_json.prom_id = input_json_dict['host']['serial']
    fields_from_json.flow_cell_id = input_json_dict['protocol_run_info']['flow_cell']['flow_cell_id']
    # be sure to handle exception of no data output
    # convert data output from bases to Gb with three decimal places
    # use total estimated bases as output
    if 'estimated_selected_bases' in input_json_dict['acquisitions'][3]['acquisition_run_info']['yield_summary']:
        fields_from_json.data_output = round(pd.to_numeric(input_json_dict['acquisitions'][3]['acquisition_run_info']['yield_summary']['estimated_selected_bases'])/1e9, 3)
    else:
        fields_from_json.data_output = 0
    # get n50 in kb to two decimal places for estimated bases, not basecalled bases
    if 'n50' in input_json_dict['acquisitions'][3]['read_length_histogram'][3]['plot']['histogram_data'][0]:
        fields_from_json.n50 = round(pd.to_numeric(input_json_dict['acquisitions'][3]['read_length_histogram'][3]['plot']['histogram_data'][0]['n50'])/1e3, 2)
    else:
        fields_from_json.n50 = 0
    # need to branch here because minknow version is in different locations depending on json version type
    if 'software_versions' not in input_json_dict:
        # new software_versions path in 2024
        fields_from_json.minknow_version = input_json_dict['protocol_run_info']['software_versions']['distribution_version']
    else:
        # old software_versions path in 2023
        fields_from_json.minknow_version = input_json_dict['software_versions']['distribution_version']
    # get modal q score for passed and failed reads if found in json file
    if 'qscore_histograms' in input_json_dict['acquisitions'][3]:
        # test if passed reads present as element
        if len(input_json_dict['acquisitions'][3]['qscore_histograms'][0]['histogram_data']) >= 1:
            # test if passed reads present as element but no reads actually passed
            if 'modal_q_score' in input_json_dict['acquisitions'][3]['qscore_histograms'][0]['histogram_data'][0]:
                fields_from_json.modal_q_score_passed = input_json_dict['acquisitions'][3]['qscore_histograms'][0]['histogram_data'][0]['modal_q_score']
            else:
                fields_from_json.modal_q_score_passed = 'NA'
        else:
            fields_from_json.modal_q_score_passed = 'NA'
        # test if failed reads present
        if len(input_json_dict['acquisitions'][3]['qscore_histograms'][0]['histogram_data']) >= 2:
            # test if failed reads present as element but no reads actually failed
            if 'modal_q_score' in input_json_dict['acquisitions'][3]['qscore_histograms'][0]['histogram_data'][1]:
                fields_from_json.modal_q_score_failed = input_json_dict['acquisitions'][3]['qscore_histograms'][0]['histogram_data'][1]['modal_q_score']
            else:
                fields_from_json.modal_q_score_failed = 'NA'
        else:
            fields_from_json.modal_q_score_failed = 'NA'
    else:
        fields_from_json.modal_q_score_passed = 'NA'
        fields_from_json.modal_q_score_failed = 'NA'
    # get starting active pores if in json file
    if len(input_json_dict['acquisitions'][3]['acquisition_run_info']['bream_info']['mux_scan_results']) >= 1:
        # get first (index 0) mux scan results
        fields_from_json.starting_active_pores = input_json_dict['acquisitions'][3]['acquisition_run_info']['bream_info']['mux_scan_results'][0]['counts']['single_pore'] + input_json_dict['acquisitions'][3]['acquisition_run_info']['bream_info']['mux_scan_results'][0]['counts']['reserved_pore']
    else:
        fields_from_json.starting_active_pores = 'NA'
    # get second active pore count if in json file
    if len(input_json_dict['acquisitions'][3]['acquisition_run_info']['bream_info']['mux_scan_results']) >= 2:
        # get first (index 0) mux scan results
        fields_from_json.second_active_pore_count = input_json_dict['acquisitions'][3]['acquisition_run_info']['bream_info']['mux_scan_results'][1]['counts']['single_pore'] + input_json_dict['acquisitions'][3]['acquisition_run_info']['bream_info']['mux_scan_results'][1]['counts']['reserved_pore']
    else:
        fields_from_json.second_active_pore_count = 'NA'
    return fields_from_json
# load json file list
# user input
inparser = argparse.ArgumentParser(description = 'Extract data from long read JSON report')
inparser.add_argument('--json_dir', default=None, type=str, help = 'path to directory containing JSON files, if converting whole directory')
inparser.add_argument('--filelist', default=None, type=str, help = 'text file containing list of all JSON reports to parse')
inparser.add_argument('--output', action="store", type=str, dest="output_file", help="Output long read JSON report summary table in tab-delimited format")
args = inparser.parse_args()
# get list of files
if args.json_dir is not None:
    files = glob.glob(f'{args.json_dir}/*.json')
elif args.filelist is not None:
    with open(args.filelist, 'r') as infile:
        files = [x.strip() for x in infile.readlines()]
else:
    quit('ERROR: No directory (--json_dir) or file list (--filelist) provided!')
# create output data frame
# set indices
sequencing_report_df_indices = [np.arange(0,len(files))]
# set column names
sequencing_report_column_names = ['Experiment Name','Sample Name','Run Date','PROM ID','Flow Cell ID','Data output (Gb)','N50 (kb)','MinKNOW Version', 'Passed Modal Q Score', 'Failed Modal Q Score', 'Starting Active Pores', "Second Pore Count"]
# initialize data frame with said column names and filenames as indexes
sequencing_report_df = pd.DataFrame(index=sequencing_report_df_indices,columns=sequencing_report_column_names)
# main loop to process files
for idx, x in enumerate(files):
    try:
        # JSON file
        # debug by printing JSON file to stdout
        # print(x)
        f = open (x, "r")
        # Reading Python dictionary from JSON file
        data = json.loads(f.read())
        # get important information
        current_data_fields = get_fields_from_json(data)
        sequencing_report_df.loc[idx] = [current_data_fields.experiment_name,current_data_fields.sample_name,current_data_fields.run_date,current_data_fields.prom_id,current_data_fields.flow_cell_id,current_data_fields.data_output,current_data_fields.n50,current_data_fields.minknow_version,current_data_fields.modal_q_score_passed,current_data_fields.modal_q_score_failed,current_data_fields.starting_active_pores,current_data_fields.second_active_pore_count]
    except ValueError as e:
        print(e)
        continue
# print output data frame to tab delimited tsv file
sequencing_report_df.to_csv(args.output_file,sep='\t',index=False)
# end program
quit()

