"""
ExtAnalysis - Browser Extension Analysis Framework
Copyright (C) 2019 - 2020 Tuhinshubhra

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

def view(analysis_id):
    # so the result ids are in this format : EXA<some digits> so we can try to replace 'EXTA' and convert the rest to int if it passes it's a valid type
    try:
        int(analysis_id.replace('EXA','')) # Check

        analysis_info = core.get_result_info(analysis_id)
        
        if not analysis_info[0]:
            # Could not get analysis_info
            error_txt = 'Something went wrong while getting analysis info!<br>Error: ' + analysis_info[1]
            return render_template('error.html', error_title = "Invalid Result ID", error_head = "Invalid Result ID: {0}".format(analysis_id) , error_txt=error_txt)
        else:
            result_directory = analysis_info[1]['report_directory'].replace('<reports_path>', core.reports_path)

            if os.path.isdir(result_directory):
                # result directory found let's check for all necessary files
                graph_file = os.path.join(result_directory, 'graph.data')
                report_json = os.path.join(result_directory, 'extanalysis_report.json')
                source_file = os.path.join(result_directory, 'source.json')


                if all([os.path.isfile(the_file) for the_file in [graph_file, report_json, source_file]]):
                    core.updatelog('Viewing Analysis {0}'.format(analysis_id))
                    graph_data = open(graph_file, 'r')
                    graph_data = graph_data.read()
                    source_data = open(source_file, 'r')
                    source_data = json.loads(source_data.read())
                    report_data = open(report_json, 'r')
                    report_data = json.loads(report_data.read())

                    # prepare data to be sent to result page
                    basic_info_t = [report_data['name'], 
                                    report_data['version'], 
                                    report_data['author'], 
                                    report_data['description'],
                                    analysis_info[1]['time']
                                    ]
                    
                    # extension type
                    extension_type = report_data['type']
                    if 'firefox' in extension_type.lower():
                        extension_type = '<i class="fab fa-firefox"></i> ' + extension_type
                    elif 'chrome' in extension_type.lower():
                        extension_type = '<i class="fab fa-chrome"></i> ' + extension_type

                    # URL Table
                    if report_data['urls'] != []:
                        urls_table = '<table class="result-table" id="urls-table"><thead><tr><th>URL</th><th>Domain</th><th>File</th><th>Actions</th></tr></thead><tbody>'
                        extjs_table = '<table class="result-table" id="extjs-table"><thead><tr><th>URL</th><th>Domain</th><th>File</th><th>Actions</th></tr></thead><tbody>'
                        done_urls = []
                        done_ejss = []
                        urls_count = 0
                        extjs_count = 0
                        for aurl in report_data['urls']:
                            if aurl['url'].endswith('.js'):
                                if aurl['url'] not in done_ejss:
                                    done_ejss.append(aurl['url'])
                                    aurl_href = '<a href="{0}" class="ext_url" target="_blank"><i class="fas fa-external-link-alt" style="font-size:12px;"></i> {0}</a>'.format(aurl['url'])
                                    extjs_table += '<tr><td>' + aurl_href + '</td>'
                                    b64url = "'" + base64.b64encode(aurl['url'].encode('ascii', 'ignore')).decode('ascii') + "'"
                                    extjs_table += '<td>{0}</td><td>{1}</td>'.format(aurl['domain'], aurl['file'])
                                    extjs_table += '<td><button class="bttn-fill bttn-xs bttn-primary" onclick=whois(\'{1}\')><i class="fab fa-searchengin"></i> WHOIS</button> <button class="bttn-fill bttn-xs bttn-success" onclick="getSource({0})"><i class="fas fa-code"></i> Source</button> <button class="bttn-fill bttn-xs bttn-danger" onclick="getHTTPHeaders({0})"><i class="fas fa-stream"></i> HTTP Headers</button></td></tr>'.format(b64url, aurl['url'])
                                    extjs_count += 1
                            else:
                                if aurl['url'] not in done_urls:
                                    done_urls.append(aurl['url'])
                                    aurl_href = '<a href="{0}" class="ext_url" target="_blank"><i class="fas fa-external-link-alt" style="font-size:12px;"></i> {0}</a>'.format(aurl['url'])
                                    urls_table += '<tr><td>' + aurl_href + '</td>'
                                    urls_table += '<td>{0}</td><td>{1}</td>'.format(aurl['domain'], aurl['file'])
                                    b64url = "'" + base64.b64encode(aurl['url'].encode('ascii', 'ignore')).decode('ascii') + "'"
                                    urls_table += '<td><button class="bttn-fill bttn-xs bttn-primary" onclick=whois(\'{1}\')><i class="fab fa-searchengin"></i> WHOIS</button> <button class="bttn-fill bttn-xs bttn-success" onclick="getSource({0})"><i class="fas fa-code"></i> Source</button> <button class="bttn-fill bttn-xs bttn-danger" onclick="getHTTPHeaders({0})"><i class="fas fa-stream"></i> HTTP Headers</button></td></tr>'.format(b64url, aurl['url'])
                                    urls_count += 1

                        if done_urls != []:
                            urls_table += '</tbody></table>'
                        else:
                            urls_table = '<h3 class="nothing"> No URLs Found </h3>'

                        if done_ejss != []:
                            extjs_table += '</tbody></table>'
                        else:
                            extjs_table = '<h3 class="nothing"> No External JavaScript Found in any files! </h3>'
                    else:
                        urls_table = '<h3 class="nothing"> No URLs Found </h3>'
                        extjs_table = '<h3 class="nothing"> No External JavaScript Found in any files! </h3>'
                        extjs_count = 0
                        urls_count = 0

                    # Domains div
                    if report_data['domains'] != []:
                        domains_table = '<table class="result-table" id="domains-table"><thead><tr><th>Country</th><th>Domain</th><th>IP Address</th><th>Actions</th></tr></thead><tbody>'
                        for domain in report_data['domains']:
                            domain_flag = helper.fixpath(core.path + '/static/images/flags/' + domain['country_code'] + '.png')
                            if os.path.isfile(domain_flag):
                                flag_path = url_for('static',filename='images/flags/' + domain['country_code'] + '.png')
                            else:
                                flag_path = url_for('static',filename='images/flags/unknown.png')
                            country_html = '<img src="{0}" class="country_flag"> {1}'.format(flag_path, domain['country'])
                            domains_table += '<tr><td>{4}</td><td>{0}</td><td>{2}</td><!-- td>{1}</td --><td><button class="bttn-fill bttn-xs bttn-danger" onclick=whois("{0}")><i class="fab fa-searchengin"></i> WHOIS</button> <button class="bttn-fill bttn-xs bttn-primary" onclick="domainvt(\'{0}\', \'{3}\')"><i class="fas fa-hourglass-end"></i> VT Report</button> <button class="bttn-fill bttn-xs bttn-success" onclick=geoip("{2}")><i class="fas fa-globe-americas"></i> Geo-IP Lookup</button></td></tr>'.format(domain['name'], '0/66', domain['ip'], analysis_id, country_html)
                        domains_table += '</tbody></table>'
                    else:
                        domains_table = '<h3 class="nothing"> No Domains Extracted! </h3>'
                    unique_domains = len(report_data['domains'])

                        
                    # Permissions div containing all permissions accordions
                    permissions_div = ""
                    for perm in report_data['permissions']:
                        #perm_html = '<div class="perm"><div class="perm-name">{0}</div> <div class="perm-desc">{1}</div> <div class="perm-warn">{2}</div></div>'.format(perm['name'], perm['description'], (perm['warning'] if perm['warning'] != 'na' else ''))
                        perm_html = '<div class="accordion"><div class="accordion__item"><div class="accordion__question">{0} {1} <div class="risk-pill {4}">{4}</div></div><div class="accordion__answer">{2} <div class="warning"> {3} </div></div></div></div>'.format(perm['badge'], helper.escape(perm['name']), perm['description'], (perm['warning'] if perm['warning'] != 'na' else ''), perm['risk'])
                        permissions_div += perm_html
                    permissions_count = len(report_data['permissions'])



                    # table consisting of all the viewable source files
                    files_table = '<table class="result-table" id="files-table"><thead><tr><th>File Name</th><th>Path</th><th>Size</th><th>Actions</th></tr></thead><tbody>'
                    for file_info in source_data:
                        file_name = source_data[file_info]['file_name']
                        rel_path = source_data[file_info]['relative_path']
                        file_id = source_data[file_info]['id']
                        file_size = source_data[file_info]['file_size']
                        file_action = '<button class="bttn-fill bttn-xs bttn-primary" onclick="viewfile(\'' + analysis_id + '\', \'' + file_id + '\')"><i class="fas fa-code"></i> View Source</button>'
                        if file_name.endswith('.js'):
                            # Add button for viewing retirejs vulnerability scan results
                            # okay it's annoying to show button on every js file let's just show where there is vuln.
                            if source_data[file_id]['retirejs_result'] != []:
                                file_action += ' <button class="bttn-fill bttn-xs bttn-danger" onclick="retirejsResult({0}, {1}, {2})"><i class="fas fa-spider"></i> Vulnerabilities</button>'.format("'"+file_id+"'", "'"+analysis_id+"'", "'"+file_name+"'")
                        file_type = helper.fixpath(core.path + '/static/images/' + file_name.split('.')[-1] + '1.png')
                        if os.path.isfile(file_type):
                            file_type = file_name.split('.')[-1] + '1.png'
                        else:
                            file_type = 'other1.png'
                        file_type = url_for('static',filename='images/' + file_type)
                        file_type = '<img src="{0}" class="ft_icon">'.format(file_type)
                        file_html = "<tr><td>{2} {0}</td><td>{1}</td><td>{4}</td><td>{3}</td></tr>".format(file_name, rel_path, file_type, file_action, file_size)
                        files_table += file_html
                    files_table += '</tbody></table>'


                    # table consisting of ipv6 and ipv4 addresses
                    if report_data['ipv4_addresses'] == [] and report_data['ipv6_addresses'] == []:
                        ips_table = '<h3 class="nothing">No IPv4 or IPv6 addresses found!</h3>'
                    else:
                        ips_table = '<table class="result-table" id="ips_table"><thead><tr><th>IP Address</th><th>Type</th><th>File</th></tr></thead><tbody>'
                        for ip in report_data['ipv4_addresses']:
                            ips_table += '<tr><td>{0}</td><td>{1}</td><td>{2}</td></tr>'.format(ip['address'], 'IPv4', ip['file'])
                        for ip in report_data['ipv6_addresses']:
                            ips_table += '<tr><td>{0}</td><td>{1}</td><td>{2}</td></tr>'.format(ip['address'], 'IPv6', ip['file'])
                        ips_table += '</tbody></table>'


                    # table consisting of emails
                    if report_data['emails'] != []:
                        mails_table = '<table class="result-table" id="mails_table"><thead><tr><th>Email Address</th><th>File</th></tr></thead><tbody>'
                        for mail in report_data['emails']:
                            mails_table += '<tr><td>{0}</td><td>{1}</td></tr>'.format(mail['mail'], mail['file'])
                        mails_table += '</tbody></table>'
                    else:
                        mails_table = '<h3 class="nothing">No email addresses found in any of the files!</h3>'

                    # table containing btc addresses
                    if report_data['bitcoin_addresses'] != []:
                        btc_table = '<table class="result-table" id="btc_table"><thead><tr><th>BTC Address</th><th>File</th></tr></thead><tbody>'
                        for mail in report_data['bitcoin_addresses']:
                            btc_table += '<tr><td>{0}</td><td>{1}</td></tr>'.format(mail['address'], mail['file'])
                        btc_table += '</tbody></table>'
                    else:
                        btc_table = '<h3 class="nothing">No Bitcoin Address found!</h3>'

                    # table containing comments
                    if report_data['comments'] != []:
                        comments_table = '<table class="result-table" id="comments_table"><thead><tr><th>Comment</th><th>File</th></tr></thead><tbody>'
                        for comment in report_data['comments']:
                            comments_table += '<tr><td>{0}</td><td>{1}</td></tr>'.format(helper.escape(comment['comment']), comment['file'])
                        comments_table += '</tbody></table>'
                    else:
                        comments_table = '<h3 class="nothing">No comments found in any js/html/css files!</h3>'


                    # table containing base64 encoded strings
                    if report_data['base64_strings'] != []:
                        base64_table = '<table class="result-table" id="base64_table"><thead><tr><th>Base64 Encoded String</th><th>File</th></tr></thead><tbody>'
                        for b64 in report_data['base64_strings']:
                            base64_table += '<tr><td>{0}</td><td>{1}</td></tr>'.format(b64['string'], b64['file'])
                        base64_table += '</tbody></table>'
                    else:
                        base64_table = '<h3 class="nothing">No base64 encoded string found in any js/html/css files!</h3>'

                    manifest_content = json.dumps(report_data['manifest'])

                    '''
                    Files count
                    '''
                    js_files_count = len(report_data['files']['js'])
                    css_files_count = len(report_data['files']['css'])
                    html_files_count = len(report_data['files']['html'])
                    json_files_count = len(report_data['files']['json'])
                    other_files_count = len(report_data['files']['other'])
                    static_files_count = len(report_data['files']['static'])

                    return render_template("report.html",
                                            extension_type = extension_type, 
                                            graph_data = graph_data, 
                                            basic_info = basic_info_t, 
                                            urls_table = urls_table, 
                                            permissions_div = permissions_div, 
                                            analysis_id=analysis_id, 
                                            files_table=files_table, 
                                            manifest_content=manifest_content,
                                            domains_table = domains_table,
                                            base64_table = base64_table,
                                            comments_table = comments_table,
                                            ips_table = ips_table,
                                            btc_table = btc_table,
                                            mails_table = mails_table,
                                            extjs_table = extjs_table,
                                            urls_count = urls_count,
                                            extjs_count = extjs_count,
                                            permissions_count = permissions_count,
                                            unique_domains = unique_domains,
                                            js_files_count = js_files_count,
                                            css_files_count = css_files_count,
                                            html_files_count = html_files_count,
                                            json_files_count = json_files_count,
                                            other_files_count = other_files_count,
                                            static_files_count = static_files_count
                                        )
                
                
                else:
                    error_txt = 'All the result files are not found.. Try scanning the extension again! and don\'t mess with the result files this time'
                    return render_template('error.html', error_title = "Malformed Result", error_head = "Incomplete Result", error_txt=error_txt)
           
           
            else:
                error_txt = 'The result directory corresponding to result id {0} could not be found... hence ExtAnalysis has nothing to show'.format(analysis_id)
                return render_template('error.html', error_title = "Result Directory Not Found", error_head = "Result Directory Not Foundt", error_txt=error_txt)
    
    except:
        logging.error(traceback.format_exc())
        return render_template('error.html', error_title = "Invalid Result ID", error_head = "Invalid Result ID" , error_txt='There seems to be no result corresponding to the provided ID. Did you delete the result? or maybe you did some weird shit with the parameter?')