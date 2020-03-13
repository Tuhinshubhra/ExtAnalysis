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

import core.core as core
import requests
import random
import time
import logging, traceback

pub_vt = []
## add extra virustotal apis if you have any! helps in faster scan. format: pub_vt = ['api1', 'api2']


virustotal_api = core.virustotal_api

def scan_url(url):
    # Scan the url
    global pub_vt, virustotal_api
    if virustotal_api == "":
        # get a random virustotal api
        virustotal_api = random.choice(pub_vt)
        core.updatelog('Using api: ' + virustotal_api)
    vturl = 'https://www.virustotal.com/vtapi/v2/url/scan'
    params = {'apikey': virustotal_api, 'url':url}
    response = requests.post(vturl, data=params)
    response = response.json()
    if response['response_code'] == 1:
        core.updatelog('URL queued for scan! getting report after 10 seconds...')
        time.sleep(10)
        newurl = 'https://www.virustotal.com/vtapi/v2/url/report'
        newparams = {'apikey': virustotal_api, 'resource':url}
        newresponse = requests.get(newurl, params=newparams)
        finalresp = newresponse.json()
        if finalresp['response_code'] == 1:
            print('{0}/{1} - {2}'.format(finalresp['positives'], finalresp['total'], finalresp['permalink']))
        else:
            return [False, 'Reached maximum rate limit for virustotal api! If you are using your own key, please wait a minute and try again']
    else:
        return [False, 'Reached maximum rate limit for virustotal api! If you are using your own key, please wait a minute and try again']


def scan_domain(domain):
    global pub_vt
    # get a random virustotal api
    tvirustotal_api = random.choice(pub_vt)
    core.updatelog('Using api: ' + tvirustotal_api)
    try:
        url = 'https://www.virustotal.com/vtapi/v2/domain/report'
        params = {'apikey':tvirustotal_api,'domain':domain}
        response = requests.get(url, params=params)
        response = response.json()
        if response['response_code'] == 1:
            return [True, response]
        else:
            return [False, 'Either rate limited or something else went wrong while getting domain report from virustotal']
    except Exception as e:
        logging.error(traceback.format_exc())
        return [False, str(e)]


def domain_batch_scan(domains):
    # used only when there is only one virustotal api and the pub_vt list is empty
    batch_result = {}
    total_domains = len(domains)

    if total_domains > 4:
        # virustotal has limitation of 4 scans per minute for an api so if the domain count is less then 4 we have nothing to wait
        gotta_wait = True
    else:
        gotta_wait = False

    if core.virustotal_api != "":
        # Do batch scan
        for index,domain in enumerate(domains):
            real_index = index + 1
            if gotta_wait and real_index%4 == 0:
                core.updatelog('Sleeping for 1 minute... virustotal api limit reached!')
                # Sleep for 60 seconds.. I really hate it but it seems there's no other way around other then you adding a bunch of diff apis to the above list
                time.sleep(60)
            core.updatelog('Getting virustotal report for: ' + domain)
            try:
                url = 'https://www.virustotal.com/vtapi/v2/domain/report'
                params = {'apikey':core.virustotal_api,'domain':domain}
                response = requests.get(url, params=params)
                response = response.json()
                if response['response_code'] == 1:
                    batch_result[domain] = [True, response]
                else:
                    batch_result[domain] = [False, {"error":"Either rate limited or something else went wrong while getting domain report from virustotal"}]
            except Exception as e:
                logging.error(traceback.format_exc())
                batch_result[domain] = [False, str(e)]
    else:
        for _domain in domains:
            core.updatelog('Skipping virustotal domain scan for {0}. Reason: No virustotal api added!'.format(_domain))
            batch_result[_domain] = [False, "No virustotal api found"]

    return batch_result
