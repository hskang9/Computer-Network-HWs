from os import listdir, mkdir, getcwd, remove
from os.path import isfile, join, normpath, join
from time import time

def get_file_list(path):
    return listdir(path)

def make_personal_directory(username):
    try:
        # make a dir inside files/ directory
        curr_dir = getcwd()
        result = join(curr_dir, f"{username}")
        print(result)
        mkdir(result, 0o666)
    except FileExistsError:
        print("user directory already exists, moving on")

def save_cookie(user):
    with open(f"cookies/{user}", "wb") as file:
        timestamp = f"{time()}"
        file.write(timestamp.encode())

def delete_file(user, file):
    remove(f"{user}/{file}")