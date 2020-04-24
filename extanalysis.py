#!/usr/bin/python3
# -*- coding: utf-8 -*-

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
import logging
import traceback
import argparse
import webbrowser
from flask import Flask, request, render_template, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import core.core as core
import core.analyze as analysis
import core.helper as helper
import core.settings as settings
from flask_wtf.csrf import CSRFProtect

parser = argparse.ArgumentParser(prog='extanalysis.py', add_help=False)
parser.add_argument('-h', '--host', help='Host to run ExtAnalysis on. Default host is 127.0.0.1')
parser.add_argument('-p', '--port', help='Port to run ExtAnalysis on. Default port is 13337')
parser.add_argument('-v', '--version', action='store_true', help='Shows version and quits')
parser.add_argument('-u', '--update', action='store_true', help='Checks for update')
parser.add_argument('-q', '--quiet', action='store_true', help='Quiet mode shows only errors on cli!')
parser.add_argument('-n', '--nobrowser', action='store_true', help='Skips launching a web browser')
parser.add_argument('--help', action='store_true', help='Shows this help menu and exits')
args = parser.parse_args()

allowed_extension = set(['crx', 'zip', 'xpi'])
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Set host and port
if args.host is not None:
    host = args.host
else:
    host = '127.0.0.1'

if args.port is not None:
    port = int(args.port)
else:
    port = 13337

# enable Quiet mode
if args.quiet:
    core.quiet = True

# help
if args.help:
    parser.print_help()
    parser.exit()

# version
if args.version:
    # core.print_logo()
    print('ExtAnalysis Version: ' + core.version)
    exit()

if args.update:
    import core.updater as updater

    updater.check()


# core.updatelog('Initiating settings...')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extension


csrf = CSRFProtect()
app = Flask('ExtAnalysis - Browser Extension Analysis Toolkit')
app.config['UPLOAD_FOLDER'] = core.lab_path
app.secret_key = str(os.urandom(24))
csrf.init_app(app)


@app.errorhandler(404)
def page_not_found(e):
    error_txt = 'The page you are trying to browse does not exist... Please click on the logo to go back to homepage.'
    return render_template('error.html', error_title="Error 404 - Page Not Found!",
                           error_head="The page you are looking for is kinda imaginary!", error_txt=error_txt), 404


@app.errorhandler(500)
def internal_error(e):
    error_txt = 'Welp! There\'s no good way of telling this but something has gone terribly wrong with the program!'
    return render_template('error.html', error_title="Error 500 - Internal Server Error!",
                           error_head="Something seriously went wrong... ", error_txt=error_txt), 500


@app.route("/")
def home():
    core.updatelog('Accessed Main page')
    lic = open(helper.fixpath(core.path + '/LICENSE'), 'r')
    license_text = lic.read()
    cred = open(helper.fixpath(core.path + '/CREDITS'), 'r')
    credits_text = cred.read()
    sett = open(core.settings_file, 'r')
    settings_json = sett.read()
    return render_template("index.html",
                           report_dir=core.reports_path,
                           lab_dir=core.lab_path,
                           license_text=license_text,
                           credits_text=credits_text,
                           virustotal_api=core.virustotal_api,
                           settings_json=settings_json
                           )


@app.route('/upload/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return ('error: No File uploaded')
        file = request.files['file']
        if file.filename == '':
            return ('error: Empty File!')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            core.updatelog('File Uploaded.. Filename: ' + filename)
            # saveas = filename.split('.')[0]
            anls = analysis.analyze(filename)
            return (anls)
        else:
            return (
                'error: Invalid file format! only .crx files allowed. If you\'re trying to upload zip file rename it to crx instead')


@app.route("/api/", methods=["POST"])
def api():
    if request.method == 'POST':
        # query = request.args.get('query')
        query = request.form['query']
        import frontend.api as processapi
        return (processapi.view(query, request.args))


@app.route("/log/")
def updatelogs():
    return (core.log)


@app.route('/view-graph/<analysis_id>')
def large_graph(analysis_id):
    import frontend.viewgraph as viewgraph
    return (viewgraph.view(analysis_id))


@app.route('/view-source/<analysis_id>/<file_id>')
def view_source(analysis_id, file_id):
    import frontend.viewfile as viewfile
    return (viewfile.view(analysis_id, file_id))


@app.route('/source-code/<url>')
def source_code(url):
    import frontend.viewsource as vs
    return (vs.view(url))


@app.route('/analysis/<analysis_id>')
def show_analysis(analysis_id):
    import frontend.viewresult as viewResult
    return (viewResult.view(analysis_id))


if __name__ == "__main__":
    core.print_logo()
    settings.init_settings()
    main_url = 'http://{0}:{1}'.format(host, port)
    if args.nobrowser is not True:
        webbrowser.open(main_url)
    print('\n[~] Starting ExtAnalysis at: {0} \n\n'.format(main_url))
    app.run(host=host, port=port, debug=False)
