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
import os
import zipfile
import tarfile
import re
import core.core as core
import json
from pathlib import Path
import traceback
import logging
import shutil
import core.result as saveresult
import core.helper as helper
import socket
import core.virustotal as virustotal
import core.intel as intel
import core.ip2country as ip2country


def sort_files(extension_dir):
    try:
        extract_dir = helper.fixpath(core.lab_path + '/' + extension_dir)
        html_files = []
        js_files = []
        css_files = []
        static_files = []
        other_files = []  # File extensions that are not listed above
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                filepath = os.path.join(root, file)
                file = file.lower()
                if file.endswith('.html'):
                    core.updatelog('Discovered html file: ' + file)
                    html_files.append(filepath)
                elif file.endswith('.js'):
                    core.updatelog('Discovered js file: ' + file)
                    js_files.append(filepath)
                elif file.endswith('.css'):
                    core.updatelog('Discovered css file: ' + file)
                    css_files.append(filepath)
                elif file.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.svg')):
                    core.updatelog('Discovered static file: ' + file)
                    static_files.append(filepath)
                else:
                    other_files.append(filepath)
        core.updatelog('Sorted files: ' + extension_dir)
        # core.updatelog('HTML Files: {0}, JS Files: {1}, CSS Files: {2}, Static Files: {3}, Other Files: {4}'.format(str(count(html_files)), str(count(js_files)), str(count(css_files)), str(count(static_files)), str(count(other_files)))
        r = {'html_files': html_files, 'js_files': js_files, 'css_files': css_files,
             'static_files': static_files, 'other_files': other_files}
        return r
    except Exception as e:
        core.updatelog('Error while sorting files: ' + str(e))
        return False


def analyze(ext_name, ext_type='local'):
    # Handle the /detail/ format
    core.updatelog(ext_name)
    file_name = None
    if '?' in ext_name:
        # Split the path and get the last segment before any query parameters
        # This handles cases like /detail/histre/cmhjbooiibolkopmdohhnhlnkjikhkmn?hl=en-US
        file_name = ext_name.split('?')[0]

    # extension_extracted = False
    if ext_name.endswith('.crx') or ext_name.endswith('.xpi') or ext_name.endswith('.zip') or ext_name.endswith('.tar') or ext_name.endswith('.gzip'):
        '''
        EXTENSION NAME / PACKED PATH 
        UNZIP THE EXTENSION FOR FURTHER ANALYSIS
        '''

        if ext_name.endswith('.crx'):
            file_extension = '.crx'
            extract_method = 'zip'
        elif ext_name.endswith('.xpi'):
            file_extension = '.xpi'
            extract_method = 'zip'
        elif ext_name.endswith('.zip'):
            file_extension = '.zip'
            extract_method = 'zip'
        elif ext_name.endswith('.tar'):
            file_extension = '.tar'
            extract_method = 'tar'
        elif ext_name.endswith('.gzip'):
            file_extension = '.gzip'
            extract_method = 'tar'
        else:
            file_extension = ''
        ext_name = file_name + file_extension if file_name is not None else ext_name
        if os.path.isfile(ext_name):
            '''
            Full extension path sent, we unzip it to the lab directroy
            Used mostly to pass local firefox extensions
            '''
            ext_path = ext_name
            ext_name = os.path.basename(ext_name).split(file_extension)[0]
            extract_dir = helper.fixpath(core.lab_path + '/' + ext_name)
        else:
            '''
            Only the extension name is sent.. 
            In this case we assume that the extension is located inside the lab directory.
            Used while scanning an uploaded or downloaded extension
            '''
            ext_path = helper.fixpath(core.lab_path + '/' + ext_name)
            extract_dir = helper.fixpath(
                core.lab_path + '/' + ext_name.split(file_extension)[0])

        core.updatelog('Trying to unzip {0} to {1}'.format(
            ext_path, extract_dir))
        try:
            if os.path.exists(extract_dir):

                if os.path.exists(extract_dir + '_old'):
                    # there is already a _old directory we have to delete so that we can rename the last directory to this name
                    core.updatelog(
                        'Found previously created _old directory... deleting that')
                    try:
                        shutil.rmtree(extract_dir + '_old')
                    except Exception as e:
                        core.updatelog('Error while deleting: {0} . Error: {1}'.format(
                            extract_dir + '_old', str(e)))
                        logging.error(traceback.format_exc())
                        return ('error: Something went wrong while deleting old scan directory {0}'.format(extract_dir + '_old'))

                new_name = os.path.basename(extract_dir) + '_old'
                core.updatelog('Renaming old extract directory {0} as {1}'.format(
                    extract_dir, new_name))
                os.rename(extract_dir, extract_dir + '_old')
                core.updatelog('Old directory successfully renamed')

            if extract_method == 'zip':
                # zip, xpi, crx file extraction
                zip_contents = zipfile.ZipFile(ext_path, 'r')
                zip_contents.extractall(extract_dir)
                zip_contents.close()
                core.updatelog('Zip Extracted Successfully')
            elif extract_method == 'tar':
                # tar, gzip file extraction
                tar_contents = tarfile.open(ext_path)
                tar_contents.extractall(extract_dir)
                tar_contents.close()
                core.updatelog('Tar Extracted Successfully')

            # extension_extracted = True
        except Exception as e:
            logging.error(traceback.format_exc())
            core.updatelog(
                'Something went wrong while unzipping extension\nError: ' + str(e))
            return ('error: Something went wrong while unzipping extension. Check log for more information')

    elif os.path.isdir(ext_name):
        # if ext_name is a directory most likely it's a local extension
        ext_path = 'Local'
        extract_dir = ext_name
    else:
        return ('error: [analyze.py] Unsupported input!')

    core.updatelog('======== Analysis Begins ========')
    try:
        core.updatelog('Reading manifest.json')
        manifest_file = helper.fixpath(extract_dir + '/manifest.json')
        manifest_load = open(manifest_file, 'r')
        manifest_content = manifest_load.read()
        manifest_content = json.loads(manifest_content)
        rinit = core.initreport(manifest_content, extract_dir, ext_type)
        if not rinit:
            return ('error: Something went wrong while parsing manifest.json... analysis stopped')
        core.report['crx'] = ext_path
        core.report['extracted'] = extract_dir

        #####################################################################
        ##### PERMISSION CHECKS AND OTHER STUFFS RELATED TO PERMISSIONS #####
        #####################################################################
        perm_file = helper.fixpath(core.path + '/db/permissions.json')
        perms = open(perm_file, 'r')
        perms = perms.read()
        perms = json.loads(perms)
        try:
            for permission in manifest_content['permissions']:
                if permission != "":
                    permarray = {'name': permission}
                    core.updatelog('Discoverd Permission: ' +
                                   helper.escape(permission))
                    if permission in perms:
                        permarray['description'] = perms[permission]['description']
                        permarray['badge'] = perms[permission]['badge']
                        permarray['risk'] = perms[permission]['risk']
                        if perms[permission]['warning'] != 'none':
                            permarray['warning'] = perms[permission]['warning']
                            # core.updatelog('Warning: ' + perms[permission]['warning'])
                        else:
                            permarray['warning'] = 'na'
                    else:
                        permarray['description'] = 'na'
                        permarray['warning'] = 'na'
                        permarray['risk'] = 'none'
                        permarray['badge'] = '<i class="fas fa-question"></i>'
                    core.insertpermission(permarray)
        except Exception as e:
            core.updatelog('No permissions found')
            core.updatelog(str(e))

        #####################################################################
        #####     GET ALL FIELS AND STORE THEM FOR FURTHER ANALYSIS      ####
        #####################################################################
        html_files = []
        js_files = []
        json_files = []
        css_files = []
        static_files = []
        other_files = []  # File extensions that are not listed above

        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                filepath = os.path.join(root, file)
                relpath = os.path.relpath(filepath, extract_dir)
                fname = file
                file = file.lower()
                if file.endswith(('.html', '.htm')):
                    html_files.append(filepath)
                    core.report['files']['html'].append({fname: relpath})
                elif file.endswith('.js'):
                    js_files.append(filepath)
                    core.report['files']['js'].append({fname: relpath})
                elif file.endswith('.json'):
                    json_files.append(filepath)
                    core.report['files']['json'].append({fname: relpath})
                elif file.endswith('.css'):
                    css_files.append(filepath)
                    core.report['files']['css'].append({fname: relpath})
                elif file.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.svg', '.gif')):
                    core.report['files']['static'].append({fname: relpath})
                    static_files.append(filepath)
                else:
                    core.report['files']['other'].append({fname: relpath})
                    other_files.append(filepath)

        ######################################################################
        ## EXTRACT INTELS FROM  FILES (url, email, ip address, btc address) ##
        ######################################################################

        urls = []
        domains = []
        for allfiles in (js_files, html_files, json_files, css_files):
            for file in allfiles:
                try:
                    cnt = open(file, 'r', encoding="utf8")
                    contents = cnt.read()
                    relpath = os.path.relpath(file, extract_dir)
                    core.updatelog('Extracting intels from: ' + file)
                    intels = intel.extract(contents, relpath)

                    # Parse the intels and add them to result
                    found_urls = intels['urls']
                    found_mail = intels['mails']
                    found_btcs = intels['btc']
                    found_ipv4 = intels['ipv4']
                    found_ipv6 = intels['ipv6']
                    found_b64s = intels['base64']
                    found_cmnt = intels['comments']

                    for u in found_urls:
                        urls.append(u)
                    for m in found_mail:
                        core.report['emails'].append(m)
                    for b in found_btcs:
                        core.report['bitcoin_addresses'].append(b)
                    for i in found_ipv4:
                        core.report['ipv4_addresses'].append(i)
                    for i in found_ipv6:
                        core.report['ipv6_addresses'].append(i)
                    for b in found_b64s:
                        core.report['base64_strings'].append(b)
                    for c in found_cmnt:
                        core.report['comments'].append(c)

                except Exception as e:
                    core.updatelog(
                        'Skipped reading file: {0} -- Error: {1}'.format(file, str(e)))
                    logging.error(traceback.format_exc())
        # urls = list(set(urls)) [NOTE TO SELF] we are tracking all urls in all files so set isn't used here

        ######################################################################
        ## APPEND URLS, DOMAINS TO REPORT AND DO VIRUSTOTAL SCAN ON DOMAINS ##
        ######################################################################

        for url in urls:
            core.updatelog('Found URL: ' + url['url'])
            domain = re.findall(
                '^(?:https?:\/\/)?(?:[^@\/\\n]+@)?(?:www\.)?([^:\/?\\n]+)', url['url'])[0]
            url['domain'] = domain
            core.report['urls'].append(url)  # add url to the report file
            domains.append(domain)

        if virustotal.pub_vt == []:
            # No extra virustotal apis added hence the slow scan
            core.updatelog(
                'Starting virustotal analysis of domains. [SLOW MODE]')
            virustotal_scans = virustotal.domain_batch_scan(set(domains))

        for domain in set(domains):
            core.updatelog(
                'getting virustotal Scan results for domain: ' + domain)
            if virustotal.pub_vt != []:
                # the faster scan!
                virustotal_report = virustotal.scan_domain(domain)
                if not virustotal_report[0]:
                    core.updatelog(
                        'Error getting virustotal result... Error: ' + virustotal_report[1])
                    domain_vt = {
                        "error": "Either rate limited or something else went wrong while getting domain report from virustotal"}
                else:
                    core.updatelog('Virustotal result successfully acquired!')
                    domain_vt = virustotal_report[1]
            else:
                domain_vt = virustotal_scans[domain][1]
                core.updatelog('Virustotal result successfully acquired!')
            try:
                ip = socket.gethostbyname(domain)
            except:
                ip = 'unknown'
            if ip != 'unknown':
                ip_info = ip2country.get_country(ip)
                if ip_info[0]:
                    country = ip_info[2]
                    country_code = ip_info[1]
                else:
                    country = 'unknown'
                    country_code = 'unknown'
            else:
                country = 'unknown'
                country_code = 'unknown'

            domainarr = {"name": domain, "ip": ip, "country_code": country_code,
                         "country": country, "virustotal": domain_vt}
            core.report['domains'].append(domainarr)

        save_result = saveresult.createresult(extract_dir)
        cid = save_result.savereport()
        """
        if extension_extracted:
            # if the extension was extracted we delete the directory it was extracted to
            # don't want any local extensions to be deleted hence extension_extracted boolean
            core.updatelog('Deleting extraction directory: ' + extract_dir)
            try:
                shutil.rmtree(extract_dir)
                core.updatelog('Extraction directory successfully deleted')
            except Exception as e:
                core.updatelog('Something went wrong while deleting extraction directory: ' + str(e))
                logging.error(traceback.format_exc())
        """
        if cid != False and cid != None:
            return ('Extension analyzed and report saved under ID: ' + cid)
        else:
            return ('error:Something went wrong with the analysis!')
    except Exception as e:
        core.updatelog(
            'Something went wrong while reading source of manifest.json file')
        print(e)
        core.updatelog(logging.error(traceback.format_exc()))


"""
def handle_delete(func, path, exc_info):
    os.chmod(path, stat.S_IWRITE)
    os.unlink(path)
"""