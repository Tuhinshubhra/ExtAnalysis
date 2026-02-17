import os
import base64
from flask import url_for
import core.core as core
import core.helper as helper

def build_urls_tables(report_data):
    if not report_data['urls']:
        return '<h3 class="nothing"> No URLs Found </h3>', '<h3 class="nothing"> No External JavaScript Found in any files! </h3>', 0, 0
    
    urls_table = '<table class="result-table" id="urls-table"><thead><tr><th>URL</th><th>Domain</th><th>File</th><th>Actions</th></tr></thead><tbody>'
    extjs_table = '<table class="result-table" id="extjs-table"><thead><tr><th>URL</th><th>Domain</th><th>File</th><th>Actions</th></tr></thead><tbody>'
    
    done_urls = []
    done_ejss = []
    urls_count = 0
    extjs_count = 0
    
    for aurl in report_data['urls']:
        b64url = "'" + base64.b64encode(aurl['url'].encode('ascii', 'ignore')).decode('ascii') + "'"
        aurl_href = f'<a href="{aurl["url"]}" class="ext_url" target="_blank"><i class="fas fa-external-link-alt" style="font-size:12px;"></i> {aurl["url"]}</a>'
        actions = f'<td><button class="bttn-fill bttn-xs bttn-primary" onclick=whois(\'{aurl["url"]}\')><i class="fab fa-searchengin"></i> WHOIS</button> <button class="bttn-fill bttn-xs bttn-success" onclick="getSource({b64url})"><i class="fas fa-code"></i> Source</button> <button class="bttn-fill bttn-xs bttn-danger" onclick="getHTTPHeaders({b64url})"><i class="fas fa-stream"></i> HTTP Headers</button></td>'
        
        if aurl['url'].endswith('.js'):
            if aurl['url'] not in done_ejss:
                done_ejss.append(aurl['url'])
                extjs_table += f'<tr><td>{aurl_href}</td><td>{aurl["domain"]}</td><td>{aurl["file"]}</td>{actions}</tr>'
                extjs_count += 1
        else:
            if aurl['url'] not in done_urls:
                done_urls.append(aurl['url'])
                urls_table += f'<tr><td>{aurl_href}</td><td>{aurl["domain"]}</td><td>{aurl["file"]}</td>{actions}</tr>'
                urls_count += 1
    
    urls_table = urls_table + '</tbody></table>' if done_urls else '<h3 class="nothing"> No URLs Found </h3>'
    extjs_table = extjs_table + '</tbody></table>' if done_ejss else '<h3 class="nothing"> No External JavaScript Found in any files! </h3>'
    
    return urls_table, extjs_table, urls_count, extjs_count 