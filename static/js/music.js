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

var music_button = document.getElementById('musicButton')
var button_div = document.getElementById('music_buttons');
var play_button = document.getElementById('play_pause');
var chiptunes = [ '/static/chiptunes/1.mod', 
                  '/static/chiptunes/12th_echo.mod', 
                  '/static/chiptunes/2.xm', 
                  '/static/chiptunes/3.xm', 
                  '/static/chiptunes/hotntotti.mod', 
                  '/static/chiptunes/luxaflex.mod', 
                  '/static/chiptunes/melodilicious05.mod', 
                  '/static/chiptunes/the_no_named.xm', 
                  '/static/chiptunes/zeta_force.xm'
                ]


window['libopenmpt'] = {};
libopenmpt.locateFile = function(filename) {
    return filename;
};


var player;

function init() {
    if (player == undefined) {
        player = new ChiptuneJsPlayer(new ChiptuneJsConfig(-1));
    } else {
        player.stop();
    }
}



function afterLoad(path, buffer) {
    document.querySelectorAll('#pitch,#tempo').forEach(e => e.value = 1);
    player.play(buffer);
}


function toggle_music() {
    var status = music_button.getAttribute('status')
    if (status === 'off') {
        music_button.innerHTML = '<img src="/static/images/cross.svg" style="width:27px;">'
        music_button.setAttribute('status', 'on');
        $('#music_buttons').fadeIn(700);
    } else {
        music_button.setAttribute('status', 'off');
        music_button.innerHTML = '<img src="/static/images/music.svg" style="width:27px;">'
        $('#music_buttons').fadeOut(700);
    }
}

function toggle_play() {
    var music_status = play_button.getAttribute('status');
    if (music_status === 'off') {
        play_button.innerHTML = '<img src="/static/images/pause.svg" style="width:27px;">';
        play_button.setAttribute('status', 'on');
        play();

    } else {
        play_button.innerHTML = '<img src="/static/images/play.svg" style="width:27px;">';
        play_button.setAttribute('status', 'off');
        pause();
    }
}

function change_music(){
    var chiptune = chiptunes[Math.floor(Math.random() * chiptunes.length)];
    if (chiptune === window.current_chiptune){
        change_music();
    } 
    else {
        console.log(`Playing ${chiptune}`);
        window.current_chiptune = chiptune;
        init();
        player.load(chiptune, afterLoad.bind(this, chiptune));
        play_button.innerHTML = '<img src="/static/images/pause.svg" style="width:27px;">';
        play_button.setAttribute('status', 'on');
    }
}

function play() {
    if (window.current_chiptune === undefined){
        // No chosen chiptune so this button works as start
        var chiptune = chiptunes[Math.floor(Math.random() * chiptunes.length)];
        console.log(`Playing ${chiptune}`);
        window.current_chiptune = chiptune;
        init();
        player.load(chiptune, afterLoad.bind(this, chiptune));
    } else {
        player.togglePause();
    }
    
}

function pause() {
    player.togglePause();
}