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
import core.scans as scan
import core.core as core
import base64
import logging, traceback
from flask import render_template, url_for

def view(url):
    try:
        decoded_url = base64.b64decode(url).decode('ascii')
        scstat = scan.source_code(decoded_url)
        if scstat[0]:
            # Successful 
            source_code = scstat[1]
            icon_url = url_for('static',filename='images/url1.png')
            url_icon = '<img src="' + icon_url + '">'
            return render_template('sourcecode.html', 
                                    source_code = source_code,
                                    url_icon = url_icon,
                                    target_url = decoded_url
                                )
        else:
            return render_template('error.html', error_title = "Error Encountered!", error_head = "Error getting source code!" , error_txt='Something went wrong while getting source code of the given url!<br>Error: ' + scstat[1])

    except:
        logging.error(traceback.format_exc())
        return render_template('error.html', error_title = "Error Encountered!", error_head = "Invalid URL Parameter" , error_txt='Something went wrong while decoding url!')

