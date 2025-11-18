import os
import json
import base64
from flask import url_for
import core.core as core
import core.helper as helper
from .file_handler import load_analysis_data, get_analysis_files

def get_analysis_data(analysis_id):
    """Helper function to get common analysis data"""
    analysis_info = core.get_result_info(analysis_id)
    if not analysis_info[0]:
        return None, None, None, None
        
    result_directory = analysis_info[1]['report_directory'].replace('<reports_path>', core.reports_path)
    files_valid, files = get_analysis_files(result_directory)
    if not files_valid:
        return None, None, None, None
        
    graph_data, source_data, report_data = load_analysis_data(files)
    return analysis_info, graph_data, source_data, report_data

def get_basic_info(analysis_id):
    analysis_info, _, _, report_data = get_analysis_data(analysis_id)
    if not analysis_info:
        return {'error': 'Invalid analysis data'}
        
    extension_type = report_data['type']
    if 'firefox' in extension_type.lower():
        extension_type = '<i class="fab fa-firefox"></i> ' + extension_type
    elif 'chrome' in extension_type.lower():
        extension_type = '<i class="fab fa-chrome"></i> ' + extension_type
        
    return {
        'name': report_data['name'],
        'version': report_data['version'],
        'author': report_data['author'],
        'description': report_data['description'],
        'time': analysis_info[1]['time'],
        'extension_type': extension_type
    }

def get_files_data(analysis_id):
    _, _, source_data, report_data = get_analysis_data(analysis_id)
    if not source_data:
        return {'error': 'Invalid analysis data'}
        
    files_table = '<table class="result-table" id="files-table"><thead><tr><th>File Name</th><th>Path</th><th>Size</th><th>Actions</th></tr></thead><tbody>'
    
    for file_info in source_data:
        file_name = source_data[file_info]['file_name']
        rel_path = source_data[file_info]['relative_path']
        file_id = source_data[file_info]['id']
        file_size = source_data[file_info]['file_size']
        
        file_action = f'<button class="bttn-fill bttn-xs bttn-primary" onclick="viewfile(\'{analysis_id}\', \'{file_id}\')"><i class="fas fa-code"></i> View Source</button>'
        
        if file_name.endswith('.js') and source_data[file_id]['retirejs_result']:
            file_action += f' <button class="bttn-fill bttn-xs bttn-danger" onclick="retirejsResult(\'{file_id}\', \'{analysis_id}\', \'{file_name}\')"><i class="fas fa-spider"></i> Vulnerabilities</button>'
            
        file_type = helper.get_file_type_icon(file_name)
        file_type = f'<img src="{file_type}" class="ft_icon">'
        
        files_table += f"<tr><td>{file_type} {file_name}</td><td>{rel_path}</td><td>{file_size}</td><td>{file_action}</td></tr>"
    
    files_table += '</tbody></table>'
    
    return {
        'files_table': files_table,
        'counts': {
            'js': len(report_data['files']['js']),
            'css': len(report_data['files']['css']),
            'html': len(report_data['files']['html']),
            'json': len(report_data['files']['json']),
            'other': len(report_data['files']['other']),
            'static': len(report_data['files']['static'])
        }
    }

def get_urls_data(analysis_id):
    _, _, _, report_data = get_analysis_data(analysis_id)
    if not report_data:
        return {'error': 'Invalid analysis data'}
    
    urls_table = '<table class="result-table" id="urls-table"><thead><tr><th>URL</th><th>Domain</th><th>File</th><th>Actions</th></tr></thead><tbody>'
    for url in report_data.get('urls', []):
        b64url = base64.b64encode(url['url'].encode()).decode()
        urls_table += f'''
            <tr>
                <td><a href="{url['url']}" target="_blank">{url['url']}</a></td>
                <td>{url['domain']}</td>
                <td>{url['file']}</td>
                <td>
                    <button class="bttn-fill bttn-xs bttn-primary" onclick="whois('{url['url']}')">WHOIS</button>
                    <button class="bttn-fill bttn-xs bttn-success" onclick="getSource('{b64url}')">Source</button>
                    <button class="bttn-fill bttn-xs bttn-danger" onclick="getHTTPHeaders('{b64url}')">Headers</button>
                </td>
            </tr>
        '''
    urls_table += '</tbody></table>'
    return {'urls_table': urls_table}

def get_permissions_data(analysis_id):
    _, _, _, report_data = get_analysis_data(analysis_id)
    if not report_data:
        return {'error': 'Invalid analysis data'}
    
    permissions = report_data.get('permissions', [])
    return {'permissions': permissions}

def get_domains_data(analysis_id):
    _, _, _, report_data = get_analysis_data(analysis_id)
    if not report_data:
        return {'error': 'Invalid analysis data'}
    
    domains = report_data.get('domains', [])
    return {'domains': domains}

def get_ips_data(analysis_id):
    _, _, _, report_data = get_analysis_data(analysis_id)
    if not report_data:
        return {'error': 'Invalid analysis data'}
    
    ips = report_data.get('ips', [])
    return {'ips': ips}

def get_emails_data(analysis_id):
    _, _, _, report_data = get_analysis_data(analysis_id)
    if not report_data:
        return {'error': 'Invalid analysis data'}
    
    emails = report_data.get('emails', [])
    return {'emails': emails}

def get_btc_data(analysis_id):
    _, _, _, report_data = get_analysis_data(analysis_id)
    if not report_data:
        return {'error': 'Invalid analysis data'}
    
    btc_addresses = report_data.get('btc_addresses', [])
    return {'btc_addresses': btc_addresses}

def get_comments_data(analysis_id):
    _, _, _, report_data = get_analysis_data(analysis_id)
    if not report_data:
        return {'error': 'Invalid analysis data'}
    
    comments = report_data.get('comments', [])
    return {'comments': comments}

def get_base64_data(analysis_id):
    _, _, _, report_data = get_analysis_data(analysis_id)
    if not report_data:
        return {'error': 'Invalid analysis data'}
    
    base64_strings = report_data.get('base64_strings', [])
    return {'base64_strings': base64_strings}

def get_manifest_data(analysis_id):
    _, _, _, report_data = get_analysis_data(analysis_id)
    if not report_data:
        return {'error': 'Invalid analysis data'}
    
    manifest = report_data.get('manifest', {})
    return {'manifest': manifest}

# Similar functions for other data types (urls, permissions, domains, etc.)
# Each function follows the same pattern of getting analysis data and returning
# formatted HTML tables or structured data 