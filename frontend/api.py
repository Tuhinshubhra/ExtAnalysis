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
import core.analyze as analysis
import core.downloader as download_extension
import os
import json
from flask import Flask, request, render_template, redirect, url_for, send_from_directory
import logging
import traceback
import core.scans as scan
import base64


def view(query, allargs):
    if query == 'dlanalysis':
        try:
            extension_id = allargs.get('extid')
            saveas = ""
            try:
                saveas = allargs.get('savedir')
                if saveas == "" or saveas == " ":
                    saveas = extension_id
            except Exception as e:
                print('Save name not specified')
            try:
                downloader = download_extension.ExtensionDownloader()
                download_log = downloader.download_chrome(extension_id, saveas)
                if download_log:
                    aok = analysis.analyze(
                        saveas + '.crx', 'Remote Google Chrome Extension')
                    return (aok)
                else:
                    return ('error: Something went wrong while downloading extension')
            except Exception as e:
                core.updatelog(
                    'Something went wrong while downloading extension: ' + str(e))
                return ('error: Something went wrong while downloading extension, check log for more information')

        except Exception as e:
            core.updatelog('Something went wrong: ' + str(e))
            return ('error: Something went wrong while downloading extension, check log for more information')

    elif query == 'firefoxaddon':
        try:
            addonurl = allargs.get('addonurl')
            try:
                downloader = download_extension.ExtensionDownloader()
                download_log = downloader.download_firefox(addonurl)
                if download_log:
                    aok = analysis.analyze(
                        download_log + '.xpi', 'Remote Firefox Addon')
                    return (aok)
                else:
                    return ('error: Something went wrong while downloading extension')
            except Exception as e:
                core.updatelog(
                    'Something went wrong while downloading extension: ' + str(e))
                return ('error: Something went wrong while downloading extension, check log for more information')
        except Exception as e:
            core.updatelog('Something went wrong: ' + str(e))
            return ('error: Something went wrong while downloading extension, check log for more information')

    elif query == 'edgeaddon':
        try:
            addonurl = allargs.get('addonurl')
            saveas = addonurl.split('/')[-1]
            try:
                downloader = download_extension.ExtensionDownloader()
                download_log = downloader.download_edge(addonurl)
                if download_log:
                    aok = analysis.analyze(
                        saveas + '.crx', 'Remote Edge Extension')
                    return (aok)
                else:
                    return ('error: Something went wrong while downloading extension')
            except Exception as e:
                core.updatelog(
                    'Something went wrong while downloading extension: ' + str(e))
                return ('error: Something went wrong while downloading extension, check log for more information')
        except Exception as e:
            core.updatelog('Something went wrong: ' + str(e))
            return ('error: Something went wrong while downloading extension, check log for more information')

    elif query == 'results':
        reportids = core.reportids
        if reportids == {}:
            # Result index not loaded so let's load it and show em results
            core.updatelog('Reading report index and loading json')
            ridfile = core.report_index
            ridcnt = open(ridfile, 'r', encoding='utf8')
            ridcnt = ridcnt.read()
            reportids = json.loads(ridcnt)

        rd = "<table class='result-table' id='result-table'><thead><tr><th>Name</th><th>Version</th><th>Date</th><th>Actions</th></tr></thead><tbody>"
        for areport in reportids['reports']:
            report_name = areport['name']
            report_id = areport['id']
            report_date = areport['time']
            report_version = areport['version']
            rd += '<tr><td>' + report_name + '</td><td>' + report_version + '</td><td>' + report_date + \
                '</td><td><button class="bttn-fill bttn-xs bttn-primary" onclick=viewResult(\'' + report_id + '\')><i class="fas fa-eye"></i> View</button> <button class="bttn-fill bttn-xs bttn-danger" onclick=deleteResult(\'' + \
                report_id + '\')><i class="fas fa-trash"></i> Delete</button></td></tr>'
        return (rd + '</tbody></table><br>')

    elif query == 'getlocalextensions':
        try:
            browser = allargs.get('browser')
            if browser == 'googlechrome':
                import core.localextensions as localextensions
                lexts = localextensions.GetLocalExtensions()
                exts = ""
                exts = lexts.googlechrome()
                if exts != False and exts != [] and exts != None:
                    return_html = "<table class='result-table' id='result-table'><thead><tr><th>Extension Name</th><th>Action</th></tr></thead><tbody>"
                    for ext in exts:
                        ext_info = ext.split(',')
                        return_html += '<tr><td>' + ext_info[
                            0] + '</td><td><button class="bttn-fill bttn-xs bttn-success" onclick="analyzeLocalExtension(\'' + \
                            ext_info[1].replace('\\',
                                                '\\\\') + '\', \'googlechrome\')"><i class="fas fa-bolt"></i> Analyze</button></td></tr>'
                    return (return_html + '</tbody></table>')
                else:
                    return (
                        'error: Something went wrong while getting local Google Chrome extensions! Check log for more information')
            elif browser == 'firefox':
                import core.localextensions as localextensions
                lexts = localextensions.GetLocalExtensions()
                exts = lexts.firefox()
                if exts != False and exts != [] and exts != None:
                    return_html = "<table class='result-table' id='result-table'><thead><tr><th>Extension Name</th><th>Action</th></tr></thead><tbody>"
                    for ext in exts:
                        ext_info = ext.split(',')
                        return_html += '<tr><td>' + ext_info[
                            0] + '</td><td><button class="bttn-fill bttn-xs bttn-success" onclick="analyzeLocalExtension(\'' + \
                            ext_info[1].replace('\\',
                                                '\\\\') + '\', \'firefox\')"><i class="fas fa-bolt"></i> Analyze</button></td></tr>'
                    return (return_html + '</tbody></table>')
                else:
                    return (
                        'error: Something went wrong while getting local firefox extensions! Check log for more information')
            elif browser == 'brave':
                import core.localextensions as localextensions
                lexts = localextensions.GetLocalExtensions()
                exts = ""
                exts = lexts.braveLocalExtensionsCheck()
                if exts != False and exts != [] and exts != None:
                    return_html = "<table class='result-table' id='result-table'><thead><tr><th>Extension Name</th><th>Action</th></tr></thead><tbody>"
                    for ext in exts:
                        ext_info = ext.split(',')
                        return_html += '<tr><td>' + ext_info[
                            0] + '</td><td><button class="bttn-fill bttn-xs bttn-success" onclick="analyzeLocalExtension(\'' + \
                            ext_info[1].replace('\\',
                                                '\\\\') + '\', \'brave\')"><i class="fas fa-bolt"></i> Analyze</button></td></tr>'
                    return (return_html + '</tbody></table>')
                else:
                    return (
                        'error: Something went wrong while getting local Brave browser extensions! Check log for more information')

            elif browser == 'vivaldi':
                import core.localextensions as localextensions
                lexts = localextensions.GetLocalExtensions()
                exts = ""
                exts = lexts.vivaldi_local_extensions_check()
                if exts and len(exts) > 0:
                    return_html = "<table class='result-table' id='result-table'><thead><tr><th>Extension Name</th><th>Action</th></tr></thead><tbody>"
                    for ext in exts:
                        ext_info = ext.split(',')
                        return_html += '<tr><td>' + ext_info[
                            0] + '</td><td><button class="bttn-fill bttn-xs bttn-success" onclick="analyzeLocalExtension(\'' + \
                            ext_info[1].replace('\\',
                                                '\\\\') + '\', \'vivaldi\')"><i class="fas fa-bolt"></i> Analyze</button></td></tr>'
                    return (return_html + '</tbody></table>')
                else:
                    return (
                        'error: Something went wrong while getting local Vivaldi browser extensions! Check log for more information')

            else:
                return ('error: Invalid Browser!')
        except Exception:
            logging.error(traceback.format_exc())
            return ('error: Incomplete Query')

    elif query == 'analyzelocalextension':
        try:
            browser = allargs.get('browser')
            path_to_local = allargs.get('path')
            path = helper.fixpath(path_to_local)

            if browser == 'firefox' and os.path.isfile(path):
                # valid firefox extension
                import core.localextensions as localextensions
                analysis_stat = localextensions.analyzelocalfirefoxextension(
                    path)
                return (analysis_stat)

            elif browser == 'googlechrome' and os.path.isdir(path):
                if os.path.isfile(os.path.join(path, 'manifest.json')):
                    analysis_stat = analysis.analyze(
                        path, 'Local Google Chrome Extension')
                    return (analysis_stat)
                else:
                    return ('error: Invalid Google Chrome Extension Directory')

            elif browser == 'brave' and os.path.isdir(path):
                if os.path.isfile(os.path.join(path, 'manifest.json')):
                    analysis_stat = analysis.analyze(
                        path, 'Local Brave browser Extension')
                    return (analysis_stat)
                else:
                    return ('error: Invalid Brave Extension Directory')

            elif browser == 'vivaldi' and os.path.isdir(path):
                if os.path.isfile(os.path.join(path, 'manifest.json')):
                    analysis_stat = analysis.analyze(
                        path, 'Local Vivaldi brwoser Extension')
                    return analysis_stat
                else:
                    return 'error: Invalid Vivaldi Extension Directory'

            else:
                return ('error: Malformed Query')
        except Exception:
            logging.error(traceback.format_exc())
            return ('error: Incomplete Query')

    elif query == 'deleteAll':
        '''
        DELETES ALL RESULTS
        RESPONSE = SUCCESS / ERROR
        '''
        import core.result as result
        delete_status = result.clearAllResults()
        if delete_status:
            return "success"
        else:
            return ('There were some errors while deleting all analysis reports... refer to log for more information')

    elif query == 'clearLab':
        '''
        Deletes all the contents of lab
        RESPONSE = SUCCESS / ERROR
        '''
        clear_lab = core.clear_lab()
        if clear_lab[0]:
            # Successful
            return (clear_lab[1])
        else:
            # Unsuccessful
            return ('error: ' + clear_lab[1])

    elif query == 'deleteResult':
        '''
        DELETES A SPECIFIC RESULT
        PARAMETER = resultID
        RESPONSE = SUCCESS_MSG / 'error: ERROR_MSG'
        '''
        try:
            result_id_to_delete = allargs.get('resultID')
            import core.result as result
            delete_status = result.clearResult(result_id_to_delete)
            if delete_status:
                return "success"
            else:
                return "Something went wrong while deleting result! Check log for more information"
        except Exception:
            return ('Invalid Query')

    elif query == 'vtDomainReport':
        try:
            domain = allargs.get('domain')
            analysis_id = allargs.get('analysis_id')
            ranalysis = core.get_result_info(analysis_id)
            if ranalysis[0]:
                # if ranalysis[0] is True then ranalysis[1] contains the details
                analysis_dir = ranalysis[1]['report_directory']
                analysis_report = os.path.join(
                    analysis_dir, 'extanalysis_report.json')
                if os.path.isfile(analysis_report):
                    report = open(analysis_report, 'r')
                    domains = json.loads(report.read())['domains']
                    for adomain in domains:
                        if adomain['name'] == domain:
                            vtjson = json.dumps(
                                adomain['virustotal'], indent=4, sort_keys=False)
                            # return_html = '<div id="vt_info"></div><script>var wrapper1 = document.getElementById("vt_info");var data = '+vtjson+' try {var data = JSON.parse(dataStr);} catch (e) {} var tree = jsonTree.create(data, wrapper1);tree.expand(function(node) {   return node.childNodes.length < 2 || node.label === "phoneNumbers";});</script>'
                            return vtjson
                    return ('error: Domain info not found in analysis report!')
                else:
                    return ('error: Analysis report for #{0} not found'.format(analysis_id))
            else:
                # ranalysis[1] is the error msg when ranalysis[0] = False
                return ('error: ' + ranalysis[1])
        except:
            logging.error(traceback.format_exc())
            return ('error: Malformed api call')

    elif query == 'retirejsResult':
        '''
        GET RETIREJS SCAN RESULTS FOR FILE
        REQUIRED PARAMETER: file = FILE_ID
        '''
        try:
            file_id = allargs.get('file')
            analysis_id = allargs.get('analysis_id')
            ranalysis = core.get_result_info(analysis_id)
            if ranalysis[0]:
                # if ranalysis[0] is True then ranalysis[1] contains the details
                analysis_dir = ranalysis[1]['report_directory']
                source_json = os.path.join(analysis_dir, 'source.json')
                if os.path.isfile(source_json):
                    report = open(source_json, 'r')
                    files = json.loads(report.read())
                    for _file in files:
                        if _file == file_id:
                            retirejs_result = files[_file]['retirejs_result']
                            if retirejs_result == []:
                                ret = 'none'
                            else:
                                ret = json.dumps(
                                    retirejs_result, indent=4, sort_keys=False)
                            return ret
                    return ('error: File ID not found in report!')
                else:
                    return ('error: Analysis report for #{0} not found'.format(analysis_id))
            else:
                # ranalysis[1] is the error msg when ranalysis[0] = False
                return ('error: ' + ranalysis[1])
        except:
            logging.error(traceback.format_exc())
            return ('error: Malformed api call')

    elif query == 'whois':
        '''
        GET WHOIS REPORT OF DOMAIN
        REQUIRES 'python-whois' module
        RESPONSE = HTML DIV WITH FORMATTED WHOIS INFO
        '''
        try:
            domain = allargs.get('domain')
            try:
                import whois
            except:
                return (
                    "error: python-whois module not installed! install it using `pip3 install python-whois` or `pip3 install -r requirements.txt`")
            whois_result = whois.whois(domain)
            whois_html = '<div class="whois-data" style="overflow-y: scroll; max-height:500px; text-align: left;">'
            for data in whois_result:
                proper_data = data.replace('_', ' ').capitalize()
                if isinstance(whois_result[data], list):
                    for subdata in whois_result[data]:
                        whois_html += '<b style="color:#89ff00;">{0} : </b>{1}<br>'.format(
                            proper_data, subdata)
                else:
                    whois_html += '<b style="color:#89ff00;">{0} : </b>{1}<br>'.format(
                        proper_data, whois_result[data])
            whois_html += '</div>'
            if whois_result:
                return ('<center><h4>Whois Results For {0}</h4></center><br>{1}'.format(domain, whois_html))
            else:
                return ("error: Something went wrong while checking whois information of: " + domain)
        except Exception:
            logging.error(traceback.format_exc())
            return ('error: Invalid Query')

    elif query == 'geoip':
        '''
        GEO-IP LOOKUP OF AN IP ADDRESS
        PARAMETERS -> IP = CONTAINS IP ADDRESS TO BE LOOKED UP
        RETURNS A HTML TO BE SHOWN
        '''
        try:
            ip_address = allargs.get('ip')
            geo_ip = scan.geoip(ip_address)
            if geo_ip[0]:
                gip = geo_ip[1]
                rethtml = '<div class="whois-data" style="overflow-y: scroll; max-height:500px; text-align: left;">'
                for g in gip:
                    name = str(g).replace('_', ' ').capitalize()
                    val = str(gip[g])
                    rethtml += '<b style="color:#89ff00;">{0} : </b>{1}<br>'.format(
                        name, val)
                rethtml += '</div>'
                return ('<center><h4>Geo-IP Lookup Results For {0}</h4></center><br>{1}'.format(ip_address, rethtml))

            else:
                # in case of geo_ip[0] being false element 1 has the error msg
                return ('error: ' + geo_ip[1])

        except Exception as e:
            logging.error(traceback.format_exc())
            return ('error: Invalid Query')

    elif query == 'HTTPHeaders':
        '''
        HTTP HEADERS OF AN URL
        PARAMETERS -> URL -> BASE64 ENCODED URL
        RETURNS HTML
        '''
        try:
            url = allargs.get('url')
            url = base64.b64decode(url).decode('ascii')
            headers_status = scan.http_headers(url)
            if headers_status[0]:
                rethtml = '<div class="whois-data" style="overflow-y: scroll; max-height:500px; text-align: left;">'
                headers = headers_status[1]
                for header in headers:
                    hval = headers[header]
                    rethtml += '<b style="color:#89ff00;">{0} : </b>{1}<br>'.format(
                        header, hval)
                rethtml += '</div>'
                return ('<center><h4>Showing HTTP Headers of: {0}</h4></center><br>{1}'.format(url, rethtml))
            else:
                return ('error: ' + headers_status[1])
        except Exception as e:
            logging.error(traceback.format_exc())
            return ('error: Invalid Query')

    elif query == 'SourceCode':
        '''
        GET SOURCE CODE OF AN URL
        PARAMETERS -> URL -> BASE64 ENCODED URL
        RETURNS HTML
        '''
        try:
            url = allargs.get('url')
            rurl = base64.b64decode(url).decode('ascii')
            headers_status = scan.source_code(rurl)
            if headers_status[0]:
                rethtml = '<textarea id="src_code" class="source_code" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false">'
                headers = headers_status[1]
                rethtml += headers
                rethtml += '</textarea><br><br><center><a href="{0}" target="_blank" class="start_scan"><i class="fas fa-external-link-alt"></i> View Full Screen</a>'.format(
                    '/source-code/' + url)
                return ('<center><h4>Source Code of: {0}</h4></center><br>{1}'.format(rurl, rethtml))
            else:
                return ('error: ' + headers_status[1])
        except Exception as e:
            logging.error(traceback.format_exc())
            return ('error: Invalid Query')

    elif query == 'clearlogs':
        '''
        CLEARS LOG
        '''
        core.clearlog()
        return ('Logs cleared successfully!')

    elif query == 'changeReportsDir':
        '''
        CHANGES THE REPORT DIRECTORY
        RESPONSE = SUCCESS / 'error: ERROR_MSG'
        '''
        try:
            newpath = allargs.get('newpath')
            if os.path.isdir(newpath):
                # valid directory.. let's get the absolute path and set it
                absolute_path = os.path.abspath(newpath)
                import core.settings as settings
                change = settings.changedir(absolute_path)
                if change[0]:
                    return (change[1])
                else:
                    return ('error: ' + change[1])
            else:
                return ('error: Invalid directory path!')
        except:
            logging.error(traceback.format_exc())
            return ('error: Invalid request for directory change!')

    elif query == 'changeVTapi':
        '''
        CHANGE VIRUSTOTAL API
        RESPONSE = SUCCESS_MSG / 'error: ERROR_MSG'
        '''
        try:
            new_api = allargs.get('api')
            import core.settings as settings
            change = settings.change_vt_api(new_api)
            if change[0]:
                return (change[1])
            else:
                return ('error: ' + change[1])
        except:
            logging.error(traceback.format_exc())
            return ('error: Invalid request!')

    elif query == 'changelabDir':
        '''
        CHANGES THE LAB DIRECTORY
        RESPONSE = SUCCESS / 'error : ERROR_MSG'
        '''
        try:
            newpath = allargs.get('newpath')
            if os.path.isdir(newpath):
                # valid directory.. let's get the absolute path and set it
                absolute_path = os.path.abspath(newpath)
                import core.settings as settings
                change = settings.changelabdir(absolute_path)
                if change[0]:
                    return (change[1])
                else:
                    return ('error: ' + change[1])
            else:
                return ('error: Invalid directory path!')
        except:
            logging.error(traceback.format_exc())
            return ('error: Invalid request for directory change!')

    elif query == 'updateIntelExtraction':
        '''
        UPDATES INTELS TO BE EXTRACTED
        RESPONSE = SUCCESS_MSG / 'error: ' + ERROR_MSG
        '''
        try:
            # Create the dict with all values and keys
            parameters = {}
            parameters["extract_comments"] = str(
                allargs.get('extract_comments'))
            parameters["extract_btc_addresses"] = str(
                allargs.get('extract_btc_addresses'))
            parameters["extract_base64_strings"] = str(
                allargs.get('extract_base64_strings'))
            parameters["extract_email_addresses"] = str(
                allargs.get('extract_email_addresses'))
            parameters["extract_ipv4_addresses"] = str(
                allargs.get('extract_ipv4_addresses'))
            parameters["extract_ipv6_addresses"] = str(
                allargs.get('extract_ipv6_addresses'))
            parameters["ignore_css"] = str(allargs.get('ignore_css'))

            import core.settings as settings
            status_code = settings.update_settings_batch(parameters)
            # 0 = failed, 1 = success, 2 = some updated some not!
            if status_code == '0':
                return ('error: Settings could not be updated! Check log for more information')
            elif status_code == '1':
                return ('Settings updated successfully... Please restart ExtAnalysis for them to take effect!')
            elif status_code == '2':
                return (
                    'Some settings were updated and some were not... Please restart ExtAnalysis for them to take effect!')
            else:
                return (
                    'error: Invalid response from "update_settings_batch". please report it here: https://github.com/Tuhinshubhra/ExtAnalysis/issues/new')
        except:
            logging.error(traceback.format_exc())
            return ('error: Incomplete Request!')

    else:
        return ('error: Invalid Query!')
