# region 1. Imports and Variables
import shutil
import threading
from os.path import exists
from scripts import ui
from scripts import logging
import os
import datetime
from scripts import trash
import sys

delete_files = False  # if true, files will be recycled/trashed in backup folders when no longer existing in main folder
skip_files = []
skip_folders = []
busy = False  # waiting for a process to be completed


# endregion

# region 2. Data Types
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


# endregion

# region 3. Backup Function
def copy_from_main_to_backup_directory(use_graphics, window, main_folder, list_of_files_to_backup, backup_directory,
                                       using_windows):
    """ Ensures the input backup_directory is a clone of the main """
    progress_count = 0
    files_to_process = 0

    if use_graphics:
        window["-BAR-"].update(0)
        ui.set_loading_bar_visible(window, True)
        window["-ERROR-TEXT-"].update("Calculating backup... ")
        window.refresh()
    if not using_windows:
        backup_directory = backup_directory.replace("\\", "/")
    if ":" == backup_directory[1:2]:
        if not exists(backup_directory[0:3]):
            if use_graphics:
                window["-ERROR-TEXT-"].update("Drive" + backup_directory[0:3] + " is not connected")
                window.refresh()
            err_msg = "<<< Drive " + backup_directory[
                                     0:3] + " is not connected, skipping backup for drive: " \
                                            "" + backup_directory + ">>>\n"
            logging.log_file += err_msg
            print(err_msg)
            ui.set_loading_bar_visible(window, False)
            return "DRIVE " + backup_directory[0:3] + " NOT FOUND"
    print("<<< Backing up files to directory: " + backup_directory + " >>>")
    logging.log_file += "<<< Backing up files to directory: " + backup_directory + " >>>\n"
    files_in_backup_directory = get_all_filenames(backup_directory)
    # formatting names
    files_in_backup_directory = remove_path_to_root_folder_from_each(backup_directory, files_in_backup_directory)

    # region 1. Getting free space left on this drive ==============================================
    path = 0
    if using_windows:
        path = main_folder[0:2]
    else:
        slash_count = 0
        for i in range(len(main_folder)):
            if main_folder[i] == "/" or main_folder[i] == "\\":
                slash_count += 1
            if slash_count == 2:
                path = main_folder[0:i + 1]

    total, used, free = shutil.disk_usage(path)
    target_drive_free_space = free
    new_space_used = 0  # the new space being used by operations
    # print("target_drive_free_space=" + str(target_drive_free_space // (2 ** 30)) + "GB")

    # settings for window refreshing
    refresh_ticks = 10
    tick_count = 0
    # endregion

    # region 2. Getting every new file that needs to be put in this location ================================
    new_files = []
    for file in list_of_files_to_backup:
        if get_filename(file) in skip_files:
            print("skipping file: " + get_filename(file))
            continue
        if not using_windows:
            file = file.replace("\\", "/")
        found = False
        file_size = get_file_size(main_folder + file)
        # debugging = "checking file " + file + " with size " + str(file_size) + "\n"
        # print(str(len(list_of_files_to_backup)) + " files to compare")
        for j in range(len(files_in_backup_directory)):
            file_in_backup = files_in_backup_directory[j]
            if not using_windows:
                file_in_backup = file_in_backup.replace("\\", "/")
            backup_file_size = get_file_size(backup_directory + file_in_backup)
            # debugging += "    comparing to " + file_in_backup + " with size " + str(backup_file_size) + "\n"
            if file == file_in_backup and file_size == backup_file_size:
                found = True
                del files_in_backup_directory[j]
                break
        # if found:
        #     debugging += " was already found"
        #     print(debugging)
        # else:
        #     debugging += " was not found"
        #     print(debugging)
        if not found:
            backup_location = backup_directory + file
            if not using_windows:
                backup_location = backup_location.replace("\\", "/")
            new_files.append(NewFile(get_filename(main_folder + file), main_folder + file, backup_location, file_size,
                                     get_date(path)))

    # ------ refreshing the window and checking for events
    if use_graphics:
        # do event check here
        event, values = window.read(timeout=0)
        # if any input event in detected, open window to ask about cancelling
        if event != '__TIMEOUT__':
            if ui.question_box("Cancel backup operation?\n", 80, 15):
                ui.set_loading_bar_visible(window, False)
                return "BACKUP CANCELLED"
    # -----------------------------------------------------
    # endregion

    # region 3. Getting every old file that needs to be removed from its location ================================
    del_files = []
    for i in range(len(files_in_backup_directory)):
        # print("checking " + str(files_in_backup_directory[i]))
        file_in_backup = files_in_backup_directory[i]
        # continue if this file exists in the main directory
        if exists(main_folder + file_in_backup):
            continue
        # print("found a file to delete: " + backup_directory)
        del_files.append(DelFile(get_filename(backup_directory + file_in_backup), backup_directory + file_in_backup,
                                 get_file_size(backup_directory + file_in_backup),
                                 get_date(backup_directory + file_in_backup)))

    # ------ refreshing the window and checking for events
    if use_graphics:
        # do event check here
        event, values = window.read(timeout=0)
        # if any input event in detected, open window to ask about cancelling
        if event != '__TIMEOUT__':
            if ui.question_box("Cancel backup operation?\n", 80, 15):
                ui.set_loading_bar_visible(window, False)
                return "BACKUP CANCELLED"
    # -----------------------------------------------------

    files_to_process = len(new_files) + len(del_files)
    # endregion

    moved, copied, trashed = 0, 0, 0

    # region 4. DOING MOVE OPERATIONS ==================================================================================
    # iterating backwards since things need to be deleted from new_files and del_files possibly
    for i in range(len(new_files) - 1, -1, -1):
        for j in range(len(del_files) - 1, -1, -1):
            # move operation will happen
            if new_files[i].size == del_files[j].size and new_files[i].filename == del_files[j].filename:
                if using_windows:
                    assure_path_to_file_exists(path_to_file(new_files[i].target_path))
                else:
                    assure_path_to_file_exists(path_to_file(new_files[i].target_path.replace("\\", "/")))
                # moving a file instead of doing a copy and delete
                if using_windows:
                    shutil.move(del_files[j].target_path, new_files[i].target_path)
                else:
                    shutil.move(del_files[j].target_path.replace("\\", "/"),
                                new_files[i].target_path.replace("\\", "/"))
                moved += 1
                # --------------------------------------------------- logging
                msg = "  Moving: '" + get_filename(new_files[i].target_path) + "'"
                print(msg)
                logging.log_file += msg + "\n    to path: '" + new_files[i].target_path + "'\n"
                # -------------------------------------------------------------
                backup_location = backup_directory + file
                if use_graphics:
                    window["-ERROR-TEXT-"].update(str(ui.format_text_for_gui_display(msg)))
                    window.refresh()
                assure_path_to_file_exists(path_to_file(backup_location))
                if using_windows:
                    shutil.copyfile(main_folder + file, backup_location)
                else:
                    shutil.copyfile(main_folder + file, backup_location.replace("\\", "/"))
                # deleting folder if its empty now
                delete_directory_if_empty(del_files[j].target_path)

                # deleting these items from the copy and delete lists, important to do this last
                del new_files[i]
                del del_files[j]

                # ------ checking for events and updating loading bar
                if use_graphics:
                    # loading bar stuff
                    progress_count += 2
                    window["-BAR-"].update(progress_count / files_to_process)

                    # do event check here
                    event, values = window.read(timeout=0)
                    # if any input event in detected, open window to ask about cancelling
                    if event != '__TIMEOUT__':
                        if ui.question_box("Cancel backup operation?\n", 80, 15):
                            ui.set_loading_bar_visible(window, False)
                            return "BACKUP CANCELLED"
                # -----------------------------------------------------

                break
    # endregion

    # region 5. DOING DELETE OPERATIONS ================================================================================
    global delete_files
    if delete_files:
        for i in range(len(del_files)):
            file_name = get_filename(del_files[i].target_path)
            msg = ""
            if using_windows:
                msg += "  Recycling: '" + file_name + "'"
            else:
                msg += "  Trashing: '" + file_name + "'"
            print(msg)
            logging.log_file += msg + "\n    from path: '" + del_files[i].target_path + "'\n"
            if use_graphics:
                window["-ERROR-TEXT-"].update(str(ui.format_text_for_gui_display(msg)))
                window.refresh()
            # os.remove(backup_directory + file_in_backup) # old method that fully deletes file instantly
            trash.trash_file(del_files[i].target_path)
            trashed += 1
            # deleting folder if its empty now
            delete_directory_if_empty(del_files[i].target_path)

            # removing from new_space_used since deleting creates more space
            new_space_used -= del_files[i].size
            # print(" SPACE LEFT=" + str((target_drive_free_space - new_space_used) // (2 ** 30)) +
            #       "GB left")

            # ------ refreshing the window and checking for events
            if use_graphics:
                # loading bar stuff
                progress_count += 1
                window["-BAR-"].update(progress_count / files_to_process)
                # do event check here
                event, values = window.read(timeout=0)
                # if any input event in detected, open window to ask about cancelling
                if event != '__TIMEOUT__':
                    if ui.question_box("Cancel backup operation?\n", 80, 15):
                        ui.set_loading_bar_visible(window, False)
                        return "BACKUP CANCELLED"
            # -----------------------------------------------------
    # endregion

    # region 6. DOING COPY OPERATIONS ==================================================================================
    pause_now = False
    global busy
    for i in range(len(new_files)):
        # ------ refreshing the window and checking for events
        if use_graphics:
            # do event check here
            event, values = window.read(timeout=0)
            # if any input event in detected, open window to ask about cancelling
            if event != '__TIMEOUT__' or pause_now:
                pause_now = False
                if ui.question_box("Cancel backup operation?\n", 80, 15):
                    ui.set_loading_bar_visible(window, False)
                    return "BACKUP CANCELLED"
        # -----------------------------------------------------
        # copy the file over if its not found
        file_name = get_filename(new_files[i].target_path)
        msg = "  Copying: '" + file_name + "'"
        print(msg)
        logging.log_file += msg + "\n    to path: '" + new_files[i].target_path + "'\n"
        if use_graphics:
            window["-ERROR-TEXT-"].update(str(ui.format_text_for_gui_display(msg)))
            window.refresh()
        assure_path_to_file_exists(new_files[i].target_path)
        # assure_path_to_file_exists(path_to_file(new_files[i].target_path))
        # ensuring there is enough space on the target drive for this operation
        new_space_used += new_files[i].size
        # print("SPACE LEFT=" + str((target_drive_free_space - new_space_used) // (2 ** 30)) +
        #       "GB left")
        # print("new_space_used > target_drive_free_space? " + str(new_space_used > target_drive_free_space))
        if new_space_used > target_drive_free_space:
            # print("NOT ENOUGH SPACE")
            ui.set_loading_bar_visible(window, False)
            # log messages done after message is returned
            return "INSUFFICIENT SPACE"
        copied += 1
        if use_graphics:
            thread1 = threading.Thread(target=copy_file_thread, args=(using_windows, new_files[i].source_path,
                                                                      new_files[i].target_path))
            thread1.start()
            # input check and refresh
            while busy:
                window.refresh()
                event, values = window.read(timeout=0)
                if event != '__TIMEOUT__':
                    window["-ERROR-TEXT-"].update(str("Pausing Backup..."))
                    pause_now = True
            # loading bar stuff
            progress_count += 1
            window["-BAR-"].update(progress_count / files_to_process)
        else:  # command line copy
            if using_windows:
                shutil.copyfile(new_files[i].source_path, new_files[i].target_path)
            else:
                shutil.copyfile(new_files[i].source_path.replace("\\", "/"),
                                new_files[i].target_path.replace("\\", "/"))
    # endregion

    # region 7. Backup Successful, returning
    final_counts = "Files Moved: (" + str(moved) + ")\nFiles Trashed: (" + str(trashed) + \
                   ")\nFiles Copied: (" + str(copied) + ')'
    print(final_counts)
    print("<<< Backup Successful >>>")
    logging.log_file += final_counts + '\n'
    logging.log_file += "<<< Backup Successful >>>\n\n"
    if use_graphics:
        ui.set_loading_bar_visible(window, False)
    return "BACKUP SUCCESSFUL"

    # endregion


# endregion

# region 4. Unit Testing Help Functions

import random
import string


def exists_in_cfg(text, cfg_path):
    f = open(os.getcwd() + cfg_path, "r")
    for line in f:
        if line.strip() == text:
            f.close()
            return True
    f.close()
    return False


def get_line_from_cfg(heading):
    f = open(os.getcwd() + "/settings.cfg", "r")
    for line in f:
        if line[0:len(heading)] == heading:
            f.close()
            return (line[len(heading) + 1:len(line)]).strip()
    f.close()
    return "NotFound"


def delete_all_files_in_path(path):
    files = get_all_filenames(path)
    for file in files:
        os.remove(file)


def delete_folder(path):
    if exists(path):
        os.rmdir(path)


def remove_test_files(test_files_path):
    delete_all_files_in_path(test_files_path)
    delete_folder(test_files_path)


def random_string(min_length, max_length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(random.randint(min_length, max_length)))


def create_random_file(path):
    # file_name = os.path.join(path, random_string(5, 10) + "." + random_string(1, 5))
    file_name = path + '/' + random_string(5, 10) + "." + random_string(1, 5)
    # print("file_name=" + file_name)
    # file_name = (file_name.replace("\\", "/")).replace("//", "/")
    # print("file_name=" + file_name)
    assure_path_to_file_exists(file_name)
    fp = open(file_name, 'w')
    fp.write(random_string(20000, 100000))
    fp.close()
    return file_name


def fill_path_with_random_files(path, size_bytes):
    memory_used_bytes = 0
    while memory_used_bytes < size_bytes:
        # create random file and keep track of the size of the files created
        file_name = create_random_file(path)
        memory_used_bytes += get_file_size(file_name)
        # print("memory_used_kb=" + str(memory_used_bytes) + " for " + file_name)
        pass


def get_all_subfolders(path):
    return [f.path for f in os.scandir(path) if f.is_dir()]


def fully_delete_path(path):
    """ WARNING, this is for unit testing ONLY and permanently deletes this path """
    if not exists(path):
        return
    fully_delete_files_in_path(path)
    fully_delete_folders_in_path(path)
    os.rmdir(path)


def fully_delete_files_in_path(path):
    """ WARNING, this is for unit testing ONLY and permanently deletes files """
    files = get_all_filenames(path)
    for file in files:
        os.remove(file)


def fully_delete_folders_in_path(path):
    """ WARNING, this is for unit testing ONLY and permanently deletes folders """
    # format the path
    path = (path.replace("\\\\", "\\")).replace("\\", "/")

    # print("trash_empty_folders(" + path + ")")
    # print("path=" + path)
    # print(str(path.split("/")))

    dist_from_path_to_root = len(path.split("/"))
    folders = get_all_foldernames(path)
    for folder in folders:
        # this folder is not empty
        if len(os.listdir(folder)) > 0:
            continue

        # getting distance to the root directory
        folder = (folder.replace("\\\\", "\\")).replace("\\", "/")

        # print("removing folder: " + os.path.basename(folder))
        # print("dist_from_path_to_root=" + str(dist_from_path_to_root))
        # print("len(os.path.split(folder))=" + str(len(folder.split("/"))))
        # print("folder=" + folder)

        dist_to_root = len(folder.split("/")) - dist_from_path_to_root
        # deleting the folder
        os.rmdir(folder)
        #  checking backwards a safe number of times for more empty folders, ensuring not to go past the root
        # print(" for i in range(dist_to_root) " + str(dist_to_root))
        for i in range(dist_to_root):
            # print("    i=" + str(i))
            # go one folder up
            folder = os.path.dirname(folder)
            # if reached the path, stop now
            if folder == path:
                break
            # if this directory is also empty
            elif len(os.listdir(folder)) == 0:
                # deleting the folder
                os.rmdir(folder)
                # print("         Deleting folder: " + folder)
            else:
                # folder is not empty, no need to keep checking up the path
                # print("         folder is not empty")
                break


def folders_are_equal(folder1, folder2):
    """ Returns True if the contents of both folders have the same names """
    files1 = get_all_filenames(folder1)
    files2 = get_all_filenames(folder2)
    for file1 in files1:
        found = False
        for file2 in files2:
            if file1[len(folder1): len(file1)] == file2[len(folder2): len(file2)] and \
                    get_file_size(file1) == get_file_size(file2):
                found = True
                break
        if not found:
            return False
    return True


def create_test_files(test_files_path, main_folder_size_bytes):
    assure_path_to_file_exists(test_files_path)
    main_folder = test_files_path + "/main"
    backup_folders = [test_files_path + "/b1", test_files_path + "/b2", test_files_path + "/b3",
                      test_files_path + "/b4", test_files_path + "/b5"]
    main_sub_folders = [main_folder,
                        main_folder + "/move_to",
                        main_folder + "/folder1",
                        main_folder + "/folder1/folder2",
                        main_folder + "/folder1/folder2/folder3",
                        main_folder + "/folder4",
                        main_folder + "/folder4/folder5"
                        ]
    print("Setting up test environment...")
    # 1. create files in main folder
    for i in range(7):
        fill_path_with_random_files(main_sub_folders[i], (main_folder_size_bytes / len(main_sub_folders)))
    # 2. copying the main folder to all backup folders
    files_to_copy = get_all_filenames(main_folder)
    root_path_length = len(main_folder)
    for backup_folder in backup_folders:
        for file in files_to_copy:
            file_name = file[root_path_length:len(file)]
            backup_location = backup_folder + file_name
            # print("file: " + file_name + ", backup_location: " + backup_location)
            assure_path_to_file_exists(backup_location)
            shutil.copyfile(file, backup_location)
    # 3. making delete operation setups (creating new files to delete)
    files = get_all_filenames(main_sub_folders[2])
    for path in files:
        file_name = path[root_path_length:len(path)] + ".delete"
        for backup_folder in backup_folders:
            shutil.copyfile(path, backup_folder + file_name)
    # 4. making copy operation setups (deleting random files)
    for backup_folder in backup_folders:
        files = get_all_filenames(backup_folder)
        for i in range(int(len(files) / 4)):
            file = files[random.randrange(0, len(files))]
            if exists(file):
                os.remove(file)
    # 5. making move operation steps (moving files out of the move folder)
    for backup_folder in backup_folders:
        files = get_all_filenames(backup_folder + "/move_to")
        for file in files:
            file_name = os.path.basename(file)
            shutil.move(file, backup_folder + '/' + file_name)
    return main_folder, backup_folders


def generate_random_files_and_folders(path):
    s = string.lowercase + string.digits
    ''.join(random.sample(s, 10))


# endregion

# region 5. Other Functions


def copy_file_thread(using_windows, source_path, target_path):
    global busy
    busy = True
    if using_windows:
        shutil.copyfile(source_path, target_path)
    else:
        shutil.copyfile(source_path.replace("\\", "/"), target_path.replace("\\", "/"))
    busy = False


def backup_file(file_name):
    """ If the file exists its backed up ending with .old """
    if exists(file_name):
        shutil.copyfile(file_name, file_name + '.old')


def get_all_foldernames(path):
    # return [f.path for f in os.scandir(path) if f.is_dir()]
    global skip_folders
    list_of_files = []
    for dname, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in skip_folders]
        for dir_name in dirs:
            list_of_files.append(os.path.join(dname, dir_name))
    return list_of_files


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


def get_date(path):
    return datetime.datetime.fromtimestamp(os.path.getmtime(path))


# shared resource
# clicked_cancel_button = False
# shared_event = ""
backup_process_complete = False  # lets the loading thread know to stop refreshing the window every time the % goes up 1


def refresh_window_thread(window):
    print("refresh_window_thread THREAD STARTED")
    # global shared_event
    global backup_process_complete
    # global clicked_cancel_button
    backup_process_complete = False
    # clicked_cancel_button = False
    while not backup_process_complete:
        window.refresh()
    print("refresh_window_thread THREAD ENDED")


def end_refresh_window_thread():
    global backup_process_complete
    backup_process_complete = True


def get_all_directories_in(path):
    directories = []
    for file in os.scandir(path):
        if file.is_dir():
            directories.append(file)
    return directories


def delete_directory_if_empty(file_path):
    # deleting folder if its empty now
    directory_of_this = path_to_file(file_path)
    dir_list = os.listdir(directory_of_this)
    if len(dir_list) == 0:
        print("  Deleting the folder since its empty now")
        logging.log_file += "  Deleting the folder since its empty now\n";
        os.rmdir(directory_of_this)


def assure_path_to_file_exists(path_to_file):
    """ Assures this path exists, and makes the path if it does not exist """
    dir = os.path.dirname(path_to_file)
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

# endregion
