import os
import json
import logging
import traceback

def validate_analysis_id(analysis_id):
    try:
        int(analysis_id.replace('EXA',''))
        return True
    except:
        logging.error(traceback.format_exc())
        return False

def get_analysis_files(result_directory):
    graph_file = os.path.join(result_directory, 'graph.data')
    report_json = os.path.join(result_directory, 'extanalysis_report.json')
    source_file = os.path.join(result_directory, 'source.json')
    
    return all([os.path.isfile(f) for f in [graph_file, report_json, source_file]]), {
        'graph': graph_file,
        'report': report_json,
        'source': source_file
    }

def load_analysis_data(files):
    with open(files['graph'], 'r') as f:
        graph_data = f.read()
    with open(files['source'], 'r') as f:
        source_data = json.loads(f.read())
    with open(files['report'], 'r') as f:
        report_data = json.loads(f.read())
    
    return graph_data, source_data, report_data 