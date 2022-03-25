from os import listdir, mkdir, getcwd
from os.path import isfile, join, normpath, join
from time import time

def get_file_list(path):
    return listdir(path)

def make_personal_directory(username):
    try:
        # make a dir inside files
        curr_dir = getcwd()
        result = join(curr_dir, f"files/{username}")
        print(result)
        mkdir(result, 0o666)
    except FileExistsError:
        print("user directory already exists, moving on")

def save_cookie(user):
    with open(f"cookies/{user}", "wb") as file:
        timestamp = f"Loggined time: {time()}"
        file.write(timestamp.encode())
