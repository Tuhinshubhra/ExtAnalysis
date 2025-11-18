"""
ExtAnalysis - Browser Extension Analysis Framework
Copyright (C) 2019 - 2022 Tuhinshubhra

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import core.core as core
import core.helper as helper
import os
import json
from flask import Flask, request, render_template, redirect, url_for, send_from_directory
import logging, traceback
import base64

app = Flask(__name__)

def get_extension_type(extension_type):
    if 'firefox' in extension_type.lower():
        return '<i class="fab fa-firefox"></i> ' + extension_type
    elif 'chrome' in extension_type.lower():
        return '<i class="fab fa-chrome"></i> ' + extension_type
    return extension_type

def generate_files_table(source_data):
    files_table = ''
    for file_info in source_data:
        file_name = source_data[file_info]['file_name']
        rel_path = source_data[file_info]['relative_path']
        file_id = source_data[file_info]['id']
        file_size = source_data[file_info]['file_size']
        file_action = '<button class="bttn-fill bttn-xs bttn-primary" onclick="viewfile(\'' + file_id + '\')"><i class="fas fa-code"></i> View Source</button>'
        if file_name.endswith('.js'):
            if source_data[file_id]['retirejs_result'] != []:
                file_action += ' <button class="bttn-fill bttn-xs bttn-danger" onclick="retirejsResult({0}, {1}, {2})"><i class="fas fa-spider"></i> Vulnerabilities</button>'.format("'"+file_id+"'", "'"+file_id+"'", "'"+file_name+"'")
        file_type = helper.fixpath(core.path + '/static/images/' + file_name.split('.')[-1] + '1.png')
        if os.path.isfile(file_type):
            file_type = file_name.split('.')[-1] + '1.png'
        else:
            file_type = 'other1.png'
        file_type = url_for('static',filename='images/' + file_type)
        file_type = '<img src="{0}" class="ft_icon">'.format(file_type)
        file_html = "<tr><td>{2} {0}</td><td>{1}</td><td>{4}</td><td>{3}</td></tr>".format(file_name, rel_path, file_type, file_action, file_size)
        files_table += file_html
    return files_table

def generate_permissions_div(permissions):
    permissions_div = ""
    for perm in permissions:
        perm_html = '<div class="accordion"><div class="accordion__item"><div class="accordion__question">{0} {1} <div class="risk-pill {4}">{4}</div></div><div class="accordion__answer">{2} <div class="warning"> {3} </div></div></div></div>'.format(perm['badge'], helper.escape(perm['name']), perm['description'], (perm['warning'] if perm['warning'] != 'na' else ''), perm['risk'])
        permissions_div += perm_html
    return permissions_div

def generate_domains_table(domains):
    if not domains:
        return '<h3 class="nothing"> No Domains Extracted! </h3>'
    
    domains_table = '<tbody>'
    for domain in domains:
        domain_flag = helper.fixpath(core.path + '/static/images/flags/' + domain['country_code'] + '.png')
        if os.path.isfile(domain_flag):
            flag_path = url_for('static',filename='images/flags/' + domain['country_code'] + '.png')
        else:
            flag_path = url_for('static',filename='images/flags/unknown.png')
        country_html = '<img src="{0}" class="country_flag"> {1}'.format(flag_path, domain['country'])
        domains_table += '<tr><td>{4}</td><td>{0}</td><td>{2}</td><td><button class="bttn-fill bttn-xs bttn-danger" onclick=whois("{0}")><i class="fab fa-searchengin"></i> WHOIS</button> <button class="bttn-fill bttn-xs bttn-primary" onclick="domainvt(\'{0}\')"><i class="fas fa-hourglass-end"></i> VT Report</button> <button class="bttn-fill bttn-xs bttn-success" onclick=geoip("{2}")><i class="fas fa-globe-americas"></i> Geo-IP Lookup</button></td></tr>'.format(domain['name'], '0/66', domain['ip'], '', country_html)
    domains_table += '</tbody>'
    return domains_table

def generate_urls_table(urls):
    if not urls:
        return '<h3 class="nothing"> No URLs Found </h3>'
    
    urls_table = '<tbody>'
    done_urls = []
    for aurl in urls:
        if not aurl['url'].endswith('.js') and aurl['url'] not in done_urls:
            done_urls.append(aurl['url'])
            aurl_href = '<a href="{0}" class="ext_url" target="_blank"><i class="fas fa-external-link-alt" style="font-size:12px;"></i> {0}</a>'.format(aurl['url'])
            urls_table += '<tr><td>' + aurl_href + '</td>'
            urls_table += '<td>{0}</td><td>{1}</td>'.format(aurl['domain'], aurl['file'])
            b64url = "'" + base64.b64encode(aurl['url'].encode('ascii', 'ignore')).decode('ascii') + "'"
            urls_table += '<td><button class="bttn-fill bttn-xs bttn-primary" onclick=whois(\'{1}\')><i class="fab fa-searchengin"></i> WHOIS</button> <button class="bttn-fill bttn-xs bttn-success" onclick="getSource({0})"><i class="fas fa-code"></i> Source</button> <button class="bttn-fill bttn-xs bttn-danger" onclick="getHTTPHeaders({0})"><i class="fas fa-stream"></i> HTTP Headers</button></td></tr>'.format(b64url, aurl['url'])
    urls_table += '</tbody>'
    return urls_table

def generate_extjs_table(urls):
    if not any(u['url'].endswith('.js') for u in urls):
        return '<h3 class="nothing"> No External JavaScript Found in any files! </h3>'
    
    extjs_table = '<tbody>'
    done_ejss = []
    for aurl in urls:
        if aurl['url'].endswith('.js') and aurl['url'] not in done_ejss:
            done_ejss.append(aurl['url'])
            aurl_href = '<a href="{0}" class="ext_url" target="_blank"><i class="fas fa-external-link-alt" style="font-size:12px;"></i> {0}</a>'.format(aurl['url'])
            extjs_table += '<tr><td>' + aurl_href + '</td>'
            b64url = "'" + base64.b64encode(aurl['url'].encode('ascii', 'ignore')).decode('ascii') + "'"
            extjs_table += '<td>{0}</td><td>{1}</td>'.format(aurl['domain'], aurl['file'])
            extjs_table += '<td><button class="bttn-fill bttn-xs bttn-primary" onclick=whois(\'{1}\')><i class="fab fa-searchengin"></i> WHOIS</button> <button class="bttn-fill bttn-xs bttn-success" onclick="getSource({0})"><i class="fas fa-code"></i> Source</button> <button class="bttn-fill bttn-xs bttn-danger" onclick="getHTTPHeaders({0})"><i class="fas fa-stream"></i> HTTP Headers</button></td></tr>'.format(b64url, aurl['url'])
    extjs_table += '</tbody>'
    return extjs_table

def generate_ips_table(report_data):
    if not report_data.get('ipv4_addresses', []) and not report_data.get('ipv6_addresses', []):
        return '<h3 class="nothing">No IPv4 or IPv6 addresses found!</h3>'
    
    ips_table = '<tbody>'
    for ip in report_data.get('ipv4_addresses', []):
        ips_table += '<tr><td>{0}</td><td>{1}</td><td>{2}</td></tr>'.format(ip['address'], 'IPv4', ip['file'])
    for ip in report_data.get('ipv6_addresses', []):
        ips_table += '<tr><td>{0}</td><td>{1}</td><td>{2}</td></tr>'.format(ip['address'], 'IPv6', ip['file'])
    ips_table += '</tbody>'
    return ips_table

def generate_mails_table(emails):
    if not emails:
        return '<h3 class="nothing">No email addresses found in any of the files!</h3>'
    
    mails_table = '<tbody>'
    for mail in emails:
        mails_table += '<tr><td>{0}</td><td>{1}</td></tr>'.format(mail['mail'], mail['file'])
    mails_table += '</tbody>'
    return mails_table

def generate_btc_table(btc_addresses):
    if not btc_addresses:
        return '<h3 class="nothing">No Bitcoin Address found!</h3>'
    
    btc_table = '<tbody>'
    for btc in btc_addresses:
        btc_table += '<tr><td>{0}</td><td>{1}</td></tr>'.format(btc['address'], btc['file'])
    btc_table += '</tbody>'
    return btc_table

def generate_comments_table(comments):
    if not comments:
        return '<h3 class="nothing">No comments found in any js/html/css files!</h3>'
    
    comments_table = '<tbody>'
    for comment in comments:
        comments_table += '<tr><td>{0}</td><td>{1}</td></tr>'.format(helper.escape(comment['comment']), comment['file'])
    comments_table += '</tbody>'
    return comments_table

def generate_base64_table(base64_strings):
    if not base64_strings:
        return '<h3 class="nothing">No base64 encoded string found in any js/html/css files!</h3>'
    
    base64_table = '<tbody>'
    for b64 in base64_strings:
        base64_table += '<tr><td>{0}</td><td>{1}</td></tr>'.format(b64['string'], b64['file'])
    base64_table += '</tbody>'
    return base64_table

@app.route('/analysis/<analysis_id>/')  # Default route
@app.route('/analysis/<analysis_id>/<tab>/')  # Tab-specific route
def view(analysis_id, tab='basic_info'):
    try:
        int(analysis_id.replace('EXA','')) # Check
        analysis_info = core.get_result_info(analysis_id)
        
        if not analysis_info[0]:
            error_txt = 'Something went wrong while getting analysis info!<br>Error: ' + analysis_info[1]
            return render_template('error.html', error_title = "Invalid Result ID", error_head = "Invalid Result ID: {0}".format(analysis_id) , error_txt=error_txt)
        
        # Validate tab parameter
        valid_tabs = ['basic_info', 'files', 'permissions', 'urls_domains', 'gathered_intels']
        if tab not in valid_tabs:
            tab = 'basic_info'
            
        # Get result data
        result_directory = analysis_info[1]['report_directory'].replace('<reports_path>', core.reports_path)
        
        if not os.path.isdir(result_directory):
            error_txt = 'The result directory corresponding to result id {0} could not be found'.format(analysis_id)
            return render_template('error.html', error_title="Result Directory Not Found", error_head="Result Directory Not Found", error_txt=error_txt)

        # Load required files
        graph_file = os.path.join(result_directory, 'graph.data')
        report_json = os.path.join(result_directory, 'extanalysis_report.json')
        source_file = os.path.join(result_directory, 'source.json')
        
        if not all(os.path.isfile(f) for f in [graph_file, report_json, source_file]):
            error_txt = 'All the result files are not found. Try scanning the extension again!'
            return render_template('error.html', error_title="Malformed Result", error_head="Incomplete Result", error_txt=error_txt)

        # Load data from files
        graph_data = open(graph_file, 'r').read()
        report_data = json.loads(open(report_json, 'r').read())
        source_data = json.loads(open(source_file, 'r').read())

        # Prepare template data based on selected tab
        template_data = {
            'analysis_id': analysis_id,
            'current_tab': tab,
            'graph_data': graph_data,
            'basic_info': [
                report_data.get('name', 'Unknown Name'),
                report_data.get('version', 'Unknown Version'), 
                report_data.get('author', 'Unknown Author'),
                report_data.get('description', 'No description available'),
                analysis_info[1]['time']
            ],
            'extension_type': get_extension_type(report_data.get('type', 'unknown'))
        }

        # Add tab-specific data
        if tab == 'basic_info':
            template_data.update({
                'manifest_content': json.dumps(report_data.get('manifest', {})),
                'permissions_count': len(report_data.get('permissions', [])),
                'unique_domains': len(report_data.get('domains', [])),
                'urls_count': len([u for u in report_data.get('urls', []) if not u['url'].endswith('.js')]),
                'extjs_count': len([u for u in report_data.get('urls', []) if u['url'].endswith('.js')])
            })
            
        elif tab == 'files':
            template_data.update({
                'files_table': generate_files_table(source_data),
                'js_files_count': len(report_data.get('files', {}).get('js', [])),
                'css_files_count': len(report_data.get('files', {}).get('css', [])), 
                'html_files_count': len(report_data.get('files', {}).get('html', [])),
                'json_files_count': len(report_data.get('files', {}).get('json', [])),
                'other_files_count': len(report_data.get('files', {}).get('other', [])),
                'static_files_count': len(report_data.get('files', {}).get('static', []))
            })
            
        elif tab == 'permissions':
            template_data['permissions_div'] = generate_permissions_div(report_data.get('permissions', []))
            
        elif tab == 'urls_domains':
            template_data.update({
                'domains_table': generate_domains_table(report_data.get('domains', [])),
                'urls_table': generate_urls_table(report_data.get('urls', [])),
                'extjs_table': generate_extjs_table(report_data.get('urls', []))
            })
            
        elif tab == 'gathered_intels':
            template_data.update({
                'ips_table': generate_ips_table(report_data),
                'btc_table': generate_btc_table(report_data.get('bitcoin_addresses', [])),
                'mails_table': generate_mails_table(report_data.get('emails', [])),
                'comments_table': generate_comments_table(report_data.get('comments', [])),
                'base64_table': generate_base64_table(report_data.get('base64_strings', []))
            })

        return render_template("report.html", **template_data)

    except:
        logging.error(traceback.format_exc())
        return render_template('error.html', error_title="Invalid Result ID", error_head="Invalid Result ID", error_txt='Invalid result ID provided')