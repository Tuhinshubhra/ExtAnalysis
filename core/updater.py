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

import core.core as core
import core.scans as scan
import logging, traceback
import core.helper as helper
import os
import sys
import tempfile
import subprocess

def check():
    '''
    Check for update
    '''
    print('==== ExtAnalysis Update Check ====')
    core.updatelog('Current Version: ' + core.version)
    current_version = int(core.version.replace('.', ''))

    core.updatelog('Getting new version from github')
    v = scan.source_code(core.version_url)
    if v[0]:
        # Successfully acquired source code
        try:
            # validate version
            latest_version = int(v[1].replace('.', '').replace('\n', ''))
            core.updatelog('Latest version: ' + v[1])
            if latest_version > current_version:
                # Update available
                update_prompt = input('New Version available! Update Now? (y/n): ').lower()
                if update_prompt == 'y':
                    # update it
                    update()
                else:
                    core.updatelog('Update cancled! Make sure update the app later')
                    core.handle_exit()
            elif latest_version == current_version:
                print("you're already on the latest version!")
                core.handle_exit()
            else:
                print('The script was tampered with and i don\'t like it!')
                core.handle_exit()
        except Exception as e:
            core.updatelog('Invalid response from github')
            logging.error(traceback.format_exc())
            core.handle_exit()
    else:
        core.updatelog('Something went wrong while getting version from github')
        core.handle_exit()


def update():
    '''
    Updates ExtAnalysis
    1. Create the updater child script and save it to temp directory
    2. End self process and start the child script
    '''
    print("\n[i] Creating Updater file")

    child_script = open(helper.fixpath(core.path + '/db/updater.py'), 'r')
    child_script = child_script.read()

    src = child_script.replace('<current_extanalysis_directory>', core.path.replace('\\', '\\\\'))
    src = src.replace('<github_zip_url>', core.github_zip)

    print('[i] Moving updater file to temp directory')
    temp_dir = tempfile.gettempdir()

    updater_script = helper.fixpath(temp_dir + '/update_extanalysis.py')
    f = open(updater_script, 'w+')
    f.write(src)
    f.close()

    python_loc = sys.executable

    print('[i] Starting Updater script')

    if sys.platform == 'win32':
        os.chdir(temp_dir)
        command = [python_loc, 'update_extanalysis.py']
        subprocess.Popen(command, creationflags=subprocess.CREATE_NEW_CONSOLE, shell=False)
        print('[i] Killing self... Next time we meet I will be a better version of myself ;)')
        exit()
    else:
        os.chdir(temp_dir)
        command = ['x-terminal-emulator', '-e', python_loc, updater_script]
        subprocess.Popen(command, shell=False)
        print('[i] Killing self... Next time we meet I will be a better version of myself ;)')
        exit()
