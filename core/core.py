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
import time
import traceback
import logging
import json
import zipfile
import re
import shutil
import signal
import core.helper as helper

## all the paths
path = os.path.dirname(os.path.abspath(__file__)).replace('/core','').replace('\core','')
lab_path = helper.fixpath(path + '/lab')
reports_path = helper.fixpath(path + '/reports')

# Version
with open(os.path.join(path, 'current_version')) as vf:
    version = vf.read()

# All the variables
quiet = False
log = ""
raw_log = "\n\n\n"
report = {} #'{"name":"","version":"","author":"","permissions":[{"name":"","description":"","warning":""}],"urls":"","files":{"html":"","js":"","css":"","static":"","other":""},"content-scripts":[],"background-scripts":[],"pageaction-popup":[],"browseraction-popup":[]}'
reportids = {}
virustotal_api = ''
ignore_css = True
github_repo = 'https://github.com/Tuhinshubhra/ExtAnalysis'
github_zip = 'https://github.com/Tuhinshubhra/ExtAnalysis/archive/master.zip'
version_url = 'https://raw.githubusercontent.com/Tuhinshubhra/ExtAnalysis/master/current_version'

# settings for intel extraction! DO NOT EDIT HERE! use the settings.json instead
extract_comments = True
extract_btc_addresses = True
extract_base64_strings = True
extract_email_addresses = True
extract_ipv4_addresses = True
extract_ipv6_addresses = True

report_index = os.path.join(path, 'reports.json')
settings_file = helper.fixpath(path + '/settings.json')
log_file = helper.fixpath(path + '/extanalysis.log')


def print_logo():
    logo = '''
     _____     _   _____         _         _
    |   __|_ _| |_|  _  |___ ___| |_ _ ___|_|___
    |   __|_'_|  _|     |   | .'| | | |_ -| |_ -|
    |_____|_,_|_| |__|__|_|_|__,|_|_  |___|_|___|
    => Browser Extension Analysis |___| Framework
    => Version {0} By r3dhax0r

    '''.format(version)
    print(logo)

def updatelog(clog, type='info'):
    '''
    Logger
    TODO: it was already too late before i thought of type hence this shitty hack
    will fix it later
    '''
    global raw_log, log, quiet
    clog = str(clog)
    if any (val in clog.lower() for val in ['success', 'done', 'finished', "complete", 'found']):
        raw_log += '[SUC - {0}]  {1} \n'.format(time.strftime('%d-%b-%y %H:%M:%S', time.gmtime()), clog)
        if not quiet:
            msg = '[+] ' + clog
            print(msg)
    elif any (val in clog.lower() for val in ['error', 'wrong', 'not', "n't"]):
        raw_log += '[ERR - {0}]  {1} \n'.format(time.strftime('%d-%b-%y %H:%M:%S', time.gmtime()), clog)
        if not quiet:
            msg = '[!] ' + clog
            print(msg)
    else:
        raw_log += '[INF - {0}]  {1} \n'.format(time.strftime('%d-%b-%y %H:%M:%S', time.gmtime()), clog)
        if not quiet:
            msg = '[i] ' + clog
            print(msg)

    log += '<br>[' + time.strftime("%H:%M:%S", time.gmtime()) + '] ' + clog

def clearlog():
    global log
    log = ""

def initreport(manifestjson, ext_dir, ext_type='local'):
    global report, reportids, path, report_index
    try:
        ridfile = report_index
        ridcnt = open(ridfile, 'r')
        ridcnt = ridcnt.read()
        reportids = json.loads(ridcnt)
        ext_manifest = os.path.join(ext_dir, 'manifest.json')
        try:
            report['name'] = manifestjson['name']
            # check if name is defined in locale
            if '__MSG_' in manifestjson['name']:
                updatelog('Getting extension name from _locales')
                #locale_dir = helper.fixpath(ext_dir + '/_locales/')
                ext_name = GetNameFromManifest(ext_manifest)
                if ext_name != False and ext_name != "" and ext_name != None:
                    report['name'] = ext_name
            report['crx'] = ""
            report['extracted'] = ''
            report['type'] = ext_type
            report['manifest'] = manifestjson
            report['version'] = manifestjson['version']
            report['permissions'] = []
            report['urls'] = []
            report['emails'] = []
            report['bitcoin_addresses'] = []
            report['ipv4_addresses'] = []
            report['ipv6_addresses'] = []
            report['base64_strings'] = []
            report['comments'] = []
            report['domains'] = []
            report['files'] = {'html':[], 'json':[], 'js':[], 'css':[], 'static':[], 'other':[]}
            try:
                # non Required values
                report['author'] = manifestjson['author']
            except:
                report['author'] = 'unknown'
                updatelog('No author name found')
            try:
                report['description'] = manifestjson['description']
                if '__MSG_' in report['description']:
                    updatelog('Getting Extension Description from locale')
                    app_desc = GetDescriptionFromManifest(ext_manifest)
                    if app_desc != False and app_desc != None and app_desc != "":
                        report['description'] = app_desc
                    else:
                        updatelog('Could not get extension description from locale')
            except:
                report['description'] = 'unknown'
                updatelog('No author name found')
            return True
        except Exception as e:
            updatelog('Error while parsing manifest.json, Error: ' + str(e))
            logging.error(traceback.format_exc())
            #print(manifestjson)
            return False
    except Exception as e:
        logging.error(traceback.format_exc())
        updatelog('Something went wrong while getting report ids. Error: ' + str(e))
        return False

def insertpermission(permarray):
    if all(val in permarray for val in ['name', 'description', 'warning', 'badge', 'risk']):
        global report
        report['permissions'].append(permarray)
    else:
        updatelog('Skipped adding permission "MISSING KEY". Perm: ' + str(permarray))

def extract_urls(file_path):
    updatelog('Extracting URLs From: ' + file_path)
    urls = []
    try:
        cnt = open(helper.fixpath(file_path), 'r', encoding='utf8')
        contents = cnt.read()
        curls = re.findall('(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?', contents)
        for url in curls:
            urls.append(url[0]+'://'+url[1]+url[2])
            updatelog('Found url: ' + url[0]+'://'+url[1]+url[2])
        urls = list(set(urls))
        return(urls)
    except Exception as e:
        updatelog('error: Something went wrong while reading file')
        updatelog('ERROR: ' + str(e))
        logging.error(traceback.format_exc())
        return []


def GetNameFromManifest(manifest_file):
    # Get's the name of an extension from manifest file
    if os.path.isfile(manifest_file):
        # Path is valid and it's a manifest file
        extension_path = helper.fixpath(manifest_file.replace('manifest.json', ''))
        manifest_content = open(manifest_file, 'r')
        manifest_content = manifest_content.read()

        try:
            # load the json data
            manifest_json = json.loads(manifest_content)

            try:
                manifest_name = manifest_json['name']
                if '__MSG_' in manifest_name:
                    # This is the whole reason i created this function...
                    updatelog('Getting manifest name from locale file: ' + extension_path)
                    manifest_message = re.findall('__MSG_(.*?)__', manifest_name)[0]
                    locale_dir = helper.fixpath(extension_path + '/_locales/')
                    if os.path.isdir(locale_dir):
                        # locale directory exists let' s grab our thing
                        try:
                            # get the default locale from manifest
                            default_locale = manifest_json['default_locale']
                            en_locale_file = helper.fixpath(locale_dir + '/' + default_locale + '/messages.json')
                            updatelog('Default Locale: ' + default_locale)
                        except Exception as e:
                            # use hardcoded en
                            en_locale_file = helper.fixpath(locale_dir + '/en/messages.json')
                        if os.path.isfile(en_locale_file):
                            # en locale file found let's grab the name
                            en_locale_content = open(en_locale_file, 'r')
                            try:
                                en_locale_content = json.loads(en_locale_content.read())
                                string_content = str(en_locale_content)
                                ext_name = ''
                                if manifest_message in string_content:
                                    ext_name = en_locale_content[manifest_message]['message']
                                    updatelog('Extension name grabbed from en locale file.. Name: ' + ext_name)
                                    return ext_name
                                else:
                                    updatelog('Could not find name')
                                    return False

                            except Exception as e:
                                updatelog('Something went wrong while reading or parsing en locale file...')
                                logging.error(traceback.format_exc())
                                return False
                        else:
                            # en locale not found let's just get the first one we find and be done with it
                            ldirs = os.listdir(locale_dir)
                            for dir in ldirs:
                                if os.path.isfile(helper.fixpath(locale_dir + '/' + dir + '/messages.json')):
                                    locale_content = open(helper.fixpath(locale_dir + '/' + dir + '/messages.json'), 'r')
                                    try:
                                        en_locale_content = json.loads(locale_content.read())
                                        if manifest_message in locale_content:
                                            ext_name = en_locale_content[manifest_message]['message']
                                            updatelog('Extension name grabbed from en locale file.. Name: ' + ext_name)
                                            return ext_name
                                        else:
                                            updatelog('Could not find name')
                                            return False

                                    except Exception as e:
                                        updatelog('Something went wrong while reading or parsing en locale file...')
                                        logging.error(traceback.format_exc())
                                        return False
                    else:
                        # _locale dir doesn't exist let's just go...
                        updatelog('_locale directory doesn\'t exist.. dir: ' + locale_dir)
                        return False
                else:
                    return manifest_name
            except Exception as e:
                updatelog('No name in on manifest.json ... maybe an invalid extension?')
                logging.error(traceback.format_exc())
                return False
        except Exception as e:
            updatelog('Something went wrong while loading manifest json [GetNameFromManifest]')
            updatelog('Error: ' + str(e))
            logging.error(traceback.format_exc())
            return False

def GetDescriptionFromManifest(manifest_file):
    # Get's the desc of an extension from manifest file
    if os.path.isfile(manifest_file):
        # Path is valid and it's a manifest file
        extension_path = helper.fixpath(manifest_file.replace('manifest.json', ''))
        manifest_content = open(manifest_file, 'r', encoding="utf8")
        manifest_content = manifest_content.read()

        try:
            # load the json data
            manifest_json = json.loads(manifest_content)

            try:
                manifest_desc = manifest_json['description']
                if '__MSG_' in manifest_desc:
                    # This is the whole reason i created this function...
                    updatelog('Getting manifest description from locale file: ' + extension_path)
                    manifest_message = re.findall('__MSG_(.*?)__', manifest_desc)[0]
                    locale_dir = helper.fixpath(extension_path + '/_locales/')
                    if os.path.isdir(locale_dir):
                        # locale directory exists let' s grab our thing
                        try:
                            # get the default locale from manifest
                            default_locale = manifest_json['default_locale']
                            en_locale_file = helper.fixpath(locale_dir + '/' + default_locale + '/messages.json')
                            updatelog('Default Locale: ' + default_locale)
                        except Exception as e:
                            # use hardcoded en
                            en_locale_file = helper.fixpath(locale_dir + '/en/messages.json')
                        if os.path.isfile(en_locale_file):
                            # en locale file found let's grab the desc
                            en_locale_content = open(en_locale_file, 'r', encoding="utf8")
                            try:
                                en_locale_content = json.loads(en_locale_content.read())
                                string_content = str(en_locale_content)
                                ext_desc = ''
                                if manifest_message in string_content:
                                    ext_desc = en_locale_content[manifest_message]['message']
                                    updatelog('Extension description grabbed from default locale file.. description: ' + ext_desc)
                                    return ext_desc
                                else:
                                    updatelog('Could not find description')
                                    return False

                            except Exception as e:
                                updatelog('Something went wrong while reading or parsing default locale file...')
                                logging.error(traceback.format_exc())
                                return False
                        else:
                            # en locale not found let's just get the first one we find and be done with it
                            ldirs = os.listdir(locale_dir)
                            for dir in ldirs:
                                if os.path.isfile(helper.fixpath(locale_dir + '/' + dir + '/messages.json')):
                                    locale_content = open(helper.fixpath(locale_dir + '/' + dir + '/messages.json'), 'r', encoding="utf8")
                                    try:
                                        en_locale_content = json.loads(locale_content.read())
                                        if manifest_message in locale_content:
                                            ext_desc = en_locale_content[manifest_message]['message']
                                            updatelog('Extension description grabbed from ' + dir + ' locale file.. description: ' + ext_desc)
                                            return ext_desc
                                        else:
                                            updatelog('Could not find description')
                                            return False

                                    except Exception as e:
                                        updatelog('Something went wrong while reading or parsing en locale file...')
                                        logging.error(traceback.format_exc())
                                        return False
                    else:
                        # _locale dir doesn't exist let's just go...
                        updatelog('_locale directory doesn\'t exist.. dir: ' + locale_dir)
                        return False
                else:
                    return manifest_desc
            except Exception as e:
                updatelog('No description in on manifest.json ... maybe an invalid extension?')
                logging.error(traceback.format_exc())
                return False
        except Exception as e:
            updatelog('Something went wrong while loading manifest json [GetDescriptionFromManifest]')
            updatelog('Error: ' + str(e))
            logging.error(traceback.format_exc())
            return False

def get_result_info(analysis_id):
    '''
    GET INFO ABOUT A SPECIFIC ANALYSIS INFO
    RESPONSE = [TRUE/FALSE, JSON_LOADED_RESULT/ERROR_MSG]
    '''
    global reportids, report_index, reports_path
    if reportids == {}:
        # index not loaded.. let's load it up
        indexs = open(report_index, 'r')
        indexs = json.loads(indexs.read())
        reportids = indexs

    reports = reportids['reports']
    if analysis_id in str(reports):
        for report in reports:
            if report['id'] == analysis_id:
                report['report_directory'] = helper.fixpath(report['report_directory'].replace('<reports_path>', reports_path).replace('\\', '/'))
                return [True, report]
        return [False, 'Analysis ID mismatch: {0}'.format(analysis_id)]
    else:
        return [False, 'Analysis ID {0} not found in result index!'.format(analysis_id) ]


def clear_lab():
    '''
    Deletes all the contents of lab
    Response = [True/False, Success_msg/err_msg]
    '''
    global lab_path
    if os.path.isdir(lab_path):
        updatelog('Lab directory found... deleting it!')
        try:
            shutil.rmtree(lab_path)
            updatelog('lab directory deleted successfully! Creating new directory...')
            try:
                os.mkdir(lab_path)
                updatelog('New lab directory created!')
                return [True, 'Lab successfully cleared!']
            except Exception as e:
                err_msg = 'Error: {0} encountered while creating empty lab directory!'.format(str(e))
                updatelog(err_msg)
                logging.error(traceback.format_exc())
                return[False, err_msg]
        except Exception as e:
            err_msg = 'Error {0} encountered while deleting lab directory'.format(str(e))
            updatelog(err_msg)
            logging.error(traceback.format_exc())
            return[False, err_msg]
    else:
        updatelog('No lab directory found! Creating a new directory')
        try:
            os.mkdir(lab_path)
            return [True, 'Empty lab directory created successfully!']
        except Exception as e:
            err_msg = 'Error: {0} encountered while creating empty lab directory!'.format(str(e))
            updatelog(err_msg)
            logging.error(traceback.format_exc())
            return[False, err_msg]

def handle_exit():
    '''
    Save logs and exit
    '''
    global raw_log, log_file
    if os.path.isfile(log_file):
        with open(log_file, 'a', encoding='utf-8') as lf:
            lf.write(raw_log)
    else:
        f = open(log_file, 'w+', encoding='utf-8')
        f.write(raw_log)
        f.close()
    exit()

def signal_handler(signal, frame):
    # Handle Ctrl+c
    handle_exit()

signal.signal(signal.SIGINT, signal_handler)
