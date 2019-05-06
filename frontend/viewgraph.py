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
import core.helper as helper
import os
from flask import render_template
import logging, traceback

def view(analysis_id):
    try:
        int(analysis_id.replace('EXA','')) # throws exception if improper id passed
        analysis_info = core.get_result_info(analysis_id)
        
        if not analysis_info[0]:
            # Could not get analysis_info
            error_txt = 'Something went wrong while getting analysis info!<br>Error: ' + analysis_info[1]
            return render_template('error.html', error_title = "Invalid Result ID", error_head = "Invalid Result ID: {0}".format(analysis_id) , error_txt=error_txt)
        
        analysis_path = analysis_info[1]['report_directory'].replace('<reports_path>', core.reports_path)
        
        graph_data = os.path.join(analysis_path, 'graph.data')
        if os.path.isfile(graph_data):
            graph_data = open(graph_data, 'r')
            graph_data = graph_data.read()
            return render_template('graph.html', graph_data = graph_data)
        else:
            return render_template('error.html', error_title = "Missing Graph File", error_head = "Missing Graph File for Result ID: {0}".format(analysis_id) , error_txt='ExtAnalysis could not find "grpah.data" file in the analysis report directory! Please re-analyze the extension') 
    except:
        error_txt = 'There seems to be no result corresponding to the provided ID. Did you delete the result? or maybe you did some weird shit with the parameter?'
        return render_template('error.html', error_title = "Invalid Result ID", error_head = "Invalid Result ID: {0}".format(analysis_id) , error_txt=error_txt) 
