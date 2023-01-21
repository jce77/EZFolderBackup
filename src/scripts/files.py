import shutil
from os.path import exists
from scripts import ui
from scripts import logging
import os
import datetime

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


def get_file_size(path):
    return os.path.getsize(path)


def get_filename(full_path):
    """ Returns the filename only without the path """
    return os.path.basename(full_path)


def path_to_file(full_path):
    """ Returns path without file name """
    return full_path[0:len(full_path) - len(get_filename(full_path))]


class NewFile:
    """ A file that needs to be added to a location, either copied or moved """

    def __init__(self, filename, source_path, target_path, size, date):
        self.filename = filename
        self.source_path = source_path
        self.target_path = target_path
        self.size = size
        self.date = date


class DelFile:
    """ A file to be removed from the target_path, either deleted or moved """

    def __init__(self, filename, target_path, size, date):
        self.filename = filename
        self.target_path = target_path
        self.size = size
        self.date = date


def get_date(path):
    return datetime.datetime.fromtimestamp(os.path.getmtime(path))


def copy_from_main_to_backup_directory(use_graphics, window, main_folder, list_of_files_to_backup, backup_directory,
                                       using_windows):
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

    # checking that the target drive has enough space ==============================================
    path = main_folder[0:2]
    total, used, free = shutil.disk_usage(path)
    target_drive_free_space = free // (2 ** 30)

    # settings for window refreshing
    refresh_ticks = 10
    tick_count = 0

    #  getting every new file that needs to be put in this location ================================
    new_files = []
    for file in list_of_files_to_backup:
        # ------ refreshing the window
        tick_count += 1
        if tick_count > refresh_ticks:
            tick_count = 0
            window.refresh()
        # ----------------------------
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
        file_size = get_file_size(main_folder + file)
        debugging = "checking file " + file + " with size " + str(file_size) + "\n"
        for j in range(len(files_in_backup_directory)):
            file_in_backup = files_in_backup_directory[j]
            if not using_windows:
                file_in_backup = file_in_backup.replace("\\", "/")
            backup_file_size = get_file_size(backup_directory + file_in_backup)
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
            backup_location = backup_directory + file
            if not using_windows:
                backup_location = backup_location.replace("\\", "/")
            new_files.append(NewFile(get_filename(main_folder + file), main_folder + file, backup_location, file_size,
                                     get_date(path)))

    #  getting every old file that needs to be removed from its location ================================
    del_files = []
    for i in range(len(files_in_backup_directory)):
        # ------ refreshing the window
        tick_count += 1
        if tick_count > refresh_ticks:
            tick_count = 0
            window.refresh()
        # ----------------------------
        # print("checking " + str(files_in_backup_directory[i]))
        file_in_backup = files_in_backup_directory[i]
        # continue if this file exists in the main directory
        if exists(main_folder + file_in_backup):
            continue
        # print("found a file to delete: " + backup_directory)
        del_files.append(DelFile(get_filename(backup_directory + file_in_backup), backup_directory + file_in_backup,
                                 get_file_size(backup_directory + file_in_backup),
                                 get_date(backup_directory + file_in_backup)))

    #  DOING MOVE OPERATIONS ==================================================================================
    # iterating backwards since things need to be deleted from new_files and del_files possibly
    for i in range(len(new_files) - 1, -1, -1):
        # ------ refreshing the window
        tick_count += 1
        if tick_count > refresh_ticks:
            tick_count = 0
            window.refresh()
        # ----------------------------
        for j in range(len(del_files) - 1, -1, -1):
            # print("1. comparing " + new_files[i].filename + " and " + del_files[j].filename)
            # print("2. comparing " + str(new_files[i].size) + " and " + str(del_files[j].size))
            # print("new_files[i].size == del_files[j].size? " + str(new_files[i].size == del_files[j].size))
            # print("new_files[i].filename == del_files[j].filename? " + str(new_files[i].filename == del_files[j].filename))
            if new_files[i].size == del_files[j].size and new_files[i].filename == del_files[j].filename:  # and \
                # new_files[i].date == del_files[j].date:
                # decided not to include date created for this. name and exact amount of bytes hopefully will be
                # good enough
                if using_windows:
                    assure_path_exists(path_to_file(new_files[i].target_path))
                else:
                    assure_path_exists(path_to_file(new_files[i].target_path.replace("\\", "/")))
                # moving a file instead of doing a copy and delete
                if using_windows:
                    shutil.move(del_files[j].target_path, new_files[i].target_path)
                else:
                    shutil.move(del_files[j].target_path.replace("\\", "/"), new_files[i].target_path.replace("\\", "/"))

                # logging the event
                # copy the file over if its not found

                print("  '" + get_filename(new_files[i].target_path) + "' has been moved to " + new_files[i].target_path)
                logging.log_file += "  '" + get_filename(new_files[i].target_path) + \
                                    "' has been moved to " + new_files[i].target_path + "\n"
                backup_location = backup_directory + file
                if use_graphics:
                    window["-ERROR-TEXT-"].update(
                        "Moving file: " + str(ui.format_text_for_gui_display(get_filename(new_files[i].target_path))))
                    window.refresh()
                assure_path_exists(path_to_file(backup_location))
                if using_windows:
                    shutil.copyfile(main_folder + file, backup_location)
                else:
                    shutil.copyfile(main_folder + file, backup_location.replace("\\", "/"))
                # deleting folder if its empty now
                delete_directory_if_empty(del_files[i].target_path)
                # deleting these items from the copy and delete lists, important to do this last
                del new_files[i]
                del del_files[j]

                break

    #  DOING DELETE OPERATIONS ==================================================================================
    for i in range(len(del_files)):
        if using_windows:
            print("  '" + get_filename(del_files[i].target_path) + "' is not in main folder, sending to Recycle Bin")
            logging.log_file += "  '" + get_filename(del_files[i].target_path) +\
                                "' is not in main folder, sending to Recycle Bin\n"
        else:
            print("  '" + get_filename(del_files[i].target_path) + "' is not in main folder, sending to Trash")
            logging.log_file += "  '" + get_filename(del_files[i].target_path) +\
                                "' is not in main folder, sending to Trash\n"
        if use_graphics:
            window["-ERROR-TEXT-"].update(
                "Trashing " + str(ui.format_text_for_gui_display(get_filename(del_files[i].target_path))))
            window.refresh()
            # os.remove(backup_directory + file_in_backup) # old method that fully deletes file instantly
        send2trash(del_files[i].target_path)
        # deleting folder if its empty now
        delete_directory_if_empty(del_files[i].target_path)

    #  DOING COPY OPERATIONS ==================================================================================
    for i in range(len(new_files)):
        # copy the file over if its not found
        print("  '" + get_filename(new_files[i].target_path) + "' not found, copying to this backup directory")
        logging.log_file += "  '" + get_filename(
            file) + "' not found, copying to this backup directory\n"
        if use_graphics:
            window["-ERROR-TEXT-"].update("Copying to " + str(ui.format_text_for_gui_display(get_filename(file))))
            window.refresh()
        assure_path_exists(path_to_file(new_files[i].target_path))
        if using_windows:
            shutil.copyfile(new_files[i].source_path, new_files[i].target_path)
        else:
            shutil.copyfile(new_files[i].source_path.replace("\\", "/"), new_files[i].target_path.replace("\\", "/"))

    # i probably want to change the objects to hold both the file name and directory separately or else it will be a
    # crap ton of extra computations. but i should definitely get some rest now.

    #  doing all deletions ================================================================================
    #  doing all copies ===================================================================================
    print("<<< Backup Successful >>>")
    logging.log_file += "<<< Backup Successful >>>\n\n"

    return "BACKUP SUCCESSFUL"

    '''
    # original stuff ---------------------------
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
            window["-ERROR-TEXT-"].update(
                "Trashing " + str(ui.format_text_for_gui_display(get_filename(file_in_backup))))
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
    '''


def delete_directory_if_empty(file_path):
    # deleting folder if its empty now
    directory_of_this = path_to_file(file_path)
    dir_list = os.listdir(directory_of_this)
    if len(dir_list) == 0:
        print("  Deleting the folder since its empty now")
        logging.log_file += "  Deleting the folder since its empty now\n";
        os.rmdir(directory_of_this)

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
