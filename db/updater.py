#!/usr/bin/python3
# -*- coding: utf-8 -*-

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

# This is the updater script for ExtAnalysis

import urllib.request
import zipfile
import os
from distutils.dir_util import copy_tree
import shutil
import tempfile
import json
import time
import logging, traceback
import sys

current_dir = '<current_extanalysis_directory>'
download_link = '<github_zip_url>'
temp_dir = tempfile.gettempdir()
temp_exta_dir = os.path.join(temp_dir, 'extanalysis_temp').replace('\\', '\\\\')
script_path = os.path.join(temp_dir, 'update_extanalysis.py').replace('\\', '\\\\')
last_percent_reported = 0

def download_progress_hook(count, blockSize, totalSize):
    global last_percent_reported
    percent = int(count * blockSize * 100 / totalSize)

    if last_percent_reported != percent:
        if percent % 10 == 0:
            print('[V] Downloaded {0}%'.format(str(percent)))

    last_percent_reported = percent

# STEP 1. Copy the reports and lab directory
print('=== ExtAnalysis Updater Script ===')
print('          Version 1.0.1           \n\n')
print('[~] Waiting 3 seconds for main process to die!\n')
time.sleep(3) # sleep for 5 seconds to let the main process exit

# Download File
print('[i] Downloading zip from github... (Please be patient.. GitHub servers can be painfully slow at times!)\n')
zip_loc = os.path.join(temp_dir, 'extanalysis.zip').replace('\\', '\\\\')

# Check if any previous version is present
if os.path.isfile(zip_loc):
    # Delete old zip
    os.remove(zip_loc)

# Download the zip
try:
    urllib.request.urlretrieve(download_link, zip_loc, reporthook=download_progress_hook)
    print('\n[+] Zip Successfully downloaded: ' + zip_loc)
except Exception as e:
    print('[!] Something went wrong while downloading zip! Please update extanalysis manually')
    logging.error(traceback.format_exc())
    end = input('Press [Enter] To exit!')
    exit()

# Extract the zip
print('[i] Unzipping new zip: {0}'.format(zip_loc))
extract_location = os.path.join(temp_dir, 'extanalysis_new').replace('\\', '\\\\')
try:
    zip_contents = zipfile.ZipFile(zip_loc, 'r')
    zip_contents.extractall(extract_location)
    zip_contents.close()
    print('[+] Unzipped successfully to: ' + extract_location)
except Exception as e:
    print('[!] Something went wrong while extracting zip! Please update extanalysis manually')
    logging.error(traceback.format_exc())
    end = input('Press [Enter] To exit!')
    exit()

# Real directory
new_dir = os.path.join(extract_location, 'ExtAnalysis-master').replace('\\', '\\\\')

# Directories
dirs_to_copy = ['lab', 'reports']

# Files
files_to_copy = ['settings.json', 'extanalysis.log', 'reports.json']

# Copy old files and directories
try:
    if not os.path.isdir(temp_exta_dir):
        # Create the temporary directory
        os.mkdir(temp_exta_dir)
    else:
        # Previous directory... remove it and create empty one
        shutil.rmtree(temp_exta_dir)
        os.mkdir(temp_exta_dir)

    print('\n[i] Copying directories into temporary directory\n')
    for _dir in dirs_to_copy:
        try:
            src = os.path.join(current_dir, _dir).replace('\\', '\\\\')
            dst = os.path.join(temp_exta_dir, _dir).replace('\\', '\\\\')
            shutil.copytree(src, dst)
            print('[+] Directory {0} successfully copied!'.format(src))
        except Exception as e:
            print('[!] Failed to copy directory {0}. Error: {1}'.format(_dir, str(e)))

    print('\n[i] Copying Files into temprary directory\n')
    for _file in files_to_copy:
        try:
            src = os.path.join(current_dir, _file).replace('\\', '\\\\')
            dst = os.path.join(temp_exta_dir, _file).replace('\\', '\\\\')
            shutil.copyfile(src, dst)
            print('[+] File {0} successfully copied!'.format(src))
        except Exception as e:
            print('[!] Failed to copy File {0}. Error: {1}'.format(_file, str(e)))

except Exception as e:
    print('Error While copying...')


# Remove old extanalysis directory
print('\n[i] Removing old ExtAnalysis directory: ' + current_dir)
for root, dirs, files in os.walk(current_dir):
    for f in files:
        try:
            os.unlink(os.path.join(root, f)).replace('\\', '\\\\')
        except Exception as e:
            print('[!] Error {0} encountered while deleting {1}'.format(str(e), f))

    for d in dirs:
        try:
            shutil.rmtree(os.path.join(root, d)).replace('\\', '\\\\')
        except Exception as e:
            print('[!] Error {0} encountered while deleting {1}'.format(str(e), f))

# Move the downloaded one to old location
print('\n[i] Copying new version to old location...')
try:
    copy_tree(new_dir, current_dir)
    print('[+] Copy successful!')
except:
    # Manual instruction
    logging.error(traceback.format_exc())
    print('\n\n\n SOMETHING WENT WRONG WHILE COPYING NEW VERSION TO OLD DIRECTORY!\n\nFollow the directions to do it manually:\n')
    print('Step 1. Create a new directory: ' + current_dir)
    print('Step 2. Copy the contents of "{0}" to the previously created directory!'.format(new_dir))
    print('Step 3. Copy the contents of "{0}" too.. these contains your log, settings, reports dir and lab dir')
    print('Step 4. Once everything is done delete the following (temporary files and directories):')
    print('[1] {0}\n[2] {1}\n[3] {2}\n[4] {3}'.format(temp_exta_dir, extract_location, os.path.join(temp_dir, 'extanalysis.zip').replace('\\', '\\\\'), script_path))
    print('\n\n')
    end = input('When done... Press [ENTER] to exit')
    exit()

# Update the new settings file
new_settings = os.path.join(new_dir, 'settings.json').replace('\\', '\\\\')
old_settings = os.path.join(temp_exta_dir, 'settings.json').replace('\\', '\\\\')
with open(new_settings, 'r') as ns, open(old_settings, 'r') as ols:
    news = json.loads(ns.read())
    olds = json.loads(ols.read())
news.update(olds)
write_settings = open(old_settings, 'w')
write_settings.write(json.dumps(news, indent=4, sort_keys=False))
write_settings.close()

# Copy old files and dirs
print('\n[i] Copying your old files\n')
for _file in files_to_copy:
    try:
        src = os.path.join(current_dir, _file).replace('\\', '\\\\')
        dst = os.path.join(temp_exta_dir, _file).replace('\\', '\\\\')
        if os.path.isfile(src):
            # delete the file so that we can write the old file (might be a bad idea...)
            os.remove(src)
        shutil.copyfile(dst, src)
        print('[+] File {0} successfully copied!'.format(src))
    except Exception as e:
            print('[!] Failed to copy File {0}. Error: {1}'.format(_file, str(e)))

print('\n[i] Copying your old directories\n')
for _dir in dirs_to_copy:
    try:
        src = os.path.join(current_dir, _dir).replace('\\', '\\\\')
        dst = os.path.join(temp_exta_dir, _dir).replace('\\', '\\\\')
        if os.path.isdir(src):
            shutil.rmtree(src)
        shutil.copytree(dst, src)
        print('[+] Directory {0} successfully copied!'.format(src))
    except Exception as e:
        print('[!] Failed to copy directory {0}. Error: {1}'.format(_dir, str(e)))


# Cleanup
dirs_to_clean = [temp_exta_dir, extract_location]
files_to_clean = ['extanalysis.zip']
print('\n[i] Initiating clean-up procedure')

for _dir in dirs_to_clean:
    try:
        shutil.rmtree(_dir)
        print('[-] Successfully deleted ' + _dir)
    except Exception as e:
        print('[!] Error {0} encountered while deleting {1}'.format(str(e), _dir))

for _file in files_to_clean:
    _dir = os.path.join(temp_dir, _file).replace('\\', '\\\\')
    try:
        os.remove(_dir)
        print('[-] Successfully deleted ' + _dir)
    except Exception as e:
        print('[!] Error {0} encountered while deleting {1}'.format(str(e), _dir))

end = input('\n\n[*] UPDATE SUCCESSFUL!\n\nPress [ENTER] To exit and self destruct update script!')

if sys.platform == 'win32':
    exit_command = 'ping 127.0.0.1 -n 4 > nul & del ' + script_path
else:
    exit_command = 'sleep 3 && rm ' + script_path

os.system(exit_command)
exit()
