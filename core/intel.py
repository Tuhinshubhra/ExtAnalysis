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

import re
import core.core as core
import core.helper as helper

def extract(contents, relpath):
    '''
    EXTRACTS THE FOLLOWING:
        -> URL
        -> EMAIL
        -> BTC ADDRESS
        -> IPV4, IPV6 ADDRESSES
        -> BASE64 ENCODED STRINGS

    CONTENTS = FILE CONTENT
    RELPATH = RELATIVE PATH (FOR JSON ENTRY IN RESULT)
    '''

    found_urls = [] # URLS -> (http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?
    found_mail = [] # emails -> ([a-zA-Z0-9\.\-_]+(?:@| ?\[(?:at)\] ?)[a-zA-Z0-9\.\-]+(?:\.| ?\[(?:dot)\] ?)[a-zA-Z]+)
    found_btcs = [] # bitcoin address -> [^a-zA-Z0-9]([13][a-km-zA-HJ-NP-Z1-9]{26,33})[^a-zA-Z0-9]
    found_ipv4 = [] # IPv4 addr -> [^a-zA-Z0-9]([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})[^a-zA-Z0-9]
    found_ipv6 = [] # IPV6 -> (([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))(?=\s|$)
    found_b64s = [] # base64 -> (?:[A-Za-z0-9+/]{4}){2,}(?:[A-Za-z0-9+/]{2}[AEIMQUYcgkosw048]=|[A-Za-z0-9+/][AQgw]==)
    found_cmnt = [] # Comments -> ...

    # Check if the file is css and if ignore css is set to true
    if core.ignore_css and relpath.endswith('.css'):
        # return empty result
        core.updatelog('ignore css set to true... ignoring: ' + relpath)
        result = {
                "urls":found_urls, 
                "mails":found_mail, 
                "ipv4":found_ipv4, 
                "ipv6":found_ipv6, 
                "base64":found_b64s, 
                "btc":found_btcs,
                "comments":found_cmnt
            }
        return result
    
    '''
    EXTRACT URLS FROM JS, HTML, CSS AND JSON FILES
    ''' 
    curls = re.findall('(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?', contents)
    for url in curls:
        urlresult = {"file":relpath, "url":url[0]+'://'+url[1]+url[2]}
        if urlresult not in found_urls:
            found_urls.append(urlresult)

    
    '''
    EXTRACT EMAIL IDs FROM JS, HTML, JSON AND CSS FILES
    '''
    if core.extract_email_addresses:
        cmails = re.findall('([a-zA-Z0-9\.\-_]+(?:@| ?\[(?:at)\] ?)[a-zA-Z0-9\.\-]+(?:\.| ?\[(?:dot)\] ?)[a-zA-Z]+)', contents)
        for mail in cmails:
            mail = mail.replace('[at]', '@').replace('[dot]','.')
            core.updatelog('Found email address: ' + mail)
            mailarray = {"mail":mail, "file":relpath}
            if mailarray not in found_mail:
                found_mail.append(mailarray)


    '''
    EXTRACT BITCOIN ADDRESSES
    '''
    if core.extract_btc_addresses:
        btc_addresses = re.findall('[^a-zA-Z0-9]([13][a-km-zA-HJ-NP-Z1-9]{26,33})[^a-zA-Z0-9]', contents)
        for btc_address in btc_addresses:
            core.updatelog('Found BTC address: ' + btc_address)
            btcarr = {"address":btc_address, "file":relpath}
            if btcarr not in found_btcs:
                found_btcs.append(btcarr)


    '''
    EXTRACT IPV6 ADDRESSES
    '''
    if core.extract_ipv6_addresses:
        ipv6s = re.findall('(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))(?=\s|$)', contents)
        for ipv6 in ipv6s:
            addr = ipv6[0]
            core.updatelog('Found IP v6 Address: ' + addr)
            v6arr = {"address":addr, "file":relpath}
            if v6arr not in found_ipv6:
                found_ipv6.append(v6arr)


    '''
    EXTRACT IPV4 ADDRESSES
    '''
    if core.extract_ipv4_addresses:
        ipv4s = re.findall('[^a-zA-Z0-9]([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})[^a-zA-Z0-9]', contents)
        for ipv4 in ipv4s:
            core.updatelog('Found IP v4 Address: ' + ipv4)
            iparr = {"address":ipv4, "file":relpath}
            if iparr not in found_ipv4:
                found_ipv4.append(iparr)


    '''
    EXTRACT BASE64 ENCODED STRINGS
    '''
    if core.extract_base64_strings:
        base64_strings = re.findall('(?:[A-Za-z0-9+/]{4}){2,}(?:[A-Za-z0-9+/]{2}[AEIMQUYcgkosw048]=|[A-Za-z0-9+/][AQgw]==)', contents)
        for base64_string in base64_strings:
            core.updatelog('Found base64 encoded string: ' + base64_string)
            stringarr = {"string":base64_string, "file":relpath}
            if stringarr not in found_b64s:
                found_b64s.append(stringarr)


    '''
    EXTRACT COMMENTS FROM JS AND HTML FILES
    '''
    if core.extract_comments:
        if relpath.endswith(('.html', '.js', '.htm', '.css')):
            c1 = re.findall('\/\*.*?\*\/|\/\/(.*?)\n|\$', contents)
            c2 = re.findall('\/\* *([^\"\']+?) *\*\/', contents)
            c3 = re.findall('<!-- *(.+?) *-->', contents)
            c1.extend(c2)
            c1.extend(c3)
            comments = c1
            for comment in comments:
                if comment != "" and comment != " ":
                    comment = helper.escape(comment) # escape html
                    core.updatelog('Extracted comment: ' + comment[:30] + ' ...')
                    cmarray = {"comment":comment, "file":relpath}
                    if cmarray not in found_cmnt:
                        found_cmnt.append(cmarray)
    
    result = {
                "urls":found_urls, 
                "mails":found_mail, 
                "ipv4":found_ipv4, 
                "ipv6":found_ipv6, 
                "base64":found_b64s, 
                "btc":found_btcs,
                "comments":found_cmnt
            }
    return result