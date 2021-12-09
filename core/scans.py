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

import requests
import core.core as core
import logging, traceback


def geoip(ip):
    '''
    Geo-IP Lookup via ipapi.co
    needed parameter = ip = the ip address
    response = [True/False, JSON_RESULT/ERROR_MSG]
    '''
    core.updatelog('Initiating Geo-IP Lookup for address: ' + ip)
    try:
        lookup_url = 'https://ipapi.co/{0}/json'.format(ip)
        lookup = requests.get(lookup_url)
        lookup = lookup.json()
        try:
            if lookup['error']:
                core.updatelog('Geo-IP Lookup failed: ' + lookup['reason'])
                return [False, lookup['reason']]
        except:
            core.updatelog('Geo-IP Lookup successful')
            return [True, lookup]
    except Exception as e:
        logging.error(traceback.format_exc())
        core.updatelog('Geo-IP Lookup failed: ' + str(e))
        return [False, str(e)]
    

def http_headers(url):
    '''
    HTTP Headers lookup
    needed parameter = url = the url to get the http headers of
    response = [True/False, HEADERS_LIST/ERROR_MSG]
    '''
    core.updatelog('Getting HTTP Headers of: ' + url)
    try:
        req = requests.get(url)
        headers = req.headers
        core.updatelog('HTTP Headers successfully acquired!')
        return [True, headers]
    except Exception as e:
        core.updatelog('Error while getting HTTP Headers of {0}! Error: {1}'.format(url, str(e)))
        logging.error(traceback.format_exc())
        return [False, str(e)]

def source_code(url):
    '''
    GET Source Code
    needed parameter = url = the url to get the source code of
    response = [True/False, SOURCE_CODE/ERROR_MSG]
    '''
    core.updatelog('Getting Source code of: ' + url)
    try:
        req = requests.get(url)
        headers = req.text
        core.updatelog('Source code successfully acquired!')
        return [True, headers]
    except Exception as e:
        core.updatelog('Error while getting Source code of {0}! Error: {1}'.format(url, str(e)))
        logging.error(traceback.format_exc())
        return [False, str(e)]