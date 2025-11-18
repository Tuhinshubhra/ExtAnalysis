import os
from flask import url_for
import core.core as core

def get_file_type_icon(file_name):
    file_ext = file_name.split('.')[-1]
    file_type = os.path.join(core.path, 'static', 'images', f'{file_ext}1.png')
    
    if os.path.isfile(file_type):
        return url_for('static', filename=f'images/{file_ext}1.png')
    return url_for('static', filename='images/other1.png') 