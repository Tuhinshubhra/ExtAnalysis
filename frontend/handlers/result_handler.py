import os
import json
import logging
import traceback
import base64
from flask import render_template
import core.core as core
import core.helper as helper
from .data_handler import (
    get_basic_info, get_files_data, get_urls_data,
    get_permissions_data, get_domains_data, get_ips_data,
    get_emails_data, get_btc_data, get_comments_data,
    get_base64_data, get_manifest_data
)
from .file_handler import validate_analysis_id

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

def view_result(analysis_id):
    """Main view function that aggregates all data for the template"""
    if not validate_analysis_id(analysis_id):
        return render_template('error.html', 
                             error_title="Invalid Result ID", 
                             error_head="Invalid Result ID",
                             error_txt='Invalid result ID format')

    basic_info = get_basic_info(analysis_id)
    if 'error' in basic_info:
        return render_template('error.html', 
                             error_title="Invalid Result ID", 
                             error_head=f"Invalid Result ID: {analysis_id}", 
                             error_txt="Could not load analysis data")
    
    files_data = get_files_data(analysis_id)
    urls_data = get_urls_data(analysis_id)
    permissions_data = get_permissions_data(analysis_id)
    domains_data = get_domains_data(analysis_id)
    ips_data = get_ips_data(analysis_id)
    emails_data = get_emails_data(analysis_id)
    btc_data = get_btc_data(analysis_id)
    comments_data = get_comments_data(analysis_id)
    base64_data = get_base64_data(analysis_id)
    manifest_data = get_manifest_data(analysis_id)
    
    return render_template("report.html",
        analysis_id=analysis_id,
        basic_info=basic_info,
        files_table=files_data['files_table'],
        js_files_count=files_data['counts']['js'],
        css_files_count=files_data['counts']['css'],
        html_files_count=files_data['counts']['html'],
        json_files_count=files_data['counts']['json'],
        other_files_count=files_data['counts']['other'],
        static_files_count=files_data['counts']['static'],
        # ... other template variables ...
    ) 