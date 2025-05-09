import shutil
from os.path import exists
from scripts import logging
try:
    trash_method = 0
    from send2trash import send2trash
except ModuleNotFoundError:
    send2trash = 0
    trash_method = 1
    trash_files_path = ""
    trash_info_path = ""
    from datetime import datetime
    import os

    pass

trash_method = 0  # 0 is send2trash, 1 is my custom unrecommended way that may be less stable to use


def start(using_gui, using_windows):
    global trash_method
    if type(send2trash) == int:
        trash_method = 1
        if using_gui:
            return "If using GUI, send2trash module must be installed using pip"
        if using_windows:
            return "If using windows command-line, send2trash module must be installed using pip"
        print("send2trash module is not installed (its recommended to install it), "
              "using shutil move to trash files instead.")
        # finding trash folders, otherwise ending the program if they are not found
        return find_trash_folder()
    else:
        trash_method = 0
        return "Passed"


def get_all_foldernames(path):
    if exists(path):
        return [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    return []


def get_trash_folders_inside_path(path):
    trash_folders = []  # multiple just in case
    folder_names = get_all_foldernames(path)
    # print("checking folder names")
    for folder in folder_names:
        # print("  " + str(folder))
        if os.path.basename(os.path.normpath(folder)) == "Trash":
            trash_folders.append()
    return trash_folders


def find_trash_folder():
    """ Finds the trash folder on a linux system only """

    # region 1. Finding path to the trash folder
    path_to_trash = -1
    if exists("/home/" + os.getlogin() + "/.local/share/Trash/"):
        path_to_trash = "/home/" + os.getlogin() + "/.local/share/Trash/"
    else:
        trash_folders = get_trash_folders_inside_path("/home/")
        if len(trash_folders) == 1:
            path_to_trash = trash_folders[0]
        else:
            # checking which folder has share in the path
            for folder in trash_folders:
                folders_in_path = folder.split("/")
                if folders_in_path[len(folders_in_path) - 2] == "share":
                    path_to_trash = folder
    if path_to_trash == -1:
        print("Error, trash folder not found in /Home/ directory")
        return "Failed"

    # endregion

    # region 2. Getting trash sub folders
    global trash_files_path
    global trash_info_path
    trash_files_path = path_to_trash + "files/"
    trash_files_path = trash_files_path.replace("\\", "/")
    trash_info_path = path_to_trash + "info/"
    trash_info_path = trash_info_path.replace("\\", "/")
    assure_path_exists(trash_files_path)
    assure_path_exists(trash_info_path)
    return "Passed"

    # endregion


def assure_path_exists(path):
    """ Assures this path exists, and makes the path if it does not exist """
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
        os.makedirs(dir)


def trash_file(path):
    """ Moves the file into the recycling/trash folder """
    # Thread that explains how to do this right, making the info file first
    # https://unix.stackexchange.com/questions/672442/how-does-the-trash-directory-work
    global trash_method
    if trash_method == 0:
        try:
            send2trash(path)
        except FileNotFoundError:
            msg = f"ERROR: could not trash file at the path: \n   '{path}'\nThe name contains unrecognized characters that must be removed.\n"
            logging.log_file += msg
            logging.log_error(msg)
            print(msg)
    else:
        # Command-line method for a fresh Linux install with no modules
        global trash_files_path
        global trash_info_path

        # Making the info file
        info_msg = f"[Trash Info]\nPath={path}\nDeletionDate={datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}"
        with open(os.path.join(trash_info_path, os.path.basename(path) + ".trashinfo"), "w") as file:
            file.write(info_msg)

        # Moving the file
        shutil.move(path, trash_files_path)


def get_filename(full_path):
    """ Returns the filename only without the path """
    return os.path.basename(full_path)
