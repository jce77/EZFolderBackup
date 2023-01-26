import shutil
from os.path import exists
try:
    trash_method = 0
    from send2trash import send2trash
except ModuleNotFoundError:
    trash_method = 1
    trash_files_path = ""
    trash_info_path = ""
    from datetime import datetime
    import os
    pass

trash_method = 0  # 0 is send2trash, 1 is my custom unrecommended way that may be less stable to use


def start(using_gui, using_windows):
    if trash_method == 1:
        if using_gui:
            return "If using GUI, send2trash module must be installed using pip"
        if using_windows:
            return "If using windows command-line, send2trash module must be installed using pip"
        print("send2trash module is not installed (its recommended to install it), "
              "using shutil move to trash files instead.")
        # finding trash folders, otherwise ending the program if they are not found
        return find_trash_folder()
    else:
        return "Passed"


def get_all_foldernames(path):
    return [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]


def get_trash_folder_inside_path(path):
    folder_names = get_all_foldernames(path)
    for folder in folder_names:
        if os.path.basename(os.path.normpath(folder)) == "Trash":
            return folder
    return -1


def find_trash_folder():
    """ Finds the trash folder on a linux system only """

    # region 1. Finding path to the trash folder
    path_to_trash = -1
    iter = 0
    if exists("/home/.local/share/Trash/"):
        path_to_trash = "/home/.local/share/Trash/"
    while type(path_to_trash) == type(int):
        if iter == 0:
            path_to_trash = get_trash_folder_inside_path("/home/.local/share/Trash/")
        elif iter == 1:
            path_to_trash = get_trash_folder_inside_path("/home/.local/share/")
        elif iter == 2:
            path_to_trash = get_trash_folder_inside_path("/home/.local/")
        elif iter == 3:
            path_to_trash = get_trash_folder_inside_path("/home/")
        elif iter == 4:
            path_to_trash = get_trash_folder_inside_path("/")
        else:
            return "TRASH FOLDER NOT FOUND"
        iter += 1

    # endregion

    # region 2. Getting trash sub folders
    global trash_files_path
    global trash_info_path
    trash_files_path = (path_to_trash + "files/").replace("\\", "/")
    trash_info_path = (path_to_trash + "info/").replace("\\", "/")
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
        send2trash(path)
    else:
        # command-line method for a fresh linux install with no modules
        global trash_files_path
        global trash_info_path
        # making the info file
        info_msg = "[Trash Info]\n"
        info_msg += "Path=" + path + "\n"
        current_datetime = datetime.now()
        info_msg += "DeletionDate=" + current_datetime.strftime("%Y-%m-%dT%H:%M:%S")
        with open(trash_info_path, "w") as file:
            file.write(info_msg + ".trashinfo")
            file.close
        # moving the file
        shutil.move(path.replace("\\", "/"), trash_files_path)


def get_filename(full_path):
    """ Returns the filename only without the path """
    return os.path.basename(full_path)
