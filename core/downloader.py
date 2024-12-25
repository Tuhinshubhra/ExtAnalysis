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
from urllib.parse import parse_qsl, urlparse, parse_qs


def download(id, name=""):
    ext_id = id
    if name == "":
        save_name = ext_id
    else:
        save_name = name
    save_path = helper.fixpath(core.lab_path + '/' + save_name + '.crx')
    core.updatelog("Downloader says: save_path is " + save_path)
    # dl_url = "https://clients2.google.c{{ngrok}}/om/service/update2/crx?response=redirect&x=id%3D" + ext_id + "%26uc&prodversion=32"
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
            test.add_header(
                'User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0')
            source = urllib.request.urlopen(test)
            source_code = source.read().decode('utf-8')
            xpi_file = re.findall(
                '<a class="Button Button--action AMInstallButton-button Button--puffy" href="(.*?).xpi?', source_code)[0]
            core.updatelog('Found link for xpi file: ' + xpi_file + '.xpi')
            name = xpi_file.split('/')[-1]
            xpi_file += '.xpi'
            save_path = helper.fixpath(core.lab_path + '/' + name + '.xpi')
            core.updatelog("Downloader says: save_path is " + save_path)
            try:
                urllib.request.urlretrieve(xpi_file, save_path)
                core.updatelog(
                    "Extension downloaded successfully: " + save_path)
                return name
            except Exception as e:
                core.updatelog("Error while downloading xpi file: " + xpi_file)
                print(e)
                return False
        except Exception:
            core.updatelog(
                'Something went wrong while getting download link for xpi file')


def downloadEdge(url):
    """
    Download Microsoft Edge extensions from various URL formats.
    Supported formats:
    - /detail/[name]/[id]
    - /detail/[name]/[id]?hl=[locale]
    - ?x=id%3D[id]
    Returns extension ID if successful, False otherwise
    """
    print(f"Processing URL: {url}")

    if 'microsoftedge.microsoft.com' not in url:
        core.updatelog('Invalid Edge addon URL')
        return False

    ext_id = None
    try:
        # Parse the URL
        parsed_url = urlparse(url)

        # Handle the /detail/ format
        if '/detail/' in parsed_url.path:
            # Split the path and get the last segment before any query parameters
            # This handles cases like /detail/histre/cmhjbooiibolkopmdohhnhlnkjikhkmn?hl=en-US
            path_without_query = parsed_url.path.split('?')[0]
            path_parts = [p for p in path_without_query.split('/') if p]
            if len(path_parts) >= 3:
                ext_id = path_parts[-1]
                print(f"Extracted ID from path: {ext_id}")

        # If we still don't have an ID, try query parameters
        if not ext_id and parsed_url.query:
            query_params = dict(parse_qsl(parsed_url.query))
            if 'x' in query_params and 'id%3D' in query_params['x']:
                ext_id = query_params['x'].split('id%3D')[1].split('%')[0]
                print(f"Extracted ID from query: {ext_id}")

        # Final cleaning of the extension ID
        if ext_id:
            # Remove any remaining query parameters or special characters
            ext_id = ext_id.split('?')[0].split('#')[0].strip()
            print(f"Final cleaned extension ID: {ext_id}")
        print(ext_id)
    except Exception as e:
        core.updatelog(f'Error parsing URL: {str(e)}')
        print(f"Error during URL parsing: {str(e)}")
        return False

    if not ext_id:
        core.updatelog('Unable to extract extension ID from URL')
        return False

    # Create save path with clean extension ID
    save_path = helper.fixpath(core.lab_path + '/' + ext_id + '.crx')
    print(f"Save path: {save_path}")
    core.updatelog("Downloader says: save_path is " + save_path)

    # Construct download URL
    dl_url = f"https://edge.microsoft.com/extensionwebstorebase/v1/crx?response=redirect&x=id%3D{ext_id}%26installsource%3Dondemand%26uc"
    print(f"Download URL: {dl_url}")

    try:
        # Attempt to download the extension
        urllib.request.urlretrieve(dl_url, save_path)
        core.updatelog("Extension downloaded successfully: " + save_path)
        return ext_id
    except Exception as e:
        core.updatelog(f"Error downloading extension: {str(e)}")
        print(f"Download error: {str(e)}")
        return False
