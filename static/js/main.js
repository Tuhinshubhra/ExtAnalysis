/**
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
*/
var scan_container = document.getElementById('scan-container');
var result_container = document.getElementById('result-container');
var update_container = document.getElementById('update-container');
var about_container = document.getElementById('about-container');
var online_scan_container = document.getElementById('online-scan');
var local_scan_container = document.getElementById('local-scan');
var select_scan_contaienr = document.getElementById('select-scan-type');
var upload_container = document.getElementById('upload-extension');
var webstore_container = document.getElementById('webstore');
var upload_button = document.getElementById('upload-instead');
var upload_box = document.getElementById('upload-contaienr');
var logo = document.getElementById('logo');
var loading_div = document.getElementById('loading')
var elements = $('.modal-overlay, .modal');
$('.close-modal').click(function() {
    elements.removeClass('active');
});
var csrftoken = $('meta[name=csrf-token]').attr('content')

document.getElementById('noscript').style.display = 'none';

function showscan() {
    if (scan_container.style.display === 'none'){
        $('#container').fadeOut(300);
        $('#result-container').fadeOut(300);
        $('#update-container').fadeOut(300);
        $('#about-container').fadeOut(300);
        $('#container').fadeIn(600);
        $('#scan-container').fadeIn(600);
    }
}

function showabout() {
    if (about_container.style.display === 'none'){
        $('#container').fadeOut(300);
        $('#result-container').fadeOut(300);
        $('#update-container').fadeOut(300);
        $('#scan-container').fadeOut(300);
        $('#container').fadeIn(600);
        $('#about-container').fadeIn(600);
    }
}

function showresult() {
    if (result_container.style.display === 'none'){
        $('#container').fadeOut(300);
        $('#scan-container').fadeOut(300);
        $('#update-container').fadeOut(300);
        $('#about-container').fadeOut(300);
        $('#container').fadeIn(600);
        $('#result-container').fadeIn(600);
    }
}

function showupdate() {
    if (update_container.style.display === 'none'){
        $('#container').fadeOut(300);
        $('#result-container').fadeOut(300);
        $('#scan-container').fadeOut(300);
        $('#about-container').fadeOut(300);
        $('#container').fadeIn(600);
        $('#update-container').fadeIn(600);
    }
}

function loadOnline(){
    select_scan_contaienr.style.display = 'none';
    online_scan_container.style.display = 'block';
}

function download_and_scan(){
    loading_div.style.display = 'block';
    ext_id = document.getElementById('extension-id').value;
    if (ext_id.match(/chrome\.google\.com/)){
        ext_id = ext_id.split('://')[1].split('/')[4].split('?')[0]
        handle_download(ext_id);
        loading_div.style.display = 'none';
    } else if(ext_id === "" || ext_id === " "){
        swal('Empty Value', 'Extension ID value can\'t be empty!', 'warning');
        loading_div.style.display = 'none';
    } else {
        handle_download(ext_id);
        loading_div.style.display = 'none';
    }
    queryurl = '' + ext_id;

}

function download_and_scan_firefox(){
    ext_id = document.getElementById('firefox-addon').value;
    loading_div.style.display = 'block';
    if (ext_id.match(/addons\.mozilla\.org/)){
        fetch(`/api/?addonurl=${ext_id}`,{
            method: "POST",
            headers: {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", // otherwise $_POST is empty
            "X-CSRFToken": csrftoken
            },
            body: "query=firefoxaddon"
        }).then(response => {
            response.text().then(resptxt => {
                handleresponse(resptxt);
                loading_div.style.display = 'none';
            });
        }).catch(err => {
            swal('Error!', 'Something went wrong! Check logs for more information', 'error');
            loading_div.style.display = 'none';
        });
    } else {
        swal('Invalid URL', 'Please provide a valid firefox add-on URL!', 'warning');
        loading_div.style.display = 'none';
    }
    queryurl = '' + ext_id;

}

function handle_download(id){
    swal({
        text: 'Save Extension as (no need to enter file extension):',
        content: "input",
        button: {
          text: "Download & Analyze",
          closeModal: false,
        },
      })
      .then(name => {
        if (!name) throw null;
        loading_div.style.display = 'block';
        return fetch(`/api/?extid=${id}&savedir=${name}`, {
            method: "POST",
            headers: {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", // otherwise $_POST is empty
            "X-CSRFToken": csrftoken
            },
            body: "query=dlanalysis"
        });
      })
      .then(results => {
        return results.text();
      })
      .then(text => {
        handleresponse(text);
      })
      .catch(err => {
        if (err) {
          swal("Oh noes!", "The AJAX request failed!", "error");
        } else {
          swal.stopLoading();
          swal.close();
        }
      });
}

function handleresponse(response){
    button = document.getElementById('modal-content');
    try { swal.close() } catch {}
    if (response.match(/error: /)){
        var msg = response.split('error:')[1]
        var inner_html = '<center><img src="/static/images/error.png" style="width: 283px; margin: 11px;"><br><h3>' + msg + '</h3>';
        button.innerHTML = inner_html;
        elements.addClass('active');
        loading_div.style.display = 'none';
    } else if (response.match(/Extension analyzed and report saved/)){
        var anal_id = response.split('report saved under ID: ')[1];
        var rep_href = `<a href='/analysis/${anal_id}' target="_blank" class="start_scan"><i class="fas fa-external-link-alt"></i> View Analysis</a>`
        var inner_html = '<center><img src="/static/images/success.png" style="width: 283px; margin: 11px;"><br><h3>' + response + '<br><br>'+rep_href+'</h3>';
        button.innerHTML = inner_html;
        elements.addClass('active');
        loading_div.style.display = 'none';
    } else {
        var inner_html = '<center><img src="/static/images/success.png" style="width: 283px; margin: 11px;"><br><h3>' + response + '</h3>';
        button.innerHTML = inner_html;
        elements.addClass('active');
        loading_div.style.display = 'none';
    }
}

function upload_extension(){
    loading_div.style.display = 'block';
    var formdata = new FormData($('#upload-form')[0]);
    $.ajax({
        url: '/upload/',
        type: 'POST',
        headers: {
            "X-CSRFToken": csrftoken
        },
        data: formdata,
        success:(response)=>{
            handleresponse(response);
            loading_div.style.display = 'none';
        },
        cache: false,
        contentType: false,
        processData: false
    });
}

function result() {
    //path = document.getElementById('result_path').value;
    // checkurl = '/api/?query=results';
    fetch('/api/',{
            method: "POST",
            headers: {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", // otherwise $_POST is empty
            "X-CSRFToken": csrftoken
            },
            body: "query=results"
    }).then((resp) => {
        resp.text().then((txt) => {
            button = document.getElementById('changeme');
            button.innerHTML = txt;
            $('#result-table').DataTable();
        });
    });
    document.getElementById('load_result').innerHTML = '<i class="fas fa-sync-alt"></i> Reload Reports';
}

function loadresult(result) {
    checkurl = '/api/?result=' + result;
    fetch(checkurl, {
            method: "POST",
            headers: {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", // otherwise $_POST is empty
            "X-CSRFToken": csrftoken
            },
            body: "query=showresult"
    }).then((resp) => {
        resp.text().then((txt) => {
            button = document.getElementById('modal-content');
            button.innerHTML = txt;
            elements.addClass('active');
        })
    })
}

var tabs = $('.tabs');
var items = $('.tabs').find('a').length;
var selector = $(".tabs").find(".selector");
var activeItem = tabs.find('.active');
var activeWidth = activeItem.innerWidth();
$(".selector").css({
    "left": activeItem.position.left + "px",
    "width": activeWidth + "px"
});

$(".tabs").on("click", "a", function(e) {
    e.preventDefault();
    $('.tabs a').removeClass("active");
    $(this).addClass('active');
    var activeWidth = $(this).innerWidth();
    var itemPos = $(this).position();
    $(".selector").css({
        "left": itemPos.left + "px",
        "width": activeWidth + "px"
    });
});


function showscantype(){
    select_scan_contaienr.style.display = 'block';
    online_scan_container.style.display = 'none';
    local_scan_container.style.display = 'none';
}



var style = document.getElementById("pageStyle");
function getCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
      var c = ca[i];
      while (c.charAt(0) == ' ') {
        c = c.substring(1);
      }
      if (c.indexOf(name) === 0) {
        return c.substring(name.length, c.length);
      }
    }
    return "";
  }

  function checkCookie() {
    var nightmode = getCookie("lights");
    if (nightmode == "off") {
      lightsOff();
    } else {
      lightsOn();
    }
  }

  function lightsOff() {
    document.cookie = "lights = off;  expires = Fri, 31 Dec 9999 23:59:59 GMT";
    style.setAttribute('href', '/static/css/dark.css');
  }

  function lightsOn() {
    document.cookie = "lights = on;  expires = Fri, 31 Dec 9999 23:59:59 GMT";
    style.setAttribute('href', '/static/css/style.css');
  }

  checkCookie();

  function view_permission(permission){
      if (permission === 'https:'){
          permission = "https://*/*";
      } else if (permission === 'http:'){
        permission = "http://*/*";
      } else if (permission === '*'){
          permission = '*://*/*';
      }

      fetch('/api/?permission=' + permission, {
                method: "POST",
                headers: {
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", // otherwise $_POST is empty
                "X-CSRFToken": csrftoken
                },
                body: "query=permissionInfo"
      }).then((response) => {
          response.text().then((reply) => {swal('', reply, 'info')})
      }).catch(err => {
          swal('Error!', 'Something went wrong!', 'error');
      })
  }

  function viewResult(id){
      result_url = '/analysis/' + id;
      window.open(result_url, target = "_blank")
  }

  function deleteResult(id){
      console.log('delete result ' + id);
      swal({
        title: "Delete Result ID: " + id ,
        text: "Once deleted, you will not be able to recover the result!",
        icon: "warning",
        buttons: true,
        dangerMode: true,
      })
      .then((willDelete) => {
        if (willDelete) {
            loading_div.style.display = 'block';
            fetch('/api/?resultID=' + id, {
                method: "POST",
                headers: {
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", // otherwise $_POST is empty
                "X-CSRFToken": csrftoken
                },
                body: "query=deleteResult"
            }).then(response => {
                response.text().then(resptxt => {
                    if (resptxt === 'success'){
                        swal("Analysis " + id + " has been successfully deleted!", {
                            icon: "success",
                          });
                          result();
                          loading_div.style.display = 'none';
                    } else {
                        swal(resptxt, {
                            icon: "error",
                            title: "error"
                          });
                          loading_div.style.display = 'none';
                    }
                })
            }).catch(err => {
                swal('Something went wrong... Please check log for more information', {
                    icon: "error",
                    title: "error"
                  });
                  loading_div.style.display = 'none';
            });
        } else {
          swal("Result " + id + " was not deleted!");
        }
      });
  }

  function getLocalExtensions(browser){
    local_list = document.getElementById('local-list');
    loading_div.style.display = 'block';
    local_list.style.display = 'none';
    fetch('/api/?browser=' + browser, {
                method: "POST",
                headers: {
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", // otherwise $_POST is empty
                "X-CSRFToken": csrftoken
                },
                body: "query=getlocalextensions"
    }).then((response) => {
        response.text().then((reply) => {
            if (reply.match(/error: /)){
                var msg = reply.split('error: ')[1]
                swal('Error!', msg, 'error');
            } else {
                if (browser === 'googlechrome'){browser_name = 'Google Chrome'} else if (browser === 'firefox'){browser_name = 'Mozilla Firefox'} else {browser_name = browser}
                local_list.innerHTML = "<h3 class='mid_header'>Local " + browser_name + ' Extensions</h3><br>' + reply;
                $('#result-table').DataTable();
            }
            loading_div.style.display = 'none';
            local_list.style.display = 'block';
        })
    }).catch(err => {
        swal('Error!', 'Something went wrong! Check logs for more information', 'error');
        loading_div.style.display = 'none';
        local_list.style.display = 'block';
    });
  }

    function getLocalOperaExtensions(){
        swal("Coming Soon!", "Support for local Opera extensions will be added in an upcoming version... Keep updating for new stuffs and improvements.");
    }

    function analyzeLocalExtension(path, browser){
        loading_div.style.display = 'block';
        fetch('/api/?browser=' + browser + '&path=' + path, {
                method: "POST",
                headers: {
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", // otherwise $_POST is empty
                "X-CSRFToken": csrftoken
                },
                body: "query=analyzelocalextension"
        }).then((response) => {
            response.text().then((reply) => {
                handleresponse(reply);
                loading_div.style.display = 'none';
            })
        }).catch(err => {
            console.log(err)
            swal('Error!', 'Something went wrong! Check logs for more information', 'error');
            loading_div.style.display = 'none';
        });
    }

    function removeAll(){
        swal({
            title: "Delete All Analysis?" ,
            text: "Once deleted, you will not be able to recover the results!",
            icon: "warning",
            buttons: true,
            dangerMode: true,
          })
          .then((willDelete) => {
            if (willDelete) {
                loading_div.style.display = 'block';
                fetch('/api/', {
                    method: "POST",
                    headers: {
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", // otherwise $_POST is empty
                    "X-CSRFToken": csrftoken
                    },
                    body: "query=deleteAll"
                }).then(response => {
                    response.text().then(resptxt => {
                        if (resptxt === 'success'){
                            swal("All the results has successfully been deleted", {
                                icon: "success",
                              });
                              result();
                              loading_div.style.display = 'none';
                        } else {
                            swal(resptxt, {
                                icon: "error",
                                title: "error"
                              });
                              loading_div.style.display = 'none';
                        }
                    })
                }).catch(err => {
                    swal('Something went wrong... Please check log for more information', {
                        icon: "error",
                        title: "error"
                      });
                      loading_div.style.display = 'none';
                });
            } else {
              swal("Info", "Your Analysis Reports Are Safe!", "info");
            }
          });
    }

    function clearLab(){
        swal({
            title: "Clear Lab?" ,
            text: "Once deleted, you will loose all the deleted and extracted extensions! P.S: It doesn't effect your analysis reports.",
            icon: "warning",
            buttons: true,
            dangerMode: true,
          })
          .then((willDelete) => {
            if (willDelete) {
                loading_div.style.display = 'block';
                fetch('/api/', {
                    method: "POST",
                    headers: {
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", // otherwise $_POST is empty
                    "X-CSRFToken": csrftoken
                    },
                    body: "query=clearLab"
                }).then(response => {
                    response.text().then(resptxt => {
                        handleresponse(resptxt);
                    })
                }).catch(err => {
                    swal('Something went wrong... Please check log for more information', {
                        icon: "error",
                        title: "error"
                      });
                      loading_div.style.display = 'none';
                });
            } else {
              console.log('Lab is untouched!')
            }
          });
    }

    function domain_from_url(url) {
        var result
        var match
        if (match = url.match(/^(?:https?:\/\/)?(?:[^@\n]+@)?(?:www\.)?([^:\/\n\?\=]+)/im)) {
            result = match[1]
            if (match = result.match(/^[^\.]+\.(.+\..+)$/)) {
                result = match[1]
            }
        }
        return result
    }

    function whois(url){
        loading_div.style.display = 'block';
        if (url !== '' && url !== ' '){
            domain = domain_from_url(url)
            console.log(domain)
            fetch(`/api/?domain=${domain}`, {
                    method: "POST",
                    headers: {
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", // otherwise $_POST is empty
                    "X-CSRFToken": csrftoken
                    },
                    body: "query=whois"
            }).then(response => {
                response.text().then(resptxt => {
                    button = document.getElementById('modal-content');
                    button.innerHTML = resptxt;
                    elements.addClass('active');
                    loading_div.style.display = 'none';
                });
            }).catch(err => {
                swal('Error!', 'Something went wrong! Check logs for more information', 'error');
                loading_div.style.display = 'none';
            });
        } else {
            swal('Invalid URL', 'Invalid URL!', 'warning');
            loading_div.style.display = 'none';
        }
    }

    function domainvt(url, analysis_id){
        loading_div.style.display = 'block';
        if (url !== '' && url !== ' '){
            fetch(`/api/?domain=${url}&analysis_id=${analysis_id}`, {
                    method: "POST",
                    headers: {
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", // otherwise $_POST is empty
                    "X-CSRFToken": csrftoken
                    },
                    body: "query=vtDomainReport"
            }).then(response => {
                response.text().then(resptxt => {
                    if (resptxt.match(/error: /)) {
                        button = document.getElementById('modal-content');
                        var msg = resptxt.split('error:')[1]
                        var inner_html = '<center><img src="/static/images/error.png" style="width: 283px; margin: 11px;"><br><h3>' + msg + '</h3>';
                        button.innerHTML = inner_html;
                        elements.addClass('active');
                        loading_div.style.display = 'none';
                    } else {
                        button = document.getElementById('modal-content');
                        button.innerHTML = '<center><h4>VirusTotal Results For '+url+'</h4></center><br><div id="vt_info" style="overflow: scroll; max-height:500px; text-align: left;"></div>';
                        var wrp1 = document.getElementById("vt_info");
                        try {
                          var data1 = resptxt;
                          try {
                              var data1 = JSON.parse(resptxt);
                          } catch (e) {}
                          var tree1 = jsonTree.create(data1, wrp1);
                          tree1.expand(function(node) {
                          return node.childNodes.length < 2 || node.label === 'phoneNumbers';
                          });
                          elements.addClass('active');
                          loading_div.style.display = 'none';
                        } catch (e) {
                          handleresponse('error: No valid VirusTotal result found!');
                        }
                    }
                });
            }).catch(err => {
                swal('Error!', 'The api call failed! is ExtAnalysis offline?', 'error');
                loading_div.style.display = 'none';
            });
        } else {
            swal('Error', 'Invalid Domain!', 'warning');
            loading_div.style.display = 'none';
        }
    }

    function clearlogs(x){
        loading_div.style.display = 'block';
        fetch("/api/", {
            method: "POST",
            headers: {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", // otherwise $_POST is empty
            "X-CSRFToken": csrftoken
            },
            body: "query=" + encodeURIComponent(x)
        }).then(response => {
            response.text().then(resptxt => {
                handleresponse(resptxt);
                loading_div.style.display = 'none';
            });
        }).catch(err => {
            swal('Error!', 'Something went wrong! Check logs for more information', 'error');
            loading_div.style.display = 'none';
        });
    }

    function viewfile(analysis_id, file_id){
        var final_url = '/view-source/' + analysis_id + '/' + file_id;
        console.log(analysis_id + ' " ' + file_id)
        window.open(final_url, target = "_blank")
    }

    function changeReportsDir(){
        report_dir = document.getElementById('reports_dir').value
        if (report_dir === "" || report_dir === " "){
            swal(
                'Error!',
                'Invalid/Empty path!',
                'error'
            )
        } else {
            loading_div.style.display = 'block';
            apiurl = '/api/?newpath=' + report_dir;
            fetch(apiurl, {
                    method: "POST",
                    headers: {
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", // otherwise $_POST is empty
                    "X-CSRFToken": csrftoken
                    },
                    body: "query=changeReportsDir"
            }).then(resp => {
                resp.text().then(resptxt => {
                    handleresponse(resptxt);
                    loading_div.style.display = 'none';
                });
            }).catch(err => {
                swal(
                    'Error!',
                    'Something went wrong with the api call! is ExtAnalysis offline?',
                    'warning'
                );
                loading_div.style.display = 'none';
            });
        }
    }

    function changeLabDir(){
        lab_dir = document.getElementById('lab_dir').value
        if (lab_dir === "" || lab_dir === " "){
            swal(
                'Error!',
                'Invalid/Empty path!',
                'error'
            )
        } else {
            loading_div.style.display = 'block';
            apiurl = '/api/?newpath=' + lab_dir;
            fetch(apiurl, {
                    method: "POST",
                    headers: {
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", // otherwise $_POST is empty
                    "X-CSRFToken": csrftoken
                    },
                    body: "query=changelabDir"
            }).then(resp => {
                resp.text().then(resptxt => {
                    handleresponse(resptxt);
                    loading_div.style.display = 'none';
                });
            }).catch(err => {
                swal(
                    'Error!',
                    'Something went wrong with the api call! is ExtAnalysis offline?',
                    'warning'
                );
                loading_div.style.display = 'none';
            });
        }
    }

    function changeVTapi(){
        vt_api = document.getElementById('virustotal_api').value
        if (vt_api === "" || vt_api === " "){
            swal(
                'Error!',
                'Invalid API!',
                'error'
            )
        } else {
            loading_div.style.display = 'block';
            apiurl = '/api/?api=' + vt_api;
            fetch(apiurl, {
                    method: "POST",
                    headers: {
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", // otherwise $_POST is empty
                    "X-CSRFToken": csrftoken
                    },
                    body: "query=changeVTapi"
            }).then(resp => {
                resp.text().then(resptxt => {
                    handleresponse(resptxt);
                    loading_div.style.display = 'none';
                });
            }).catch(err => {
                swal(
                    'Error!',
                    'Something went wrong with the api call! is ExtAnalysis offline?',
                    'warning'
                );
                loading_div.style.display = 'none';
            });
        }
    }


    function geoip(ip){
        loading_div.style.display = 'block';
        if (ip !== '' && ip !== ' '){
            fetch(`/api/?ip=${ip}`, {
                    method: "POST",
                    headers: {
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", // otherwise $_POST is empty
                    "X-CSRFToken": csrftoken
                    },
                    body: "query=geoip"
            }).then(response => {
                response.text().then(resptxt => {
                    button = document.getElementById('modal-content');
                    button.innerHTML = resptxt;
                    elements.addClass('active');
                    loading_div.style.display = 'none';
                });
            }).catch(err => {
                swal('Error!', 'API Call failed! is ExtAnalysis offline?', 'error');
                loading_div.style.display = 'none';
            });
        } else {
            handleresponse('error: Invalid IP Address')
            loading_div.style.display = 'none';
        }
    }

    function retirejsResult(file_id, analysis_id, file_name){
        loading_div.style.display = 'block';
        if (file_id !== '' && file_id !== ' '){
            fetch(`/api/?file=${file_id}&analysis_id=${analysis_id}`, {
                    method: "POST",
                    headers: {
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", // otherwise $_POST is empty
                    "X-CSRFToken": csrftoken
                    },
                    body: "query=retirejsResult"
            }).then(response => {
                response.text().then(resptxt => {
                    if (resptxt.match(/error: /)) {
                        button = document.getElementById('modal-content');
                        var msg = resptxt.split('error:')[1]
                        var inner_html = '<center><img src="/static/images/error.png" style="width: 283px; margin: 11px;"><br><h3>' + msg + '</h3>';
                        button.innerHTML = inner_html;
                        elements.addClass('active');
                        loading_div.style.display = 'none';
                    } else if (resptxt === "none"){
                        /**
                        button = document.getElementById('modal-content');
                        button.innerHTML = '<center><h4>RetireJS Vuln Report for '+file_name+'</h4></center><br><div id="rjs_result" style="overflow: scroll; max-height:500px; text-align: left;">No vulnerabilites found!</div>';
                        elements.addClass('active');
                        loading_div.style.display = 'none';
                         */
                        handleresponse('No vulnerabilities found in <b>' + file_name + '</b>');
                    } else {
                        button = document.getElementById('modal-content');
                        button.innerHTML = '<center><h4>RetireJS Vulnerabily Report for '+file_name+'</h4></center><br><div id="rjs_result" style="overflow: scroll; max-height:500px; text-align: left;"></div>';
                        var wrp1 = document.getElementById("rjs_result");
                        var data1 = resptxt;
                        try {
                            var data1 = JSON.parse(resptxt);
                        } catch (e) {}
                        var tree1 = jsonTree.create(data1, wrp1);
                        tree1.expand(function(node) {
                        return node.childNodes.length < 2 || node.label === 'phoneNumbers';
                        });
                        elements.addClass('active');
                        loading_div.style.display = 'none';
                    }
                });
            }).catch(err => {
                swal('Error!', 'API Call failed! is ExtAnalysis offline?', 'error');
                loading_div.style.display = 'none';
            });
        } else {
            handleresponse('error: Invalid File ID')
            loading_div.style.display = 'none';
        }
    }

    function getHTTPHeaders(url){
        loading_div.style.display = 'block';
        if (url !== '' && url !== ' '){
            fetch(`/api/?url=${url}`, {
                    method: "POST",
                    headers: {
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", // otherwise $_POST is empty
                    "X-CSRFToken": csrftoken
                    },
                    body: "query=HTTPHeaders"
            }).then(response => {
                response.text().then(resptxt => {
                    button = document.getElementById('modal-content');
                    button.innerHTML = resptxt;
                    elements.addClass('active');
                    loading_div.style.display = 'none';
                });
            }).catch(err => {
                swal('Error!', 'API Call failed! is ExtAnalysis offline?', 'error');
                loading_div.style.display = 'none';
            });
        } else {
            handleresponse('error: Invalid url parameter')
            loading_div.style.display = 'none';
        }
    }

    function getSource(url){
        loading_div.style.display = 'block';
        if (url !== '' && url !== ' '){
            fetch(`/api/?url=${url}`, {
                    method: "POST",
                    headers: {
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", // otherwise $_POST is empty
                    "X-CSRFToken": csrftoken
                    },
                    body: "query=SourceCode"
            }).then(response => {
                response.text().then(resptxt => {
                    button = document.getElementById('modal-content');
                    button.innerHTML = resptxt;
                    elements.addClass('active');
                    loading_div.style.display = 'none';
                });
            }).catch(err => {
                swal('Error!', 'API Call failed! is ExtAnalysis offline?', 'error');
                loading_div.style.display = 'none';
            });
        } else {
            handleresponse('error: Invalid url parameter')
            loading_div.style.display = 'none';
        }
    }

    function update(){
        swal('Update Extanalysis', 'Use the command "python3 extanalysis.py --update" to check for updates!', 'info')
    }

    function updateIntelExtraction(){
        // Get all the values
        try{
            var extract_comments = $('#extract_comments')[0].checked
            var extract_btc_addresses = $('#extract_btc_addresses')[0].checked
            var extract_base64_strings = $('#extract_base64_strings')[0].checked
            var extract_email_addresses = $('#extract_email_addresses')[0].checked
            var extract_ipv4_addresses = $('#extract_ipv4_addresses')[0].checked
            var extract_ipv6_addresses = $('#extract_ipv6_addresses')[0].checked
            var ignore_css = $('#ignore_css')[0].checked
            var requrl = `/api/?extract_comments=${extract_comments}&extract_btc_addresses=${extract_btc_addresses}&extract_base64_strings=${extract_base64_strings}&extract_email_addresses=${extract_email_addresses}&extract_ipv4_addresses=${extract_ipv4_addresses}&extract_ipv6_addresses=${extract_ipv6_addresses}&ignore_css=${ignore_css}`
            loading_div.style.display = 'block';
            fetch(requrl, {
                    method: "POST",
                    headers: {
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", // otherwise $_POST is empty
                    "X-CSRFToken": csrftoken
                    },
                    body: "query=updateIntelExtraction"
            }).then(response => {
                response.text().then(resptxt => {
                    handleresponse(resptxt);
                    loading_div.style.display = 'none';
                });
            }).catch(err => {
                swal('Error!', 'API Call failed! is ExtAnalysis offline?', 'error');
                loading_div.style.display = 'none';
            });
        } catch {
            handleresponse('error: Something went wrong while getting settings value');
        }
    }