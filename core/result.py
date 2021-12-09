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
import core.core as core
import json
import time
import traceback
import logging
import shutil
import core.helper as helper
import plugins.retirejs as retirejs

class createresult:

    def __init__(self, directory):
        self.current_file_number = 0
        self.current_directory_number = 0
        self.current_url_number = 0
        self.files = []
        self.dirs = []
        self.urls = []
        self.nodes = 'var nodes = new vis.DataSet(['
        self.edges = 'var edges = new vis.DataSet(['
        self.directory = directory
        self.extension_name = core.report['name']
        self.list_status = self.list(directory)

    def list(self, directory, parent=0):
        # This function is the one that helps create the graph for real
        # sub_directories list contains all the directories inside the current directory which we will use later
        # sub_directory = path,name
        sub_directories = []

        if self.current_directory_number == 0:
            # This means that this is the first time we're doing the directory listing so let's set directory 0 to the extension
            self.dirs.append({'id':'EXTAD0', 'name':self.extension_name, 'type':'extension', 'path':'/', 'parent':'none'})
            self.current_directory_number += 1

        if os.path.isdir(directory):
            # The given path is a directory and we will continue
            # core.updatelog('FUNCTION LIST IS EXECUTING ON: ' + directory)
            dirlist = os.listdir(directory)

            for folder in dirlist:
                # let's get the path...
                # print('Checking file: ' + folder)
                route = os.path.join(directory, folder)
                if os.path.isdir(route):
                    # Directory detected let's add it to the sub_directories list
                    sub_directories.append(route + ',' + str(self.current_directory_number))
                    self.dirs.append({'id':'EXTAD' + str(self.current_directory_number), 'name':folder, 'type':'directory', 'path':route, 'parent':'EXTAD' + str(parent)})
                    self.current_directory_number += 1
                else:
                    # this is a file let's classify it and add it to the list
                    if folder.endswith(('.html', '.htm')):
                        file_type = 'html'
                    elif folder.endswith('.js'):
                        file_type = 'js'
                    elif folder.endswith('.css'):
                        file_type = 'css'
                    elif folder.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.svg')):
                        file_type = 'static'
                    elif folder.endswith('.json'):
                        file_type = 'json'
                    else:
                        file_type = 'other'

                    self.files.append({'id':'EXTAF' + str(self.current_file_number), 'name':folder, 'path':route, 'type': file_type, 'parent':'EXTAD' + str(parent)})
                    self.current_file_number += 1
                # now that we are done with all the files let's go through the sub directories and work them out

            for sub_directory in sub_directories:
                # process all the sub directories
                # core.updatelog('Processing SUBDIRECTORY: ' + sub_directory)
                sub_directory = sub_directory.split(',')
                sub_parent = sub_directory[1]
                sub_directory = sub_directory[0]
                self.list(sub_directory, sub_parent)
        else:
            # Given path is not a directory hence no need for continuing
            return False

    def creategraphdata(self):
        if self.list_status != False:
            # Extract urls from all html, json, js files
            for file in self.files:
                if file['type'] == 'json' or file['type'] == 'html' or file['type'] == 'js':
                    file_path = file['path']
                    file_id = file['id']
                    file_urls = []
                    try:
                        core.updatelog('Trying to extract urls from: ' + file_path)
                        file_urls = core.extract_urls(file_path)
                        if file_urls != [] and file_urls != False:
                            for file_url in file_urls:
                                self.urls.append({'id':'EXTAU' + str(self.current_url_number), 'parent':file_id, 'type':'url', 'name':file_url})
                                self.current_url_number += 1
                    except Exception as e:
                        core.updatelog('Skipped getting URL from file: ' + file_path + ' Error: ' + str(e))
                        logging.error(traceback.format_exc())
            # TODO: Clean this mess and use format
            for file in self.files:
                # print('Doing File: ' + file + ' parent: ' + file['parent'])
                #prepare_node = '\n{ id: "{0}", label: "{1}", group: "{2}", cid: "{3}" },'.format(file['id'], file['name'], file['type'], file['parent'])
                prepare_node = '\n{id: "' + file['id'] + '", label: "' + file['name'] + '", group: "' + file['type'] + '", cid: "'+file['parent']+'"},'
                self.nodes += prepare_node
                #prepare_edge = '\n{ from: "{0}", to: "{1}", color:{color:\'#fff\', highlight:\'#89ff00\'} },'.format(file['parent'], file['id'])
                prepare_edge = '\n{from: "' + file['parent'] + '", to: "' + file['id'] + '", color:{color:\'#fff\', highlight:\'#89ff00\'}},'
                self.edges += prepare_edge

            for file in self.dirs:
                if file['parent'] == 'none' and file['id'] == 'EXTAD0':
                    # this is the parent directory i.e the extension
                    #prepare_node = '\n{ id: "{0}", label: "{1}", group: "{2}" },'.format(file['id'], file['name'], file['type'])
                    prepare_node = '\n{id: "' + file['id'] + '", label: "' + file['name'] + '", group: "' + file['type'] + '"},'
                    self.nodes += prepare_node
                else:
                    #prepare_node = '\n{ id: "{0}", label: "{1}", group: "{2}", cid: "{3}" },'.format(file['id'], file['name'], file['type'], file['parent'])
                    prepare_node = '\n{id: "' + file['id'] + '", label: "' + file['name'] + '", group: "' + file['type'] + '", cid: "'+file['parent']+'"},'
                    self.nodes += prepare_node
                    #prepare_edge = '\n{ from: "{0}", to: "{1}", color:{color:\'#fff\', highlight:\'#89ff00\'} },'.format(file['parent'], file['id'])
                    prepare_edge = '\n{from: "' + file['parent'] + '", to: "' + file['id'] + '", color:{color:\'#fff\', highlight:\'#89ff00\'}},'
                    self.edges += prepare_edge

            for url in self.urls:
                #prepare_node = '\n{ id: "{0}", label: "{1}", group: "{2}", cid: "{3}"},'.format(url['id'], url['name'], url['type'], url['parent'])
                prepare_node = '\n{id: "' + url['id'] + '", label: "' + url['name'] + '", group: "' + url['type'] + '", cid: "'+url['parent']+'"},'
                self.nodes += prepare_node
                #prepare_edge = '\n{ from: "{0}", to: "{1}", color:{color:\'#fff\', highlight:\'#89ff00\'} },'.format(url['parent'], url['id'])
                prepare_edge = '\n{from: "' + url['parent'] + '", to: "' + url['id'] + '", color:{color:\'#fff\', highlight:\'#89ff00\'}},'
                self.edges += prepare_edge

            self.nodes += '\n]);'
            self.edges += '\n]);'
            # print(self.nodes  + '\n\n\n\n\n\n\n' + self.edges)
            core.updatelog('Graph data creation complete!')
        else:
            core.updatelog('Graph data creation unsuccessful!')
            return False

    def copysource(self, result_directory):
        # copies all the json, html, css and js files and saves them to the result directory
        # create content for the source.json file
        source_json = {}

        # Copies all the json, css, js files to the result directory for future reference
        for file in self.files:
            if file['type'] == 'json' or file['type'] == 'html' or file['type'] == 'css' or file['type'] == 'js':
                file_path = file['path']
                new_path = helper.fixpath(result_directory + '/' + file['name'] + '.src')
                file_name = file['name']
                if os.path.isfile(file_path):
                    # Checks if file present
                    shutil.copyfile(file_path, new_path)
                    core.updatelog('Copied ' + file_path + ' to ' + new_path)
                    # append this to source_json dict
                    rel_path = os.path.relpath(file_path, self.directory)
                    file_size = str(os.path.getsize(file_path) >> 10) + ' KB'
                    if file['type'] == 'js':
                        # Retire js scan
                        core.updatelog('Running retirejs vulnerability scan on: ' + file_name)
                        try:
                            with open(file_path, 'r') as fc:
                                file_content = fc.read()
                                rjs_scan = retirejs.scan_file_content(file_content)
                                core.updatelog('Scan complete!')
                        except Exception as e:
                            core.updatelog('Error {0} while running retirejs scan on {1}'.format(str(e), file_name))
                            rjs_scan = []
                        source_json[file['id']] = ({'id':file['id'], 'file_name':file_name, 'location':new_path, 'relative_path':rel_path, 'file_size':file_size, 'retirejs_result':rjs_scan})
                    else:
                        source_json[file['id']] = ({'id':file['id'], 'file_name':file_name, 'location':new_path, 'relative_path':rel_path, 'file_size':file_size})

        # write all the changes to source.json
        source_file = helper.fixpath(result_directory + '/source.json')
        sf = open(source_file, 'w+')
        sf.write(json.dumps(source_json, indent=4, sort_keys=True))
        sf.close()
        core.updatelog('Saved sources to: ' + source_file)
        return True

    def savereport(self):
        try:
            # Gen scan id
            report = core.report
            reportids = core.reportids

            curid = 'EXA' + time.strftime("%Y%j%H%M%S", time.gmtime())
            core.updatelog('Saving Analysis with ID: ' + curid)
            #saveas = curid + '.json'

            # create result directory
            result_directory = os.path.join(core.reports_path, curid)
            if not os.path.exists(result_directory):
                os.makedirs(result_directory)
                core.updatelog('Created Result directory: ' + result_directory)

            # create the basic report json file: extanalysis_report.json
            report_file = helper.fixpath(result_directory + '/extanalysis_report.json')
            f = open(report_file, 'w+')
            reportfinal = json.dumps(report, sort_keys=True, indent=4)
            f.write(reportfinal)
            f.close()
            core.updatelog('Saved report file: ' + report_file)

            # get file list and create the graph
            graph_data_stat = self.creategraphdata()
            if graph_data_stat != False:
                graph_file = helper.fixpath(result_directory + '/graph.data')
                graph_file_create = open(graph_file, 'w+')
                graph_file_create.write(self.nodes + '\n' + self.edges)
                core.updatelog('Saved graph data to: ' + graph_file)
            else:
                core.updatelog('Could not save graph data!')

            # save the source files
            # print(result_directory)
            self.copysource(result_directory)

            '''
            make an entry in the reports index file
            '''
            # use <reports_path> as a variable!
            relative_result_path = result_directory.replace(core.reports_path, '<reports_path>')
            reportindex = {"name":report['name'], "version":report['version'], "id": curid, "report_directory":relative_result_path, "time":time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())}
            reportids['reports'].append(reportindex)
            indexfile = core.report_index
            g = open(indexfile, 'w+')
            indexfinal = json.dumps(reportids, sort_keys=True, indent=4)
            g.write(indexfinal)
            g.close()
            core.updatelog('Updated report index')

            # Clear global report value for new scan
            core.report = {}

            return(curid)
        except Exception as e:
            logging.error(traceback.format_exc())
            print('Something went wrong while saving result. Error: ' + str(e))

def clearAllResults():
    # Deletes all directories inside reports folder
    # create new reports.json file with the following content {"reports": []}
    core.updatelog('Clearing all results!')
    all_reports = core.reportids
    report_index = core.report_index
    if all_reports == {}:
        ri = open(report_index, 'r')
        ri = ri.read()
        all_reports = core.report_index = json.loads(ri)
    for report in all_reports['reports']:
        core.updatelog('Deleting analysis #{0} - {1}'.format(report['id'], report['name']))
        report_dir = report['report_directory'].replace('<reports_path>', core.reports_path)
        if os.path.isdir(report_dir):
            try:
                shutil.rmtree(report_dir)
                core.updatelog('Analysis #{0} deleted successfully!'.format(report['id']))
            except Exception as e:
                core.updatelog('Something went wrong while deleting Report directory {0}. Error: {1}'.format(report_dir, str(e)))
                logging.error(traceback.format_exc())
        else:
            core.updatelog('Report directory ({1}) of #{0} not found!'.format(report['id'], report_dir))
    core.updatelog('All individual result directories deleted! Updating report index...')
    try:
        i = open(report_index, 'w+')
        js = {"reports": []}
        i.write(json.dumps(js, indent=4, sort_keys=True))
        i.close()
        core.reportids = js
        core.updatelog('Index file successfully created: ' + report_index)
        return True
    except Exception as e:
        core.updatelog('Something went wrong while updating {0}! Error: {1}'.format(report_index, str(e)))
        logging.error(traceback.format_exc())
        return False

def clearResult(result_id):
    # Delete report_directory
    # remove <result_id> entry from reports.json
    report_info = core.get_result_info(result_id)
    if not report_info[0]:
        core.updatelog('No result found for analysis ID: {0}'.format(result_id))
        return False
    analysis_dir = report_info[1]['report_directory']
    reportids = core.reportids
    report_index = core.report_index


    # Check if there is a directory with the analysis id
    if not os.path.isdir(analysis_dir):
        core.updatelog('Could not find any directory with the given analysis ID: ' + result_id)
    else:
        try:
            core.updatelog('Deleting analysis directory: ' + analysis_dir)
            shutil.rmtree(analysis_dir)
            core.updatelog('Successfully deleted analysis directory')
        except Exception as e:
            core.updatelog('Something went wrong while deleting analysis directory: ' + str(e))
            logging.error(traceback.format_exc())

    # Check if there is any analysis id in the index
    if result_id not in str(reportids):
        core.updatelog('No analysis with the id {0} in analysis index file'.format(result_id))
        #print(result_id)
        #print(str(reportids))
        return False
    else:
        reports = reportids['reports']
        for report in reports:
            if report['id'] == result_id:
                reports.remove(report)
        reportids['reports'] = reports
        core.reportids = reportids
        core.updatelog('Removed analysis {0} from index.. writing index to file'.format(result_id))
        r = open(report_index, 'w+')
        r.write(json.dumps(reportids, indent=4, sort_keys=True))
        r.close()
        core.updatelog('Analysis index written to file: ' + report_index)
        return True
