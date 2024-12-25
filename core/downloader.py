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

from pathlib import Path
from typing import Optional
import urllib.request
import core.core as core
import core.helper as helper
import re
from urllib.parse import parse_qsl, urlparse, parse_qs


from pathlib import Path
import urllib.request


import urllib.request
from pathlib import Path
import re
from typing import Optional


class ExtensionDownloader:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        }
        self.lab_path = core.lab_path
        # Use more recent Chrome version as in the JS implementation
        self.chrome_version = "121.0.0.0"
        self.nacl_arch = "x86-64"

    def _download_file(self, url: str, save_path: Path) -> bool:
        """Enhanced download method with additional error handling and retries."""
        try:
            request = urllib.request.Request(url, headers=self.headers)

            # Add error handling for HTTP redirects
            response = urllib.request.urlopen(request)
            while response.geturl() != url:  # Handle redirects explicitly
                url = response.geturl()
                request = urllib.request.Request(url, headers=self.headers)
                response = urllib.request.urlopen(request)

            save_path.write_bytes(response.read())
            core.updatelog(f"Extension downloaded successfully: {save_path}")
            return True

        except urllib.error.HTTPError as e:
            core.updatelog(f"HTTP Error: {e.code} - {e.reason}")
            return False
        except urllib.error.URLError as e:
            core.updatelog(f"URL Error: {str(e.reason)}")
            return False
        except Exception as ex:
            core.updatelog(f"Download failed: {str(ex)}")
            return False

    def _download_extension(self, url: str, save_name: str, extension_type: str) -> Optional[str]:
        """Handles the downloading of both Chrome and Firefox extensions."""
        save_path = Path(self.lab_path) / f"{save_name}.{extension_type}"
        core.updatelog(f"Download URL: {url}")
        if self._download_file(url, save_path):
            return save_name
        return None

    def _extract_edge_id(self, url: str) -> Optional[str]:
        """Extract Edge extension ID from URL."""
        parsed_url = urlparse(url)

        # Try getting ID from path
        if '/detail/' in parsed_url.path:
            path_parts = [p for p in parsed_url.path.split('/') if p]
            if len(path_parts) >= 3:
                return path_parts[-1].split('?')[0]

        # Try getting ID from query parameters
        if parsed_url.query:
            query_params = dict(parse_qsl(parsed_url.query))
            if 'x' in query_params and 'id%3D' in query_params['x']:
                return query_params['x'].split('id%3D')[1].split('%')[0]

        return None

    def download_chrome(self, ext_id: str, name: Optional[str] = None) -> Optional[str]:
        """Download Chrome extension using the updated URL format.

        Args:
            ext_id: The Chrome extension ID
            name: Optional name for the saved file

        Returns:
            The name of the saved file if successful, None otherwise
        """
        save_name = name if name else ext_id

        # Using the URL format from the working JavaScript implementation
        dl_url = (
            "https://clients2.google.com/service/update2/crx?"
            "response=redirect&"
            f"prodversion={self.chrome_version}&"
            "x=id%3D" + ext_id + "%26installsource%3Dondemand%26uc&"
            f"nacl_arch={self.nacl_arch}&"
            "acceptformat=crx2,crx3"
        )

        return self._download_extension(dl_url, save_name, 'crx')

    def download_firefox(self, url: str) -> Optional[str]:
        """Download Firefox extension."""
        if 'addons.mozilla.org' not in url:
            core.updatelog('Invalid Firefox addon URL')
            return None
        try:
            request = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(request) as response:
                source_code = response.read().decode('utf-8')

            xpi_matches = re.findall(
                r'<a class="Button Button--action AMInstallButton-button Button--puffy" href="(.*?).xpi?',
                source_code
            )

            if not xpi_matches:
                core.updatelog('Could not find XPI download link')
                return None

            xpi_file = f"{xpi_matches[0]}.xpi"
            name = xpi_file.split('/')[-1]

            core.updatelog(f"Found XPI file: {xpi_file}")
            return self._download_extension(xpi_file, name, 'xpi')

        except Exception as ex:
            core.updatelog(f"Error processing Firefox addon: {str(ex)}")
            return None

    def download_edge(self, url: str) -> Optional[str]:
        """Download Microsoft Edge extension."""
        if 'microsoftedge.microsoft.com' not in url:
            core.updatelog('Invalid Edge addon URL')
            return None

        try:
            ext_id = self._extract_edge_id(url)
            if not ext_id:
                core.updatelog('Could not extract Edge extension ID')
                return None
            dl_url = (
                "https://edge.microsoft.com/extensionwebstorebase/v1/crx?"
                f"response=redirect&x=id%3D{ext_id}%26installsource%3Dondemand%26uc"
            )

            core.updatelog(f"Download URL: {dl_url}")
            return ext_id if self._download_extension(dl_url, ext_id, "crx") else None

        except Exception as e:
            core.updatelog(f'Error downloading Edge extension: {str(e)}')
            return None


if __name__ == "___main__":
    downloader = ExtensionDownloader()
    result = downloader.download_chrome("epbpdmalnhhoggbcckpffgacohbmpapb")
    if result:
        print(f"Successfully downloaded extension: {result}")
    else:
        print("Download failed")
