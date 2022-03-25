from functions.files import *
import re


def edit_storage_html():
    # get list of files in files directory
    filelist = get_file_list('files')
    # edit storage.html
    htmlFS = open('html' + '/storage.html')
    content = htmlFS.read()
    htmlFS.close()
    # find ul in storage.html with finding ul pattern
    pattern = re.compile(r"\<ul[^\>]*\>\s*\<\/ul\>")
    # replace it with mad html
    html = "<ul>"
    for i in filelist:
        list_element = f"<li>{i}</li>"
        html+=list_element
    html+="</ul>"
    result = pattern.sub(html, content)
    return result

def edit_user_storage_html(user):
    # get list of files in files directory
    filelist = get_file_list(f'files/{user}')
    # edit storage.html
    htmlFS = open('html' + '/storage.html')
    content = htmlFS.read()
    htmlFS.close()
    # find ul in storage.html with finding ul pattern
    pattern = re.compile(r"\<ul[^\>]*\>\s*\<\/ul\>")
    # replace it with mad html
    html = "<ul>"
    for i in filelist:
        list_element = f"<li>{i}</li>"
        html+=list_element
    html+="</ul>"
    result = pattern.sub(html, content)
    return result