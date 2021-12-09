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

import core.core as core
import core.helper as helper
import logging,traceback
def get_country(ip):
    '''
    Gets Country and country code from given IP.
    Parameters = ip = ip address for lookup
    Response = [True, {country_code}, {country_name}] or [False, {ERR_MSG}]
    Needs maxminddb for fast performance
    '''
    core.updatelog('Getting country from IP: ' + ip)
    try:
        # If maxminddb module is installed we don't have to query online services to get the country code hence saving a lot of time
        import maxminddb
        try:
            core.updatelog('Getting country from local DB')
            reader = maxminddb.open_database(helper.fixpath(core.path + '/db/geoip.mmdb'))
            ip_info = reader.get(ip)
            iso_code = ip_info['country']['iso_code'].lower()
            country = ip_info['country']['names']['en']
            return [True, iso_code, country]
        except Exception as e:
            core.updatelog('Something went wrong while getting country from ip {0}! Error: {1}'.format(ip, str(e)))
            logging.error(traceback.format_exc())
            return [False, str(e)]
    except:
        core.updatelog('maxminddb module not installed! Using online service to get Country from IP')
        core.updatelog('To save time in future analysis; install maxminddb by: pip3 install maxminddb')
        import core.scans as scan
        gip = scan.geoip(ip)
        if gip[0]:
           geoip = gip[1]
           return [True, geoip['country'].lower(), geoip['country_name']] 
        else:
            return [False, gip[1]]

