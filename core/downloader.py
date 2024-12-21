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

import urllib.request
import core.core as core
import core.helper as helper
import re

def download(id, name=""):
    ext_id = id
    if name == "":
        save_name = ext_id
    else:
        save_name = name
    save_path = helper.fixpath(core.lab_path + '/' + save_name + '.crx')
    core.updatelog("Downloader says: save_path is " + save_path)
    # dl_url = "https://clients2.google.com/service/update2/crx?response=redirect&x=id%3D" + ext_id + "%26uc&prodversion=32"
    # new download URL, issue #13
    dl_url = "https://clients2.google.com/service/update2/crx?response=redirect&os=win&arch=x86-64&os_arch=x86-64&nacl_arch=x86-64&prod=chromecrx&prodchannel=unknown&prodversion=81.0.4044.138&acceptformat=crx2,crx3&x=id%3D" + ext_id + "%26uc"
    print("Download URL: " + dl_url)

    try:
        urllib.request.urlretrieve(dl_url, save_path)
        core.updatelog("Extension downloaded successfully: " + save_path)
        return save_name
    except Exception as e:
        core.updatelog("Error in downloader.py")
        print(e)
        return False

def downloadFirefox(url):
    if 'addons.mozilla.org' not in url:
        core.updatelog('Invalid Firefox addon URL')
        return False
    else:
        try:
            test = urllib.request.Request(url)
            test.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0')
            source = urllib.request.urlopen(test)
            source_code = source.read().decode('utf-8')
            xpi_file = re.findall('<a class="Button Button--action AMInstallButton-button Button--puffy" href="(.*?).xpi?', source_code)[0]
            core.updatelog('Found link for xpi file: ' + xpi_file + '.xpi')
            name = xpi_file.split('/')[-1]
            xpi_file += '.xpi'
            save_path = helper.fixpath(core.lab_path + '/' + name + '.xpi')
            core.updatelog("Downloader says: save_path is " + save_path)
            try:
                urllib.request.urlretrieve(xpi_file, save_path)
                core.updatelog("Extension downloaded successfully: " + save_path)
                return name
            except Exception as e:
                core.updatelog("Error while downloading xpi file: " + xpi_file)
                print(e)
                return False
        except Exception:
            core.updatelog('Something went wrong while getting download link for xpi file')

def downloadEdge(url):
    if 'microsoftedge.microsoft.com' not in url:
        core.updatelog('Invalid Edge addon URL')
        return False
    ext_id = url.split('/')[-1]
    save_path = helper.fixpath(core.lab_path + '/' + ext_id + '.crx')
    core.updatelog("Downloader says: save_path is " + save_path)
    dl_url = "https://edge.microsoft.com/extensionwebstorebase/v1/crx?response=redirect&x=id%3D" + ext_id + "%26installsource%3Dondemand%26uc"
    print("Download URL: " + dl_url)

    try:
        urllib.request.urlretrieve(dl_url, save_path)
        core.updatelog("Extension downloaded successfully: " + save_path)
        return ext_id
    except Exception as e:
        core.updatelog("Error in downloader.py")
        print(e)
        return False