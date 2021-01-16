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

import os
import sys
import core.core as core
import configparser
import json
import logging
import traceback
import zipfile
import shutil
import core.helper as helper
import core.analyze as analysis

class GetLocalExtensions():
    def __init__(self):
        if sys.platform == 'win32':
            self.os = 'windows'
        elif sys.platform == 'darwin':
            self.os = 'osx'
        elif sys.platform == 'linux' or sys.platform == 'linux2':
            self.os = 'linux'
        else:
            self.os = 'unknown'
        
        self.user_directory = os.path.expanduser('~')
        core.updatelog('User Directory: ' + self.user_directory)
        self.chrome_extensions = []
        self.firefox_extensions = []
        self.brave_extensions = []
    
    def googlechrome(self):

        # TODO: add support for mac os

        chrome_directory = ""
        if self.os == 'windows':
            chrome_directory = helper.fixpath(self.user_directory + '\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Extensions')
        elif self.os == 'linux':
            chrome_directory = helper.fixpath(self.user_directory + '/.config/google-chrome/Default/Extensions')
        elif self.os == 'osx':
        	chrome_directory = helper.fixpath(self.user_directory + '/Library/Application Support/Google/Chrome/Profile 1/Extensions')
        
        if chrome_directory != "":
            if os.path.isdir(chrome_directory):
                core.updatelog('Found Google chrome extension directory: ' + chrome_directory)
                extension_dirs = os.listdir(chrome_directory)
                for extension_dir in extension_dirs:
                    # print('\n\n')
                    if os.path.isdir(os.path.join(chrome_directory, extension_dir)):
                        # Every extension directory is like this: Extension/<id>/<version>/{contents}
                        extension_path = os.path.join(chrome_directory, extension_dir)
                        extension_vers = os.listdir(extension_path)
                        for ver in extension_vers:
                            manifest_file = helper.fixpath(extension_path + "/" + ver + '/manifest.json')
                            if os.path.isfile(manifest_file):
                                ext_name = core.GetNameFromManifest(manifest_file)
                                if ext_name != False and ext_name != None:
                                    # append version with name
                                    ext_version = ver.split('_')[0]
                                    ext_name = ext_name + ' version ' + ext_version
                                    self.chrome_extensions.append(ext_name + ',' + helper.fixpath(extension_path + "/" + ver))
                                else:
                                    core.updatelog('Could not determine extension name.. skipping local chrome extension')
                            else:
                                core.updatelog('Invalid extension directory: ' + extension_path)
                return self.chrome_extensions
            else:
                core.updatelog('Could not find google chrome directory!')
                return False
        else:
            core.updatelog('Unsupported OS')

    def braveLocalExtensionsCheck(self):
        brave_directory = ""
        if self.os == 'windows':
            brave_directory = helper.fixpath(self.user_directory + '\\AppData\\Local\\BraveSoftware\\Brave-Browser\\User Data\\Default\\Extensions')
        elif self.os == 'linux':
            brave_directory = helper.fixpath(self.user_directory + '/.config/BraveSoftware/Brave-Browser/Default/Extensions')
        
        if brave_directory != "":
            if os.path.isdir(brave_directory):
                core.updatelog('Found Brave extension directory: ' + brave_directory)
                extension_dirs = os.listdir(brave_directory)
                for extension_dir in extension_dirs:
                    # print('\n\n')
                    if os.path.isdir(os.path.join(brave_directory, extension_dir)):
                        # Every extension directory is like this: Extension/<id>/<version>/{contents}
                        extension_path = os.path.join(brave_directory, extension_dir)
                        extension_vers = os.listdir(extension_path)
                        for ver in extension_vers:
                            manifest_file = helper.fixpath(extension_path + "/" + ver + '/manifest.json')
                            if os.path.isfile(manifest_file):
                                ext_name = core.GetNameFromManifest(manifest_file)
                                if ext_name != False and ext_name != None:
                                    # append version with name
                                    ext_version = ver.split('_')[0]
                                    ext_name = ext_name + ' version ' + ext_version
                                    self.brave_extensions.append(ext_name + ',' + helper.fixpath(extension_path + "/" + ver))
                                else:
                                    core.updatelog('Could not determine extension name.. skipping local brave extension')
                            else:
                                core.updatelog('Invalid extension directory: ' + extension_path)
                return self.brave_extensions
            else:
                core.updatelog('Could not find google chrome directory!')
                return False
        else:
            core.updatelog('Unsupported OS')

    def firefox(self):
        # read the profiles.ini
        # check for previous list and create new if not found [list = extanalysis.json]
        # Get a list of all the xpi files
        # Unzip them
        # Get all their names from manifest.json
        # update the list
        firefox_directory = ""
        
        if self.os == 'windows':
            firefox_directory = helper.fixpath(self.user_directory + '\\AppData\\Roaming\\Mozilla\\Firefox')
            
            if os.path.isdir(firefox_directory):
                # firfox installed
                firefox_profile = helper.fixpath(firefox_directory + '\\profiles.ini')
                if os.path.isfile(firefox_profile):
                    # found firefox profiles.ini
                    try:
                        firefox_config = configparser.SafeConfigParser()
                        with open(firefox_profile, 'rU') as ini_source:
                            firefox_config.readfp(ini_source)
                        default_profile_path = os.path.normpath(os.path.join(firefox_directory, firefox_config.get('Profile0', 'Path')))
                        core.updatelog('Found firefox profile path: ' + default_profile_path)
                    except Exception as e:
                        core.updatelog('Something went wrong while reading firefox profiles.ini')
                        logging.error(traceback.format_exc())
                        return False
                else:
                    core.updatelog('Could not find profiles.ini ExtAnalysis can\'t analyze local firefox extensions')
                    return False
            else:
                # Could not find firefox directory
                core.updatelog('Firefox installation could not be detected')
                return False
        elif self.os == 'linux':
            firefox_directory = helper.fixpath(self.user_directory + '/.mozilla/firefox/')
            if os.path.isdir(firefox_directory):
                # firfox installed
                firefox_profile = helper.fixpath(firefox_directory + '/profiles.ini')
                if os.path.isfile(firefox_profile):
                    # found firefox profiles.ini
                    try:
                        firefox_config = configparser.SafeConfigParser()
                        with open(firefox_profile, 'rU') as ini_source:
                            firefox_config.readfp(ini_source)
                        default_profile_path = os.path.normpath(os.path.join(firefox_directory, firefox_config.get('Profile0', 'Path')))
                        core.updatelog('Found firefox profile path: ' + default_profile_path)
                    except Exception as e:
                        core.updatelog('Something went wrong while reading firefox profiles.ini')
                        logging.error(traceback.format_exc())
                        return False
                else:
                    core.updatelog('Could not find profiles.ini ExtAnalysis can\'t analyze local firefox extensions')
                    return False
            else:
                # Could not find firefox directory
                core.updatelog('Firefox installation could not be detected')
                return False
        
        if default_profile_path != "":
            if os.path.isdir(default_profile_path):
                # profile path is valid
                firefox_extension_directory = os.path.join(default_profile_path, 'extensions')
                if os.path.join(firefox_extension_directory):
                    unfiltered_files = os.listdir(firefox_extension_directory)
                    xpi_files = []
                    for afile in unfiltered_files:
                        if afile.endswith('.xpi') and os.path.isfile(os.path.join(firefox_extension_directory, afile)):
                            xpi_files.append(afile)
                    core.updatelog('xpi list generated')
                else:
                    core.updatelog('extensions directory could not be found inside firefox default profile')
                    return False
            else:
                core.updatelog('Invalid firefox profile path... Can\'t get local firefox extensions')
                return False
        else:
            core.updatelog('Could not find default profile path for firefox')
            return False

        if xpi_files != []:
            exta_firefox_list = os.path.join(firefox_extension_directory, 'extanalysis.json')
            if os.path.isfile(exta_firefox_list):
                # found previous list
                core.updatelog('Found previous analysis log.. updating with current extensions')
                listed_extensions = []
                list_file = open(exta_firefox_list, 'r')
                list_files = json.loads(list_file.read())
                for list_file in list_files['extensions']:
                    listed_extensions.append(list_file)
                for xpi_file in xpi_files:
                    if xpi_file not in listed_extensions:
                        core.updatelog('Inserting ' + xpi_file + ' into list')
                        self.createFirefoxListing(firefox_extension_directory, xpi_file)
                # return True
            else:
                core.updatelog('Creating ExtAnalysis list file')
                list_file = open(exta_firefox_list, 'w+')
                list_file.write('{"extensions":{}}')
                list_file.close()
                core.updatelog('Updating list file with all xpi file infos')
                for xpi_file in xpi_files:
                    core.updatelog('Inserting ' + xpi_file + ' into list')
                    self.createFirefoxListing(firefox_extension_directory, xpi_file)
                # return True
        else:
            core.updatelog('No installed firefox extensions found!')
            return False
        
        # Read the final list and then create return list and return it
        firefox_extensions_list = []
        read_list = open(exta_firefox_list, 'r')
        read_list = json.loads(read_list.read())
        if read_list['extensions'] != {}:
            # There are some extensions
            for fext in read_list['extensions']:
                prepare_to_insert = read_list['extensions'][fext]['name'] + ',' + read_list['extensions'][fext]['file']
                firefox_extensions_list.append(prepare_to_insert)
            return firefox_extensions_list
        else:
            core.updatelog('ExtAnalysis could not find any local firefox extensions')

    def createFirefoxListing(self, extension_directory, xpi_file):
        list_file = os.path.join(extension_directory, 'extanalysis.json')
        xpi_directory = os.path.join(extension_directory, xpi_file)
        if os.path.isfile(xpi_directory) and os.path.isfile(list_file):
            # extract the xpi file get name from manifest and delete the extract directory
            extract_directory = os.path.join(extension_directory, 'extanalysis_temp_directory_delete_if_not_done_automatically')
            try:
                core.updatelog('Trying to unzip xpi: ' + xpi_file)
                zip_contents = zipfile.ZipFile(xpi_directory, 'r')
                zip_contents.extractall(extract_directory)
                zip_contents.close()
                core.updatelog('Unzipped xpi successfully: ' + xpi_directory)
                xpi_manifest = os.path.join(extract_directory, 'manifest.json')
                if os.path.isfile(xpi_manifest):
                    ext_name = core.GetNameFromManifest(xpi_manifest)
                    if ext_name != False or ext_name != None:
                        # DO shits
                        core.updatelog(xpi_file + ' has the name: ' + ext_name + ' adding it to the list')
                        list_content = open(list_file, 'r')
                        list_content = list_content.read()
                        list_content = json.loads(list_content)
                        list_content['extensions'][xpi_file] = ({"name":ext_name, "file":xpi_directory})
                        list_write = open(list_file, 'w+')
                        list_write.write(json.dumps(list_content, indent=4, sort_keys=True))
                        list_write.close()
                        core.updatelog('List updated! Deleting temp extract directory')
                        shutil.rmtree(extract_directory)
                        core.updatelog('Removed temp extract directory')
                        return True
                    else:
                        core.updatelog('Could not file extension name hence it will not be added to the list')
                else:
                    core.updatelog('No manifest file found after extracting xpi! Deleting temp extract directory')
                    shutil.rmtree(extract_directory)
                    core.updatelog('Removed temp extract directory')
                    return False
            except Exception as e:
                core.updatelog('Error unzipping xpi file: ' + xpi_directory)
                logging.error(traceback.format_exc())
                return False

def analyzelocalfirefoxextension(path):
    if os.path.isfile(path) and path.endswith('.xpi'):
        # Extract the .xpi file to a temp directory in lab directory
        # Analyze the extracted directory
        # delete the temp directory
        extract_directory = helper.fixpath(core.lab_path + '/temp_extract_directory')

        try:
            core.updatelog('Unzipping ' + path + ' to: ' + extract_directory)
            zip_contents = zipfile.ZipFile(path, 'r')
            zip_contents.extractall(extract_directory)
            zip_contents.close()
            core.updatelog('Unzipping complete')
        except Exception as e:
            helper.fixpath('Something went wrong while unzipping ' + path + ' to ' + extract_directory)
            logging.error(traceback.format_exc())
            return False
        
        analysis_status = analysis.analyze(extract_directory, 'Local Firefox Extension')

        if 'error:' in analysis_status:
            core.updatelog('Something went wrong while analysis... deleting temporary extract directory')
        else:
            core.updatelog('Scanning complete... Deleting temporary extract directory')
        
        shutil.rmtree(extract_directory)
        core.updatelog('Successfully deleted: ' + extract_directory)
        return analysis_status

    else:
        core.updatelog('[analyzelocalfirefoxextension] Invalid local firefox extension path: ' + path)
