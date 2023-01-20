import shutil
from os.path import exists
from scripts import ui
from scripts import logging
import os

from send2trash import send2trash

skip_files = []
skip_folders = []


def backup_file(file_name):
    """ If the file exists its backed up ending with .old """
    if exists(file_name):
        shutil.copyfile(file_name, file_name + '.old')


def get_all_filenames(path):
    """ Returns all filenames inside the given path and its sub-folders """
    global skip_folders
    list_of_files = []
    for dname, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in skip_folders]
        for fname in files:
            list_of_files.append(os.path.join(dname, fname))
    return list_of_files


def get_file_size(first_path, second_path):
    return os.path.getsize(first_path + second_path)


def get_filename(full_path):
    """ Returns the filename only without the path """
    return os.path.basename(full_path)


def path_to_file(full_path):
    """ Returns path without file name """
    return full_path[0:len(full_path) - len(get_filename(full_path))]


def copy_from_main_to_backup_directory(use_graphics, window, main_folder, list_of_files_to_backup, backup_directory, using_windows):
    """ Ensures the input backup_directory is a clone of the main """
    if not using_windows:
        backup_directory = backup_directory.replace("\\", "/")
    if ":" == backup_directory[1:2]:
        if not exists(backup_directory[0:3]):
            if use_graphics:
                window["-ERROR-TEXT-"].update("Drive" + backup_directory[0:3] + " is not connected")
            err_msg = "<<< Drive " + backup_directory[
                                     0:3] + " is not connected, skipping backup for drive: " \
                                            "" + backup_directory + ">>>\n"
            logging.log_file += err_msg
            print(err_msg)
            return "DRIVE " + backup_directory[0:3] + " NOT FOUND"
    print("<<< Backing up files to directory: " + backup_directory + " >>>")
    logging.log_file += "<<< Backing up files to directory: " + backup_directory + " >>>\n"
    files_in_backup_directory = get_all_filenames(backup_directory)
    # formatting names
    files_in_backup_directory = remove_path_to_root_folder_from_each(backup_directory, files_in_backup_directory)
    if use_graphics:
        window_update_count = 0
    for file in list_of_files_to_backup:
        if get_filename(file) in skip_files:
            continue
        if not using_windows:
            file = file.replace("\\", "/")
        if use_graphics:
            window_update_count += 1
            if window_update_count > 5:
                window_update_count = 0
                window.refresh()
        found = False
        file_size = get_file_size(main_folder, file)
        debugging = "checking file " + file + " with size " + str(file_size) + "\n"
        for j in range(len(files_in_backup_directory)):
            file_in_backup = files_in_backup_directory[j]
            if not using_windows:
                file_in_backup = file_in_backup.replace("\\", "/")
            backup_file_size = get_file_size(backup_directory, file_in_backup)
            debugging += "    comparing to " + file_in_backup + " with size " + str(backup_file_size) + "\n"
            if file == file_in_backup and file_size == backup_file_size:
                found = True
                del files_in_backup_directory[j]
                break
        if found:
            debugging += " was already found"
        else:
            debugging += " was not found"
        if not found:
            # copy the file over if its not found
            print("  '" + get_filename(file) + "' not found, copying to this backup directory")
            logging.log_file += "  '" + get_filename(
                file) + "' not found, copying to this backup directory\n"
            backup_location = backup_directory + file
            if use_graphics:
                window["-ERROR-TEXT-"].update("Copying to " + str(ui.format_text_for_gui_display(get_filename(file))))
                window.refresh()
            assure_path_exists(path_to_file(backup_location))
            if using_windows:
                shutil.copyfile(main_folder + file, backup_location)
            else:
                shutil.copyfile(main_folder + file, backup_location.replace("\\", "/"))
    # deleting any files left that do not have a file with a matching name in the main directory
    for i in range(len(files_in_backup_directory)):
        file_in_backup = files_in_backup_directory[i]
        # continue if this file exists in the main directory
        if exists(main_folder + file_in_backup):
            continue
        if using_windows:
            print("  '" + get_filename(file_in_backup) + "' is not in main folder, sending to Recycle Bin")
            logging.log_file += "  '" + get_filename(
                file_in_backup) + "' is not in main folder, sending to Recycle Bin\n"
        else:
            print("  '" + get_filename(file_in_backup) + "' is not in main folder, sending to Trash")
            logging.log_file += "  '" + get_filename(
                file_in_backup) + "' is not in main folder, sending to Trash\n"
        if use_graphics:
            window["-ERROR-TEXT-"].update("Trashing " + str(ui.format_text_for_gui_display(get_filename(file_in_backup))))
            window.refresh()
        # os.remove(backup_directory + file_in_backup) # old method that fully deletes file instantly
        send2trash(backup_directory + file_in_backup)
        # deleting folder if its empty now
        directory_of_this = path_to_file(backup_directory + file_in_backup)
        dir_list = os.listdir(directory_of_this)
        if len(dir_list) == 0:
            print("  Deleting the folder since its empty now")
            logging.log_file += "  Deleting the folder since its empty now\n";
            os.rmdir(directory_of_this)
    print("<<< Backup Successful >>>")
    logging.log_file += "<<< Backup Successful >>>\n\n"
    return "BACKUP SUCCESSFUL"


def assure_path_exists(path):
    """ Assures this path exists, and makes the path if it does not exist """
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
        os.makedirs(dir)


def valid_input_for_backup(values):
    """ Ensures enough information was input to try and do the backup """
    if len(values["-MAIN-FOLDER-"]) > 0 and len(values["-BACKUP1-"]) > 0:
        return True
    else:
        return False


def remove_path_to_root_folder_from_each(path_to_directory, list_of_files):
    """ Removes the path to the backup folder from each filename in the list """
    for i in range(len(list_of_files)):
        list_of_files[i] = list_of_files[i][len(path_to_directory):len(list_of_files[i])]
    return list_of_files


def move_index_in_dict(list, dict_key, moving_upwards):
    """ Moves the key in the dictionary forwards or backwards in the order """
    count = 0
    values = []
    if moving_upwards:  # moving upwards
        for key in list:
            values.append([key, list[key]])
            if key == dict_key:
                # cant move up past 0
                if count == 0:
                    return list
                value_above = values[count - 1]
                values[count - 1] = values[count]
                values[count] = value_above
            count += 1
    else:  # moving downwards
        switch_with_previous = False
        for key in list:
            values.append([key, list[key]])
            if key == dict_key:
                # cant move down past the last value
                if count == (len(list) - 1):
                    return list
                switch_with_previous = True
            elif switch_with_previous:
                value_above = values[count - 1]
                values[count - 1] = values[count]
                values[count] = value_above
                switch_with_previous = False
            count += 1
    new_dict = {}
    for tuple in values:
        new_dict[tuple[0]] = tuple[1]
    return new_dict
