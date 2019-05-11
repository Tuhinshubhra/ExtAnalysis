"""
ExtAnalysis - Browser Extension Analysis Framework
Copyright (C) 2019 Tuhinshubhra

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
import json
import core.core as core
import logging, traceback

def init_settings():
    # Check if reports file exist if not create an empty one
    if not os.path.isfile(core.report_index):
        rif = open(core.report_index, 'w+')
        empty_reports = {"reports": []}
        rif.write(json.dumps(empty_reports, indent=4))
        rif.close()
        core.updatelog('Created empty reports file')

    # Check if settings file exist if not get the contents from github and create one
    if not os.path.isfile(core.settings_file):
        core.updatelog('Could not find settings.json file. Downloading it from github...')
        try:
            import urllib.request
            raw_settings = 'https://raw.githubusercontent.com/Tuhinshubhra/ExtAnalysis/master/settings.json'
            urllib.request.urlretrieve(raw_settings, core.settings_file)
            core.updatelog('New settings file successfully generated!')
        except Exception as e:
            core.updatelog('Error {0} encountered while getting settings file from github... Please download a clean version of ExtAnalysis from github.'.format(str(e)))
            logging.error(traceback.format_exc())
            core.handle_exit()


    if os.path.isfile(core.settings_file):
        try:
            with open(core.settings_file, 'r') as sc:
                settings = json.loads(sc.read())

            '''
            INIT VIRUSTOTAL API
            '''
            if settings['virustotal_api'] != '':
                core.virustotal_api = settings['virustotal_api']
            else:
                core.updatelog('Virustotal api was not specified... Files won\'t be scanned')
            
           
            '''
            INIT REPORT DIRECTORY...
            '''
            new_results_dir = settings['results_directory_path']
            old_results_dir = settings['old_result_directory']
            if new_results_dir == '':
                new_results_dir = core.reports_path
            if old_results_dir == '':
                old_results_dir = core.reports_path
            ### Check if the results directory have changed... if yes we have to change paths
            if new_results_dir != old_results_dir:
                core.updatelog('Reports path change detected! fixing old paths and updating report index...')
                path_changed(old_results_dir, new_results_dir)
            # set it
            if core.reports_path != new_results_dir:
                if os.path.isdir(new_results_dir):
                    core.reports_path = new_results_dir
                else:
                    core.updatelog('Invalid results_directory_path specified in settings.json! using default path: {0}'.format(core.reports_path))
            
            
            '''
            INIT LAB DIRECTORY
            '''
            lab_dir = settings['lab_directory_path']
            if lab_dir != '' and lab_dir != core.lab_path:
                if os.path.isdir(lab_dir):
                    core.lab_path = lab_dir
                else:
                    core.updatelog('Invalid lab_directory_path specified in settings.json! using default lab path: {0}'.format(core.lab_path))
            elif lab_dir == '' and not os.path.isdir(core.lab_path):
                core.updatelog('Creating lab directory: ' + core.lab_path)
                try:
                    os.mkdir(core.lab_path)
                except:
                    core.updatelog('Something went wrong while creating lab directory!')
                    logging.error(traceback.format_exc())
                    core.handle_exit()
            
            '''
            CHECK IGNORE CSS VAR
            '''
            if not settings['ignore_css']:
                core.ignore_css = False
                core.updatelog('CSS files will not be ignored!')

            '''
            ALL THE INTEL EXTRACTION SETTINGS GO HERE
            '''
            if not settings['extract_comments']:
                # comment extraction set to false
                core.extract_comments = False
                core.updatelog('Skipping comments extraction')


            if not settings['extract_btc_addresses']:
                # BTC Address extraction set to false
                core.extract_btc_addresses = False
                core.updatelog('Skipping Bitcoin address extraction')

            if not settings['extract_base64_strings']:
                # Base64 encoded strings extraction set to false
                core.extract_base64_strings = False
                core.updatelog('Skipping Base64 strings extraction')

            if not settings['extract_email_addresses']:
                # Comments extraction set to false
                core.extract_email_addresses = False
                core.updatelog('Skipping email address extraction')

            if not settings['extract_ipv4_addresses']:
                # IPv4 address extraction set to false
                core.extract_ipv4_addresses = False
                core.updatelog('Skipping IPv4 address extraction')

            if not settings['extract_ipv6_addresses']:
                # IPv6 address extraction set to false
                core.extract_ipv6_addresses = False
                core.updatelog('Skipping IPv6 address extraction')

            return [True, 'All settings loaded']
        
        
        except Exception as e:
            core.updatelog('Something went wrong while reading settings file. Error: ' + str(e))
            logging.error(traceback.format_exc())
            return [False, 'error reading settings file']
    else:
        core.updatelog('Settings file not found... Some features might not work as intended')
        return [False, 'settings.json not found']

def path_changed(old_path, new_path):
    # Change '<reports_path>' to absolute path in results file

    if core.reportids == {}:
        ri = open(core.report_index, 'r')
        ri = ri.read()
        core.reportids = json.loads(ri)
    reports = core.reportids
    for report in reports['reports']:
        if '<reports_path>' in report['report_directory']:
            core.updatelog('[Updating reports index] Chainging <report_index> to: ' + old_path)
            report['report_directory'] = report['report_directory'].replace('<reports_path>', old_path)
    
    core.reportids = reports
    ri = open(core.report_index, 'w+')
    ri.write(json.dumps(reports, indent=4, sort_keys=True))
    ri.close()
    core.updatelog('Report index updated successfully')
    core.updatelog('Updating settings.json')
    sj = open(core.settings_file, 'r')
    sj = json.loads(sj.read())
    sj['old_result_directory'] = new_path
    wsj = open(core.settings_file, 'w+')
    wsj.write(json.dumps(sj, indent=4, sort_keys=False))
    wsj.close()
    core.updatelog('Updated settings.json successfully')

def changedir(newpath):
    '''
    change the results_directory_path in settings.json
    response [True/False, 'message']
    '''
    if os.path.isdir(newpath):
        core.updatelog('Setting results directory to: ' + newpath)
        settings = open(core.settings_file, 'r')
        settings = json.loads(settings.read())
        old_reports_path = settings['results_directory_path']
        if old_reports_path == '':
            old_reports_path = core.reports_path
        if newpath == old_reports_path:
            return[False, 'Please provide a different path, not the current one!']
        settings['results_directory_path'] = newpath
        core.updatelog('Updating settings.json')
        try:
            ws = open(core.settings_file, 'w+')
            ws.write(json.dumps(settings, indent=4, sort_keys=False))
            ws.close()
            core.updatelog('File successfully updated! rewriting variables and fixing old paths...')
            core.reports_path = newpath
            path_changed(old_reports_path, newpath)
            return[True, 'Analysis report directory updated successfully!']
        except Exception as e:
            logging.error(traceback.format_exc())
            return[False, 'Error while writing settings file: ' + str(e)]
    else:
        return [False, 'invalid path']

def changelabdir(newpath):
    '''
    change the results_directory_path in settings.json
    response [True/False, 'message']
    '''
    if os.path.isdir(newpath):
        core.updatelog('Setting lab directory to: ' + newpath)
        settings = open(core.settings_file, 'r')
        settings = json.loads(settings.read())
        old_reports_path = settings['lab_directory_path']
        if old_reports_path == '':
            old_reports_path = core.lab_path
        if newpath == old_reports_path:
            return[False, 'Please provide a different path, not the current one!']
        settings['lab_directory_path'] = newpath
        core.updatelog('Updating settings.json')
        try:
            ws = open(core.settings_file, 'w+')
            ws.write(json.dumps(settings, indent=4, sort_keys=False))
            ws.close()
            core.updatelog('File successfully updated! rewriting variables and fixing old paths...')
            core.lab_path = newpath
            return[True, 'Lab directory updated successfully!']
        except Exception as e:
            logging.error(traceback.format_exc())
            return[False, 'Error while writing settings file: ' + str(e)]
    else:
        return [False, 'invalid path']


def change_vt_api(api):
    '''
    change virustotal api!
    parameters needed = api = new api
    '''
    if api != core.virustotal_api:
        # Not the same api
        core.updatelog('Setting new virustotal api!')
        settings = open(core.settings_file, 'r')
        settings = json.loads(settings.read())
        settings['virustotal_api'] = api
        try:
            ws = open(core.settings_file, 'w+')
            ws.write(json.dumps(settings, indent=4, sort_keys=False))
            ws.close()
            core.virustotal_api = api
            core.updatelog('New virustotal api set successfully! new api: ' + api)
            return[True, 'New virustotal api set successfully!']
        except Exception as e:
            logging.error(traceback.format_exc())
            return[False, 'Error while writing settings file: ' + str(e)]

    else:
        return [False, 'This api is already in use. Nothing changed!']

def update_settings_batch(settings_dict):
    '''
    FUNCTION TO UPDATE SETTINGS KEYS THAT HAVE TRUE/FALSE VALUES
    NEEDED PARAMETERS:
    settings_dict = DICT WITH NAME AND VALUES.. ex: {"extract_comment":"true"}
    '''
    update_type = '' # 0 = failed, 1 = success, 2 = some updated some not!
    try:
        settings = open(core.settings_file, 'r')
        settings = json.loads(settings.read())

        for the_setting in settings_dict:
            try:
                if type(settings[the_setting]) == bool:
                    # okay settings key is good...
                    if str(settings_dict[the_setting]).lower() == 'true':
                        # set to true
                        settings[the_setting] = True
                        core.updatelog('Set the value of {0} to True successfully'.format(the_setting))
                        # set update type
                        if update_type == '':
                            update_type = '1'
                        elif update_type == '0':
                            update_type = '2'
                    elif str(settings_dict[the_setting]).lower() == 'false':
                        # set to false
                        settings[the_setting] = False
                        core.updatelog('Set the value of {0} to False successfully'.format(the_setting))
                        # set update type
                        if update_type == '':
                            update_type = '1'
                        elif update_type == '0':
                            update_type = '2'
                    else:
                        core.updatelog('Invalid value: {1} for setting {0}'.format(the_setting, str(settings_dict[the_setting])))
                        # set update type
                        if update_type == '':
                            update_type = '0'
                        elif update_type == '1':
                            update_type = '2'
            except Exception as e:
                logging.error(traceback.format_exc())
                if update_type == '':
                    update_type = '0'
                elif update_type == '1':
                    update_type = '2'
        try:
            ws = open(core.settings_file, 'w+')
            ws.write(json.dumps(settings, indent=4, sort_keys=False))
            ws.close()
            core.updatelog('Settings written to file successfully! Restart ExtAnalysis for them to take effect')
        except Exception as e:
            core.updatelog('Error {0} occured while writing settings.json file'.format(str(e)))
            logging.error(traceback.format_exc())
            return '0'
        return update_type

    except Exception as e:
        core.updatelog('Error {0} occured while updating settings'.format(str(e)))
        logging.error(traceback.format_exc())
        return '0'
        