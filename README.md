


<p align='center'>
  <img src="https://i.imgur.com/iOyxLPf.png" alt="Logo"> <br>
  <a href="https://github.com/Tuhinshubhra/ExtAnalysis/releases/tag/v.1.0.5"><img src="https://img.shields.io/badge/Version-1.0.5-brightgreen.svg?style=style=flat-square" alt="version"></a>
  <img src="https://img.shields.io/badge/OS-Windows%2C%20Linux-blue.svg">
  <a href="https://github.com/Tuhinshubhra/ExtAnalysis/"><img src="https://img.shields.io/badge/python-3-orange.svg?style=style=flat-square" alt="Python Version"></a>
  <a href="https://github.com/Tuhinshubhra/ExtAnalysis/stargazers"><img src="https://img.shields.io/github/stars/Tuhinshubhra/ExtAnalysis.svg" alt="GitHub stars" /></a>
  <a href="https://github.com/Tuhinshubhra/ExtAnalysis/blob/master/LICENSE"><img src="https://img.shields.io/github/license/Tuhinshubhra/ExtAnalysis.svg" alt="GitHub license" /></a>
  <a href="https://twitter.com/r3dhax0r"><img src="https://img.shields.io/twitter/url/https/github.com/Tuhinshubhra/ExtAnalysis.svg?style=social" alt="Twitter" /></a>
</p>
<hr>
<p align='center'>
	<a href="#features-of-extanalysis-">Features</a> • <a href="#how-do-i-install-it">Installation</a> • <a href="#how-do-i-use-it">Use</a> • <a href="#python-modules-used">Modules Used</a> • <a href="#screenshots">Screenshots</a> • <a href="#license-and-credits">License</a>
</p>
<hr>


### With ExtAnalysis you can :

 - Download & Analyze Extensions From:
	 - [Chrome Web Store](https://chrome.google.com)
	 - [Firefox Addons](https://addons.mozilla.org)	 
- Analyze Installed Extensions of:
	- Google Chrome
	- Mozilla Firefox
	- Opera Browser (Coming Soon)	
- Upload and Scan Extensions. Supported formats:
	- .crx
	- .xpi
	- .zip
	
## Features of ExtAnalysis :

- View Basic Informations:
	- Name, Author, Description and Version
- Manifest Viewer
- In depth permission information
- Extract Intels from files which include:
	- URLs and domains
	- IPv6 and IPv4 addresses
	- Bitcoin addresses
	- Email addresses
	- File comments
	- Base64 encoded strings
- View and Edit files. Supported file types:
	- html
	- json
	- JavaScript
	- css
- VirusTotal Scans For:
	- URLs
	- Domains
	- Files 
- RetireJS Vulnerability scan for JavaScript files
- Network graph of all files and URLs
- Reconnaissance tools for extracted URLs:
	- Whois Scan
	- HTTP headers viewer
	- URL Source viewer
	- GEO-IP location
- Some Fun Stuffs that include:
	- Dark Mode 
	- Inbuilt chiptune player (*Jam on to some classic chiptune while ExtAnalysis does the work*)

## How do I install it?
Installing ExtAnalysis is simple! It runs on python3, so make sure `python3` and `python3-pip` are installed and follow these steps:

```
$ git clone https://github.com/Tuhinshubhra/ExtAnalysis
 ```
 ```
$ cd ExtAnalysis
 ```
 ```
$ pip3 install -r requirements.txt
 ```

For proper analysis don't forget to add your virustotal api.


## How do I use it?
Once the installation is done you can jump straight ahead and run ExtAnalysis by running the command:
 **$** `python3 extanalysis.py`
It should automatically launch ExtAnalysis in a new browser window.

For other options check out the help menu **$** `python3 extanalysis.py --help`

```
usage: extanalysis.py [-h HOST] [-p PORT] [-v] [-u] [-q] [--help]

optional arguments:
  -h HOST, --host HOST  Host to run ExtAnalysis on. Default host is 127.0.0.1
  -p PORT, --port PORT  Port to run ExtAnalysis on. Default port is 13337
  -v, --version         Shows version and quits
  -u, --update          Checks for update
  -q, --quiet           Quiet mode shows only errors on cli!
  --help                Shows this help menu and exits
```


## Docker Build

 ```
 $ docker build -t extanalysis .
 ```

## Docker Usage

 ```
 $ docker run --rm -it -p 13337:13337 extanalysis -h 0.0.0.0
 ```


## Python Modules Used:

 - `flask` for the webserver
 - `python-whois` for Whois lookup
 - `maxminddb` for parsing the Geo-IP database
 - `requests` for http headers and source code viewer

## Screenshots
<p align="center">
  <img alt="Main Menu" src="https://i.imgur.com/FcGarWG.png" />
   <!-- img alt="Results" src="https://i.imgur.com/7Dlkz3O.png" /> -->
  <img alt="Results" src="https://i.imgur.com/vIOSDLe.png" />
 </p>

## Contribution
You can contribute to the development of ExtAnalysis by improving some code or even reporting by bugs. 

For any other queries feel free to contact me via twitter: [@r3dhax0r](https://twitter.com/r3dhax0r)

Below is a list of people who contributed to the development of ExtAnalysis (*only pull requests!*)
#### Contributors
WebBreacher

##  License and Credits
ExtAnalysis is licensed under [GNU General Public License v3.0](https://github.com/Tuhinshubhra/ExtAnalysis/blob/master/LICENSE). 
Attribution to all the third-party libraries used can be found in the [CREDITS](https://github.com/Tuhinshubhra/ExtAnalysis/blob/master/CREDITS) file.


<br>
<h4 align="center">Copyright (C) 2019 - 2022 Tuhinshubhra</h4>
