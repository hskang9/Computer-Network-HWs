from functions.files import *
from time import time
import re

def edit_user_storage_html(user):
    # get list of files in files directory
    filelist = get_file_list(f'{user}')
    # edit storage.html
    htmlFS = open('html' + '/storage.html')
    content = htmlFS.read()
    htmlFS.close()

    # replace user1 with received username
    pattern = re.compile(r"user1")
    change_user = pattern.sub(user, content)
    
    # find ul in storage.html with finding ul pattern
    pattern = re.compile(r"\<ul[^\>]*\>\s*\<\/ul\>")
    # replace it with mad html
    html = "<ul>"
    for i in filelist:
        list_element = f"<li>{i} <a href=\"/{user}/{i}\" download><button>Download</button></a> <a href=\"/delete/{user}/{i}\"><button>Delete</button></a> </li>"
        html+=list_element
    html+="</ul>"
    result = pattern.sub(html, change_user)
    return result

def edit_user_cookie_html(user):
    # get list of files in files directory
    filelist = get_file_list(f'{user}')
    # edit storage.html
    htmlFS = open('html' + '/cookie.html')
    content = htmlFS.read()
    htmlFS.close()

    # replace user1 with received username
    pattern = re.compile(r"user1")
    change_user = pattern.sub(user, content)
    
    # find ul in storage.html with finding ul pattern
    pattern = re.compile(r"27")
    cookieFS = open('cookies/' + user)
    content = cookieFS.read()
    cookieFS.close()
   
    # replace time in html
    result = pattern.sub(str(time() - float(content)), change_user)
    return result