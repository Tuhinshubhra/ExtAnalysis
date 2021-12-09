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
import json
import core.core as core
import core.helper as helper
import logging, traceback
from flask import render_template, url_for

def view(analysis_id, file_id):
    int(analysis_id.replace('EXA','')) # throws exception if improper id passed
    int(file_id.replace('EXTAF', ''))
    analysis_info = core.get_result_info(analysis_id)
        
    if not analysis_info[0]:
        # Could not get analysis_info
        error_txt = 'Something went wrong while getting analysis info!<br>Error: ' + analysis_info[1]
        return render_template('error.html', error_title = "Invalid Result ID", error_head = "Invalid Result ID: {0}".format(analysis_id) , error_txt=error_txt)
        
    analysis_path = analysis_info[1]['report_directory'].replace('<reports_path>', core.reports_path)
    sources_file = os.path.join(analysis_path, 'source.json')

    if os.path.isfile(sources_file):
        # valid source
        s = open(sources_file, 'r')
        sources = json.loads(s.read())
        try:
            file_info = sources[file_id]
            file_name = file_info['file_name']
            file_location = file_info['location']
            file_type = file_name.split('.')[-1]
            if file_type.endswith(('html', 'htm')):
                file_icon = 'html1.png'
            elif file_type.endswith('js'):
                file_icon = 'js1.png'
            elif file_type.endswith('css'):
                file_icon = 'css1.png'
            elif file_type.endswith(('png', 'jpg', 'jpeg', 'bmp', 'tiff', 'svg')):
                file_icon = 'static1.png'
            elif file_type.endswith('json'):
                file_icon = 'json1.png'
            else:
                file_icon = 'other1.png'
            icon_url = url_for('static',filename='images/' + file_icon)
            file_icon = '<img src="' + icon_url + '">'
            file_type = ('javascript' if file_type == 'js' else file_type)
            try:
                fs = open(file_location, 'r', encoding='utf8')
                file_source = fs.read()
                file_size = str(os.path.getsize(file_location) >> 10) + ' KB'
                return render_template('source.html', file_name = file_name, file_source = file_source, file_id = file_id, file_location = file_location, file_type = file_type, file_size = file_size, file_icon = file_icon)
            except Exception as e:
                logging.error(traceback.format_exc())
                return render_template('error.html', error_title = "Error Accessing File", error_head = "Problem while reading file source!" , error_txt='Something went wrong while reading the file source... error: ' + str(e))

        except:
            return render_template('error.html', error_title = "Invalid File ID", error_head = "Invalid File ID" , error_txt='I could not find any file with the given file id... well either you tempered with the parameter or something went WRONG!')

    else:
        return render_template('error.html', error_title = "Invalid Analysis ID", error_head = "Invalid Analysis ID" , error_txt='There seems to be no result corresponding to the provided ID. Did you delete the result? or maybe you did some weird shit with the parameter?')
