"""
EZ Folder Backup v1.0.3

Update v1.0.3
- Added an option in settings to ignore all files inside a specific folder name
- Instead of deleting files now it just sends them to Recycle Bin on Windows or Trash on Linux

A simple local backup application that runs on Windows and Linux

Run on windows:
    Run 'EZ Folder Backup.exe'
Run on linux with graphics:
    Run the script with no parameters:
    $ python main.py
Run on linux with command line only:
    See all parameters by running:
        $ python main.py -help
    Basic backup command is:
        $ python main.py -runbackup -m /path_to_main/ -b /path_to_backup/

-Latest version found at: https://github.com/jce77/EZFolderBackup
-To make a donation, please visit: https://ko-fi.com/jcecode
"""
from send2trash import send2trash
import copy
import time
from datetime import datetime
import sys
import webbrowser
from sys import platform
import os
import shutil
from os.path import exists

try:
    import PySimpleGUI as gui
except:
    pass

all_commands = ["-createpreset", "-b", "-deletepreset", "-h", "-help", "-hf", "-logfilemax", "-m", "-moveup",
                "-movedown",
                "-nologging", "-runbackup", "-runpreset", "-skipfile", "-support", "-version", "-viewlog",
                "-viewpresets", "-skipfolder"]
backup_folders = []
log_file = ""
log_file_max_count = 50  # starts deleting the oldest file once 50 logs exist
main_folder = ""
no_logging = False  # If true no log files will be created, False by default
presets = {}
skip_files = []
skip_folders = []
icon_file = ""
version = "1.0.3"


def backup_file(file_name):
    """ If the file exists its backed up ending with .old """
    if exists(file_name):
        shutil.copyfile(file_name, file_name + '.old')


def load_settings_from_config():
    global log_file_max_count
    global no_logging
    global skip_files
    global skip_folders
    if exists('settings.cfg'):
        skip_files = []
        skip_folders = []
        with open('settings.cfg', 'r') as f:
            for line in f:
                line = line.strip()
                if 'log_file_max_count=' in line:
                    log_file_max_count = int(line[19: len(line)])
                elif 'no_logging=' in line:
                    no_logging = line[11: len(line)] == 'True'
                elif 'skip_file=' in line:
                    skip_files.append(line[10: len(line)])
                elif 'skip_folder=' in line:
                    skip_folders.append(line[12: len(line)])
    else:
        # save default settings to the config
        save_settings_to_config()


def save_settings_to_config():
    global log_file_max_count
    global no_logging
    global skip_files
    global skip_folders
    settings = "log_file_max_count=" + str(log_file_max_count) + "\n"
    settings += "no_logging=" + str(no_logging) + "\n"
    for file in skip_files:
        settings += "skip_file=" + file + "\n"
    for folder_name in skip_folders:
        settings += "skip_folder=" + folder_name + "\n"
    with open('settings.cfg', 'w') as f:
        f.write(settings)


def save_presets_to_config(presets):
    """ Saves the input backup presets to the presets.cfg file """
    backup_file('presets/presets.cfg.old')
    backup_file('presets/presets.cfg')
    lines = ""
    for preset in presets:
        lines += "preset=" + preset + "\n"
        lines += "main_folder=" + str(presets[preset]["main_folder"]).replace("/", "\\") + "\n"
        for backup_folder in presets[preset]["backup_folders"]:
            lines += "backup_folder=" + str(backup_folder).replace("/", "\\") + "\n"
    with open('presets/presets.cfg', 'w') as f:
        f.write(lines)


def get_all_filenames(path):
    """ Returns all filenames inside the given path and its sub-folders """
    global skip_folders
    list_of_files = []
    extensions = ('.txt')
    for dname, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in skip_folders]
        for fname in files:
            if (fname.lower().endswith(extensions)):
                list_of_files.append(os.path.join(dname, fname))
    return list_of_files


def remove_path_to_root_folder_from_each(path_to_directory, list_of_files):
    """ Removes the path to the backup folder from each filename in the list """
    for i in range(len(list_of_files)):
        list_of_files[i] = list_of_files[i][len(path_to_directory):len(list_of_files[i])]
    return list_of_files


def get_file_size(first_path, second_path):
    return os.path.getsize(first_path + second_path)


def get_filename(full_path):
    """ Returns the filename only without the path """
    return os.path.basename(full_path)


def path_to_file(full_path):
    """ Returns path without file name """
    return full_path[0:len(full_path) - len(get_filename(full_path))]


def copy_from_main_to_backup_directory(use_graphics, window, main_folder, list_of_files_to_backup, backup_directory):
    """ Ensures the input backup_directory is a clone of the main """
    global log_file
    global using_windows
    if not using_windows:
        backup_directory = backup_directory.replace("\\", "/")
    if ":" == backup_directory[1:2]:
        if not exists(backup_directory[0:3]):
            if use_graphics:
                window["-ERROR-TEXT-"].update("Drive" + backup_directory[0:3] + " is not connected")
            err_msg = "<<< Drive " + backup_directory[
                                     0:3] + " is not connected, skipping backup for drive: " \
                                            "" + backup_directory + ">>>\n"
            log_file += err_msg
            print(err_msg)
            return "DRIVE " + backup_directory[0:3] + " NOT FOUND"
    print("<<< Backing up files to directory: " + backup_directory + " >>>")
    log_file += "<<< Backing up files to directory: " + backup_directory + " >>>\n"
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
            log_file += "  '" + get_filename(
                file) + "' not found, copying to this backup directory\n"
            backup_location = backup_directory + file
            if use_graphics:
                window["-ERROR-TEXT-"].update("Copying to " + str(format_text_for_gui_display(get_filename(file))))
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
            log_file += "  '" + get_filename(
                file_in_backup) + "' is not in main folder, sending to Recycle Bin\n"
        else:
            print("  '" + get_filename(file_in_backup) + "' is not in main folder, sending to Trash")
            log_file += "  '" + get_filename(
                file_in_backup) + "' is not in main folder, sending to Trash\n"
        if use_graphics:
            window["-ERROR-TEXT-"].update("Trashing " + str(format_text_for_gui_display(get_filename(file_in_backup))))
            window.refresh()
        # os.remove(backup_directory + file_in_backup) # old method that fully deletes file instantly
        send2trash(backup_directory + file_in_backup)
        # deleting folder if its empty now
        directory_of_this = path_to_file(backup_directory + file_in_backup)
        dir_list = os.listdir(directory_of_this)
        if len(dir_list) == 0:
            print("  Deleting the folder since its empty now")
            log_file += "  Deleting the folder since its empty now\n";
            os.rmdir(directory_of_this)
    print("<<< Backup Successful >>>")
    log_file += "<<< Backup Successful >>>\n\n"
    return "BACKUP SUCCESSFUL"


def format_text_for_gui_display(text):
    """ Ensures no strange characters that will crash the GUI exist in the string of text """
    char_list = [text[j] for j in range(len(text)) if ord(text[j]) in range(65536)]
    text = ''
    for j in char_list:
        text = text + j
    return text


def assure_path_exists(path):
    """ Assures this path exists, and makes the path if it does not exist """
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
        os.makedirs(dir)


def eula_agreed_to():
    """ Returns True if the eula has already been agreed to """
    with open("EULA.txt", "r", encoding="utf-8") as f:
        line_count = 1
        for line in f:
            if 'agree=yes\n' == line.lower():
                return True
            if line_count > 1:
                break
            line_count += 1
    return False


def refresh_presets_list(window, presets):
    """ Updates the list of backup presets in the left column """
    preset_keys = []
    for key in presets:
        preset_keys.append(str(key))
    window["-PRESET LIST-"].update(values=preset_keys)


def check_for_log_file_limit():
    """ Deletes the oldest parameter if there are more than log_file_max_count log files in the folder """
    global log_file_max_count
    list = os.listdir("log/")
    if len(list) > log_file_max_count:
        oldest_file = list[0]
        oldest_file_creation_time = os.path.getctime("log/" + str(list[0]))
        for file in list:
            creation_time = os.path.getctime("log/" + str(file))
            if creation_time < oldest_file_creation_time:
                oldest_file_creation_time = creation_time
                oldest_file = file
        print("Deleted oldest log file: " + oldest_file)
        os.remove("log/" + oldest_file)


def get_last_log_file_path():
    """ Returns the path to the latest log file to be made """
    if not exists("log/"):
        os.mkdir("log/")
        return "none"
    list = os.listdir("log/")
    if len(list) == 0:
        return "none"
    newest_file = list[0]
    newest_file_creation_time = os.path.getctime("log/" + str(list[0]))
    for file in list:
        creation_time = os.path.getctime("log/" + str(file))
        if creation_time > newest_file_creation_time:
            newest_file_creation_time = creation_time
            newest_file = file
    return os.path.abspath(os.getcwd()) + "/log/" + newest_file


def print_last_log_file():
    """ Prints last log file to the console """
    last_log_file = get_last_log_file_path()
    if last_log_file != "none":
        txt = last_log_file.replace("/", "\\") + ":\n"
        with open(last_log_file, "r", encoding="utf-8") as f:
            for line in f:
                txt += line
        print(txt)


def open_last_log_file():
    """ Opens the last log file to be made """
    last_log_file = get_last_log_file_path()
    if last_log_file != "none":
        os.startfile(last_log_file)


def print_to_log(label, log):
    """ Prints a log file with a label and deletes the oldest parameter if there are
    more than log_file_max_count log files in the folder """
    global no_logging
    if not no_logging:
        if not exists("log/"):
            os.mkdir("log/")
        filename = label + "-" + str(datetime.now().strftime("[%Y_%m_%d]-[%H_%M_%S]")) + ".txt"
        with open("log/" + filename, "w",
                  encoding="utf-8") as f:
            f.write(log)
        check_for_log_file_limit()


def load_selected_preset(preset, window, clicked_key):
    """ Shows the clicked backup preset in the GUI """
    window["-CURRENT-PRESET-NAME-"].update(clicked_key)
    window["-MAIN-FOLDER-"].update(preset['main_folder'])
    count = 1
    for backup_folder in preset['backup_folders']:
        if count == 1:
            window["-BACKUP1-"].update(backup_folder)
        elif count == 2:
            window["-BACKUP2-"].update(backup_folder)
        elif count == 3:
            window["-BACKUP3-"].update(backup_folder)
        elif count == 4:
            window["-BACKUP4-"].update(backup_folder)
        elif count == 5:
            window["-BACKUP5-"].update(backup_folder)
        else:
            break  # you only get 5 backup folders per preset
        count += 1
    while count < 6:
        if count == 1:
            window["-BACKUP1-"].update(backup_folder)
        elif count == 2:
            window["-BACKUP2-"].update("")
        elif count == 3:
            window["-BACKUP3-"].update("")
        elif count == 4:
            window["-BACKUP4-"].update("")
        elif count == 5:
            window["-BACKUP5-"].update("")
        count += 1


def add_preset(name, main_folder, backup_folders):
    global presets
    presets[name] = {'main_folder': main_folder, 'backup_folders': backup_folders}


def delete_preset(name):
    global presets
    del presets[name]


def load_presets():
    """ Reads the presets.cfg file and loads the presets to the GUI """
    presets = {}
    if not exists("presets/"):
        os.mkdir("presets/")
    if not exists("presets/presets.cfg"):
        return presets
    with open("presets/presets.cfg", "r", encoding="utf-8") as f:
        this_preset_key = ''
        for line in f:
            line = line.strip()
            if 'preset=' in line:
                this_preset_key = line[7:len(line)]
                presets[this_preset_key] = {}
            elif 'main_folder=' in line:
                main_folder_path = line[12:len(line)]
                presets[this_preset_key]['main_folder'] = main_folder_path.replace("\\", "/")
            elif 'backup_folder=' in line:
                backup_folder_path = line[14:len(line)]
                if 'backup_folders' in presets[this_preset_key]:
                    presets[this_preset_key]['backup_folders'].append(backup_folder_path.replace("\\", "/"))
                else:
                    presets[this_preset_key]['backup_folders'] = [backup_folder_path.replace("\\", "/")]
    return presets


def run_backup(window, main_folder, backup_folders):
    """ Ensures the input backup_folders are all exact clones of the input main_folder """
    use_graphics = type(window) != int
    global using_windows
    global log_file
    log_file = "Backup Log For Main Folder:\n"
    log_file += main_folder + "\n\n"
    if not exists(main_folder):
        if use_graphics:
            window["-ERROR-TEXT-"].update("The main folder was not found")
            log_file += "The main folder was not found\n"
            print_to_log("Main_Not_Found", log_file)
            return
    for i in range(len(backup_folders)):
        backup_folders[i] = backup_folders[i].replace("/", "\\")
    # getting all file paths in the main storage directory
    list_of_files = get_all_filenames(main_folder)
    # formatting names
    list_of_files = remove_path_to_root_folder_from_each(main_folder, list_of_files)
    # comparing the other directories and deleting files that no longer exist
    error_msg = ""
    response = ""
    for backup_directory in backup_folders:
        response = copy_from_main_to_backup_directory(use_graphics, window, main_folder, list_of_files,
                                                      backup_directory)
        if "NOT FOUND" in response:
            error_msg = response
    if use_graphics:
        if error_msg == "":
            window["-ERROR-TEXT-"].update(response)
        else:
            window["-ERROR-TEXT-"].update(error_msg)
    # debug log
    print_to_log("Backup", log_file)


def valid_input_for_backup(values):
    """ Ensures enough information was input to try and do the backup """
    if len(values["-MAIN-FOLDER-"]) > 0 and len(values["-BACKUP1-"]) > 0:
        return True
    else:
        return False


def get_backup_folders_from_gui(values):
    """ Returns all the backup folder names that were entered into the GUI """
    backup_folders = []
    if len(values["-BACKUP1-"]) > 0:
        backup_folders.append(values["-BACKUP1-"])
    if len(values["-BACKUP2-"]) > 0:
        backup_folders.append(values["-BACKUP2-"])
    if len(values["-BACKUP3-"]) > 0:
        backup_folders.append(values["-BACKUP3-"])
    if len(values["-BACKUP4-"]) > 0:
        backup_folders.append(values["-BACKUP4-"])
    if len(values["-BACKUP5-"]) > 0:
        backup_folders.append(values["-BACKUP5-"])
    return backup_folders


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


def show_gui():
    """ Shows the main GUI """
    global using_windows
    global presets
    presets = load_presets()
    preset_keys = []
    for key in presets:
        preset_keys.append(str(key))

    left_column = [
        [
            gui.Text("Main Folder:"),
            gui.In(size=(25, 1), enable_events=True, key="-MAIN-FOLDER-"),
            gui.FolderBrowse(),
        ],
        [
            gui.Text("Backup Presets:"),
        ],
        [
            gui.Listbox(
                values=preset_keys, enable_events=True, size=(40, 20), key="-PRESET LIST-"
            )
        ],
        [gui.Frame('', [
            [gui.Button(key='Move Up', image_filename='images/up_arrow.png', image_size=(48, 48), border_width=0,
                        button_color=(gui.theme_background_color(), gui.theme_background_color()), ),
             gui.Button(key='Move Down', image_filename='images/down_arrow.png', image_size=(48, 48),
                        border_width=0,
                        button_color=(gui.theme_background_color(), gui.theme_background_color()), )
             ]], title_color='yellow', border_width=0)],
    ]

    right_column = [
        [gui.Text("Backup Locations:")],
        [
            gui.Text("Backup 1:"),
            gui.In(size=(25, 1), enable_events=True, key="-BACKUP1-"),
            gui.FolderBrowse(),
        ],
        [
            gui.Text("Backup 2:"),
            gui.In(size=(25, 1), enable_events=True, key="-BACKUP2-"),
            gui.FolderBrowse(),
        ],
        [
            gui.Text("Backup 3:"),
            gui.In(size=(25, 1), enable_events=True, key="-BACKUP3-"),
            gui.FolderBrowse(),
        ],
        [
            gui.Text("Backup 4:"),
            gui.In(size=(25, 1), enable_events=True, key="-BACKUP4-"),
            gui.FolderBrowse(),
        ],
        [
            gui.Text("Backup 5:"),
            gui.In(size=(25, 1), enable_events=True, key="-BACKUP5-"),
            gui.FolderBrowse(),
        ],
        [gui.Text("Backup Preset Name:")],
        [gui.In(size=(25, 1), enable_events=True, key="-CURRENT-PRESET-NAME-")],

        [gui.Frame('Backup Preset', [[gui.Button("New", size=(14, 1), image_filename='images/new_preset.png'),
                         gui.Button("Save", size=(14, 1), image_filename='images/save_preset.png'),
                         gui.Button("Delete", size=(14, 1), image_filename='images/delete_preset.png')]],
                   border_width=1)],
        [gui.Frame('', [[gui.Button("Run Backup", size=(14, 1), image_filename='images/backup_files.png'),
                         gui.Button("View Log", size=(14, 1), image_filename='images/view_log.png')]],
                   border_width=0)],
        [gui.Frame('', [[gui.Button("Settings", size=(14, 1), image_filename='images/settings.png'),
                         gui.Button("Get Help", size=(14, 1), image_filename='images/get_help.png'),
                         gui.Button("Donate", size=(14, 1), image_filename='images/make_donation.png')]],
                   border_width=0)],
        [gui.Frame('', [[gui.Button("Exit", size=(14, 1), image_filename='images/exit.png')]], border_width=0)],
        [gui.Text("", size=(50, 1), key="-ERROR-TEXT-", text_color="red")],
    ]

    layout = [
        [
            gui.Column(left_column),
            gui.VSeperator(),
            gui.Column(right_column),
        ]
    ]
    global icon_file
    if using_windows:
        icon_file = 'images/icon.ico'
    else:
        icon_file = 'images/icon.png'

    window = gui.Window("EZ Folder Backup", layout, icon=icon_file)

    while True:
        event, values = window.read()
        window["-ERROR-TEXT-"].update("")
        if event == gui.WIN_CLOSED:
            break
        if event == "Exit":
            if not question_box("Exit program?", 80, 15):
                continue
            else:
                break
        elif event == "Settings":
            show_settings_box()
        elif event == "Get Help":
            show_support_email()
        elif event == "Donate":
            if using_gui:
                if not question_box("Open the website 'https://ko-fi.com/jcecode' externally?", 35, 15):
                    continue
                webbrowser.open('https://ko-fi.com/jcecode')
            else:
                print("to make a donation, please visit https://ko-fi.com/jcecode")
        elif event == "View Log":
            if using_windows:
                open_last_log_file()
            else:
                print_last_log_file()
                window["-ERROR-TEXT-"].update("Check console")
        elif event == "Move Up":
            if len(presets) > 0:
                presets = move_index_in_dict(presets, values["-CURRENT-PRESET-NAME-"], True)
                save_presets_to_config(presets)
                refresh_presets_list(window, presets)
        elif event == "Move Down":
            if len(presets) > 0:
                presets = move_index_in_dict(presets, values["-CURRENT-PRESET-NAME-"], False)
                save_presets_to_config(presets)
                refresh_presets_list(window, presets)
        elif event == "Run Backup":
            use_backup_folders = get_backup_folders_from_gui(values)
            if valid_input_for_backup(values):
                if not question_box("Backup files for preset '" + str(values["-CURRENT-PRESET-NAME-"]) + "'?\n" +
                        "(Files that no longer exist in the Main Folder will be trashed)", 80, 15):
                    continue
                window["-ERROR-TEXT-"].update("Checking for files to copy... ")
                run_backup(window, values["-MAIN-FOLDER-"], use_backup_folders)
            else:
                window["-ERROR-TEXT-"].update("You must set the main drive and at least one backup drive")
        elif event == "New":
            window["-MAIN-FOLDER-"].update("")
            window["-BACKUP1-"].update("")
            window["-BACKUP2-"].update("")
            window["-BACKUP3-"].update("")
            window["-BACKUP4-"].update("")
            window["-BACKUP5-"].update("")
            window["-CURRENT-PRESET-NAME-"].update("")

        elif event == "Delete":
            if values["-CURRENT-PRESET-NAME-"] in presets:
                if not question_box("Delete preset '" + str(values["-CURRENT-PRESET-NAME-"]) + "'?", 80, 15):
                    continue
                print("Deleted Preset: " + str(values["-CURRENT-PRESET-NAME-"]))
                del presets[values["-CURRENT-PRESET-NAME-"]]
                refresh_presets_list(window, presets)
                save_presets_to_config(presets)
            else:
                window["-ERROR-TEXT-"].update("Cannot Delete, Not Found")
        elif event == "Save":
            preset_key = values["-CURRENT-PRESET-NAME-"]
            if len(preset_key) == 0:
                window["-ERROR-TEXT-"].update("Backup Preset Name is not set")
            else:
                print("Saved Preset: " + str(preset_key))
                if preset_key in presets:
                    if not question_box("Overwrite preset '" + str(preset_key) + "'?", 65, 15):
                        continue
                presets[preset_key] = {}  # {"main_folder": values["-MAIN-FOLDER-"], "backup_folders": []}
                presets[preset_key]["main_folder"] = values["-MAIN-FOLDER-"]
                presets[preset_key]["backup_folders"] = []
                if len(values["-BACKUP1-"].strip()) > 0:
                    presets[preset_key]["backup_folders"].append(values["-BACKUP1-"])
                if len(values["-BACKUP2-"].strip()) > 0:
                    presets[preset_key]["backup_folders"].append(values["-BACKUP2-"])
                if len(values["-BACKUP3-"].strip()) > 0:
                    presets[preset_key]["backup_folders"].append(values["-BACKUP3-"])
                if len(values["-BACKUP4-"].strip()) > 0:
                    presets[preset_key]["backup_folders"].append(values["-BACKUP4-"])
                if len(values["-BACKUP5-"].strip()) > 0:
                    presets[preset_key]["backup_folders"].append(values["-BACKUP5-"])
                if len(presets[preset_key]["backup_folders"]) == 0:
                    window["-ERROR-TEXT-"].update("Enter at least one backup folder")
                else:
                    refresh_presets_list(window, presets)
                    save_presets_to_config(presets)
        elif event == "-PRESET LIST-":  # A file was chosen from the listbox
            if len(values["-PRESET LIST-"]) > 0:
                clicked_key = str(values["-PRESET LIST-"][0])
                preset = presets[clicked_key]
                load_selected_preset(preset, window, clicked_key)
                try:
                    filename = os.path.join(
                        values["-MAIN-FOLDER-"], values["-PRESET LIST-"][0]
                    )
                except:
                    pass
        # ==============================================
    window.close()


def show_settings_box():
    global icon_file
    global skip_files
    global skip_folders
    previous_skip_files = copy.copy(skip_files)
    global version
    layout = [
        [gui.Text('Settings:')],
        [gui.Frame('', [[gui.Text("Max number of log files: "),
                         gui.Input("", size=(14, 1), key="-MAX-LOG-FILES-")]], border_width=0)],
        [gui.Frame('', [[gui.Text("Do not log backups: "),
                         gui.Checkbox("", size=(14, 1), key="-DO-NOT-LOG-")]], border_width=0)],

        # IGNORE FILE
        [gui.Frame('', [[gui.Text("File Names to ignore:", size=(20, 1))]], title_color='yellow', border_width=0)],
        [gui.Frame('', [[gui.Listbox(
            values=skip_files, enable_events=True, size=(30, 10), key="-IGNORED-FILES-"
        )]], border_width=0)],

        [gui.Frame('',
                   [[gui.Text("Ignore Filename:", size=(16, 1)), gui.Input("", size=(14, 1), key="-IGNORE-FILENAME-"),
                     gui.Button("Add", size=(14, 1), key="-ADD-IGNORED-"),
                     gui.Button("Remove", size=(14, 1), key="-REMOVE-IGNORED-")]], border_width=0)],

        # IGNORE FOLDER
        [gui.Frame('', [[gui.Text("Folder Names to ignore:", size=(20, 1))]], title_color='yellow', border_width=0)],
        [gui.Frame('', [[gui.Listbox(
            values=skip_folders, enable_events=True, size=(30, 10), key="-IGNORED-FOLDERS-"
        )]], border_width=0)],

        [gui.Frame('',
                   [[gui.Text("Ignore Folder:", size=(16, 1)), gui.Input("", size=(14, 1), key="-IGNORE-FOLDER-"),
                     gui.Button("Add", size=(14, 1), key="-ADD-IGNORED-FOLDER-"),
                     gui.Button("Remove", size=(14, 1), key="-REMOVE-IGNORED-FOLDER-")]], border_width=0)],

        # VERSION
        [gui.Frame('', [[gui.Text('Version: ' + version)]], border_width=0)],

        [gui.Frame('', [[gui.Button("Save", size=(14, 1)),
                         gui.Button("Apply", size=(14, 1)),
                         gui.Button("Cancel", size=(14, 1))]], title_color='yellow', border_width=0)],
    ]
    window = gui.Window("EZ Folder Backup Settings", layout, margins=(8, 20), icon=icon_file,
                        element_justification='l', finalize=True)
    global log_file_max_count
    # previous_log_file_max_count = copy.copy(log_file_max_count)
    window["-MAX-LOG-FILES-"].update(str(log_file_max_count))
    global no_logging
    # previous_no_logging = copy.copy(no_logging)
    if no_logging:
        window["-DO-NOT-LOG-"].update(True)
    while True:
        event, values = window.read()
        if event == "-ADD-IGNORED-":
            to_add = values["-IGNORE-FILENAME-"]
            if to_add not in skip_files:
                skip_files.append(to_add)
                window["-IGNORED-FILES-"].update(skip_files)
        if event == "-REMOVE-IGNORED-":
            to_remove = values["-IGNORE-FILENAME-"]
            if to_remove[0] == '(':
                to_remove = to_remove[2:len(to_remove) - 3]
            # print("trying to remove " + str(to_remove) + " with " + str(len(skip_files)) + "files to skip")
            for i in range(0, len(skip_files)):
                # print(str(i))
                # print("comparing " + str(skip_files[i]) + " to " + str(to_remove))
                if skip_files[i] == to_remove:
                    # print("deleting from files to skip")
                    del skip_files[i]
                    window["-IGNORED-FILES-"].update(skip_files)
                    # print("files to skip now " + str(skip_files))

        # ADDING AND REMOVING IGNORED FOLDERS
        if event == "-ADD-IGNORED-FOLDER-":
            to_add = values["-IGNORE-FOLDER-"]
            if to_add not in skip_folders:
                skip_folders.append(to_add)
                window["-IGNORED-FOLDERS-"].update(skip_folders)
        if event == "-REMOVE-IGNORED-FOLDER-":
            to_remove = values["-IGNORE-FOLDER-"]
            if to_remove[0] == '(':
                to_remove = to_remove[2:len(to_remove) - 3]
            # print("trying to remove " + str(to_remove) + " with " + str(len(skip_folders)) + "files to skip")
            for i in range(0, len(skip_folders)):
                # print(str(i))
                # print("comparing " + str(skip_folders[i]) + " to " + str(to_remove))
                if skip_folders[i] == to_remove:
                    # print("deleting from files to skip")
                    del skip_folders[i]
                    window["-IGNORED-FOLDERS-"].update(skip_folders)
                    # print("files to skip now " + str(skip_folders))
        #
        if event == "-IGNORED-FILES-":
            window["-IGNORE-FILENAME-"].update(values["-IGNORED-FILES-"])
        if event == "-IGNORED-FOLDERS-":
            value = str(values["-IGNORED-FOLDERS-"])
            if value[0] == '{':
                value = str(value).strip('{')
                value = value.strip('}')
            elif value[0] == '[':
                value = str(value).strip("['")
                value = value.strip("']")
            window["-IGNORE-FOLDER-"].update(value)
        if event == "Save":
            no_logging = values["-DO-NOT-LOG-"]
            log_file_max_count = int(values["-MAX-LOG-FILES-"])
            save_settings_to_config()
            break
        if event == "Apply":
            no_logging = values["-DO-NOT-LOG-"]
            log_file_max_count = int(values["-MAX-LOG-FILES-"])
            previous_skip_files = copy.copy(skip_files)
            previous_skip_folders = copy.copy(skip_folders)
            # skip_files should already be setup
            save_settings_to_config()
        if event == "Cancel":
            skip_files = previous_skip_files  # this is important to revert changes
            skip_folders = previous_skip_folders  # this is important to revert changes
            break
        if event == gui.WIN_CLOSED:
            break
    window.close()


def show_support_email():
    """ A dialogue box where you can select the email address """
    # dialogue_box("Email help.jcecode@yahoo.com for questions or to report bugs.", 15, 20)
    support_email = 'help.jcecode@yahoo.com'
    layout = [
        [gui.Text('For questions or to report bugs please email: ')],
        [gui.InputText(support_email, use_readonly_for_disable=True, disabled=True, size=len(support_email),
                       disabled_readonly_background_color="grey70")],
        [gui.Button("Ok")]
    ]
    global icon_file
    window = gui.Window("EZ Folder Backup", layout, margins=(15, 20), icon=icon_file,
                        element_justification='c')
    while True:
        event, values = window.read()
        if event == "Ok":
            break
        if event == gui.WIN_CLOSED:
            break
    window.close()


def question_box(question, x_size, y_size):
    """ Opens a binary question box and returns the users answer """

    # gui.Column(left_column),
    # gui.VSeperator(),
    # gui.Column(right_column),

    layout = [
        [gui.Text(str(question))],
        [gui.Frame('', [[gui.Button("Yes", size=(5, 1)),
                         gui.Button("No", size=(5, 1))]],
                   border_width=0)],
    ]
    global icon_file
    window = gui.Window("EZ Folder Backup", layout, margins=(x_size, y_size), icon=icon_file,
                        element_justification='c')
    answered_yes = False
    while True:
        event, values = window.read()
        if event == "Yes":
            answered_yes = True
            break
        if event == "No" or event == gui.WIN_CLOSED:
            answered_yes = False
            break
    window.close()
    return answered_yes


def get_eula_text():
    eula_text = "--------------------------------------------------------------------------------\n"
    eula_text += 'MIT License\n\n'
    eula_text += 'Copyright (c) 2022 jce77\n\n'
    eula_text += 'Permission is hereby granted, free of charge, to any person obtaining a copy \n'
    eula_text += 'of this software and associated documentation files (the "Software"), to deal\n'
    eula_text += 'in the Software without restriction, including without limitation the rights \n'
    eula_text += 'to use, copy, modify, merge, publish, distribute, sublicense, and/or sell  \n'
    eula_text += 'copies of the Software, and to permit persons to whom the Software is \n'
    eula_text += 'furnished to do so, subject to the following conditions:\n\n'
    eula_text += 'The above copyright notice and this permission notice shall be included in \n'
    eula_text += 'all copies or substantial portions of the Software.\n\n'
    eula_text += 'THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\n'
    eula_text += 'IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\n'
    eula_text += 'FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\n'
    eula_text += 'AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\n'
    eula_text += 'LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\n'
    eula_text += 'OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\n'
    eula_text += 'SOFTWARE.\n'
    eula_text += "--------------------------------------------------------------------------------\n"
    eula_text += '\n'
    return eula_text


def agreed_to_eula(agreed):
    """ Updates EULA.txt to show that the EULA has been agreed to """
    eula_text = ""
    if agreed:
        eula_text += "Agree=Yes\n"
    else:
        eula_text += "Agree=No\n"
    eula_text += "Type Agree=Yes on the top line to show you have read the MIT License agreement and agree with its terms:\n\n"
    eula_text += get_eula_text()
    with open("EULA.txt", "w", encoding="utf-8") as f:
        f.write(eula_text)


def show_eula_gui():
    """ Open the eula agreement gui """
    eula = ""
    with open('EULA.txt') as f:
        eula += str(f.readlines())
    layout = [
        [gui.Text("                            EULA AGREEMENT:")],
        [gui.Multiline('MIT License\n\n'
                       'Copyright (c) 2022 jce77\n\n'
                       'Permission is hereby granted, free of charge, to any person obtaining a copy of this software and '
                       'associated documentation files (the "Software"), to deal in the Software without restriction, '
                       'including without limitation the rights to use, copy, modify, merge, publish, distribute, '
                       'sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is '
                       'furnished to do so, subject to the following conditions:\n\n'
                       'The above copyright notice and this permission notice shall be included in all'
                       'copies or substantial portions of the Software.\n\n'
                       'THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR'
                       'IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,'
                       'FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE'
                       'AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER'
                       'LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,'
                       'OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE'
                       'SOFTWARE.'
                       , size=(50, 25), background_color='grey30', text_color='grey95', disabled=True)],
        [gui.Button("I Agree")],
        [gui.Button("I Do Not Agree")]
    ]
    global icon_file
    window = gui.Window("EZ Folder Backup", layout, icon=icon_file, margins=(55, 55))
    exit_app = False
    while True:
        event, values = window.read()
        if event == "I Do Not Agree" or event == gui.WIN_CLOSED:
            exit_app = True
            break
        if event == "I Agree" or event == gui.WIN_CLOSED:
            break
    window.close()
    return exit_app


def create_help_file():
    help_file_text = print_help_commands(False)
    with open("help.txt", "w",
              encoding="utf-8") as f:
        f.write(help_file_text)


def print_help_commands(print_in_console):
    msg = "--------------------------------------------------------------------------------\n" \
          " EZ Folder Backup Parameters:                                                 \n" \
          "                                                                              \n" \
          "-b path..............................Adds a single backup folder to be used in\n" \
          "                                     this command. Can be used max five times.\n" \
          "-createpreset name -m path -b path...Creates a preset with the input name,    \n" \
          "                                     main folder, and up to five backup       \n" \
          "                                     folder paths that are preceded by -b.    \n" \
          "-deletepreset name...................Deletes the preset with the input name.  \n" \
          "-h...................................Show help menu and exit.                 \n" \
          "-hf..................................Creates a file help.txt containing the   \n" \
          "                                     help menu.                               \n" \
          "-logfilemax count....................Set max number of log files are deleted. \n" \
          "-m path..............................Adds the path to the single main folder  \n" \
          "                                     to be used for this command.             \n" \
          "-movedown name.......................Moves the input preset down in the list. \n" \
          "-moveup name.........................Moves the input preset up in the list.   \n" \
          "-nologging...........................Stops debug logs from being printed after\n" \
          "                                     backups.                                 \n" \
          "-runbackup -m path -b path...........Runs backup for main folder -m and up to \n" \
          "                                     five backup folders that are each        \n" \
          "                                     preceded by -b.                          \n" \
          "-runpreset name......................Runs backup for the input preset.        \n" \
          "-skipfile filename...................Skips this filename, use -skipfile once  \n" \
          "                                     per new filename to be skipped.          \n" \
          "-skipfolder foldername...............Skips this folder name, use -skipfolder  \n" \
          "                                     once per new filename to be skipped. Do  \n" \
          "                                     not enter a path, just the folder name.  \n" \
          "-support.............................Show support email for questions.        \n" \
          "-version.............................Show the current version of this program.\n" \
          "-viewlog.............................Show latest log file.                    \n" \
          "-viewpresets.........................Shows all presets.                       \n" \
          "                                                                              \n" \
          "To make a donation, please visit https://ko-fi.com/jcecode                    \n" \
          "--------------------------------------------------------------------------------\n"
    if print_in_console:
        print(msg)
    return msg


def sort_arguments(arguments):
    """ Sorts the arguments into a dictionary where the command is the key """
    next_command = []
    commands = []
    for arg in arguments:
        if arg in all_commands:
            if len(next_command) > 0:
                txt = ""
                for i in range(1, len(next_command)):
                    if i == 1:
                        txt = next_command[1]
                    else:
                        txt += " " + next_command[i]
                # commands[next_command[0]] = txt
                commands.append([next_command[0], txt])
            # reached a new commands to set
            next_command = [arg]
        else:
            next_command.append(arg)
    if len(next_command) > 0:
        txt = ""
        for i in range(1, len(next_command)):
            if i == 1:
                txt = next_command[1]
            else:
                txt += " " + next_command[i]
        # commands[next_command[0]] = txt
        commands.append([next_command[0], txt])
    return commands


def print_presets(presets, print_in_console):
    """ Shows all presets to the user """
    msg = "All presets:\n"
    for preset in presets:
        print(str(preset))
        msg += " " + preset + "\n"
        msg += "  Main Folder: " + str(presets[preset]["main_folder"]) + "\n"
        count = 1
        for backup_folder in presets[preset]["backup_folders"]:
            msg += "  Backup Folder " + str(count) + ": " + backup_folder + "\n"
            count += 1
    if print_in_console:
        print(msg)
    return msg


def run_commands(commands):
    """ Running commands that were input as parameters in the console """
    global no_logging
    global log_file_max_count
    global skip_files
    global skip_folders
    global presets
    presets = load_presets()
    skip_files = []
    skip_folders = []
    keys = []
    for command in commands:
        keys.append(command[0])
    # Error checking ========================
    if "-createpreset" in keys and "-runbackup" in keys:
        print("Cannot use -createpreset and -runbackup at the same time.")
        sys.exit(1)
    elif keys.count("-createpreset") > 1:
        print("-createpreset can only be run once at a time.")
        sys.exit(1)
    elif keys.count("-runbackup") > 1:
        print("-runbackup can only be run once at a time.")
        sys.exit(1)
    # Running commands =======================
    if "-moveup" in keys:
        for cmd in commands:
            if cmd[0] == "-moveup":
                if len(cmd[1]) == 0:
                    print("-moveup requires a preset name.")
                    sys.exit(1)
                if cmd[1] not in presets:
                    msg = print_presets(presets, False) + "\n\n"
                    msg += "The preset entered '" + cmd[1] + "' could not be found. Cannot do move operation.\n"
                    print(msg)
                    sys.exit(1)
                presets = move_index_in_dict(presets, cmd[1], True)
                # ensure changes are persistent
                save_presets_to_config(presets)
    if "-movedown" in keys:
        for cmd in commands:
            if cmd[0] == "-movedown":
                if len(cmd[1]) == 0:
                    print("-movedown requires a preset name.")
                    sys.exit(1)
                if cmd[1] not in presets:
                    msg = print_presets(presets, False) + "\n\n"
                    msg += "The preset entered '" + cmd[1] + "' could not be found. Cannot do move operation.\n"
                    print(msg)
                    sys.exit(1)
                presets = move_index_in_dict(presets, cmd[1], False)
                # ensure changes are persistent
                save_presets_to_config(presets)
    if "-support" in keys:
        print("For questions or to report bugs please email help.jcecode@yahoo.com")
    if "-version" in keys:
        global version
        print("v" + version)
    if "-viewpresets" in keys:
        print_presets(presets, True)
    if "-viewlog" in keys:
        print_last_log_file()
    if "-h" in keys or "-help" in keys:
        print_help_commands(True)
    if "-hf" in keys:
        create_help_file()
        print("Created help.txt containing all commands.")
    if "-logfilemax" in keys:
        for cmd in commands:
            if cmd[0] == "-logfilemax":
                log_file_max_count = int(cmd[1])
    if "-nologging" in keys:
        no_logging = True
    if "-skipfile" in keys:
        for cmd in commands:
            if cmd[0] == "-skipfile":
                skip_files.append(cmd[1])
    if "-skipfolder" in keys:
        for cmd in commands:
            if cmd[0] == "-skipfolder":
                skip_folders.append(cmd[1])
    # Presets
    if "-createpreset" in keys:
        preset_key = ""
        main_folder = ""
        backup_folders = []
        for cmd in commands:
            if cmd[0] == "-createpreset":
                if len(cmd[1]) > 0:
                    preset_key = cmd[1]
            elif cmd[0] == "-m":
                main_folder = cmd[1]
            elif cmd[0] == "-b":
                backup_folders.append(cmd[1])
        if preset_key == "":
            print("No name was entered for this preset.")
            sys.exit(1)
        if main_folder == "":
            print("No main folder was added using the -m command. Cannot create preset.")
            sys.exit(1)
        if len(backup_folders) == 0:
            print("No backup folder was added using the -b command. Cannot create preset.")
            sys.exit(1)
        presets[preset_key] = {}
        presets[preset_key]["main_folder"] = main_folder
        presets[preset_key]["backup_folders"] = backup_folders
        # ensure changes are persistent
        save_presets_to_config(presets)
    if "-deletepreset" in keys:
        preset_key = ""
        for cmd in commands:
            if cmd[0] == "-deletepreset":
                if len(cmd[1]) == 0:
                    print("No name was entered for this preset.")
                    sys.exit(1)
                else:
                    preset_key = cmd[1]
        if preset_key in presets:
            print("Deleted preset: " + preset_key)
            del presets[preset_key]
            # ensure changes are persistent
            save_presets_to_config(presets)
        else:
            print("Key entered '" + preset_key + "' could not be found to be deleted.")
    # Running Backup
    if "-runbackup" in keys:
        main_folder = ""
        backup_folders = []
        for cmd in commands:
            if cmd[0] == "-m":
                main_folder = cmd[1]
            elif cmd[0] == "-b":
                backup_folders.append(cmd[1])
        if main_folder == "":
            print("No main folder was added using the -m command. Cannot run backup.")
            sys.exit(1)
        if len(backup_folders) == 0:
            print("No backup folder was added using the -b command. Cannot run backup.")
            sys.exit(1)
        if not exists(main_folder):
            print("The main folder '" + main_folder + "' could not be found.")
            sys.exit(1)
        run_backup(0, main_folder, backup_folders)
    elif "-runpreset" in keys:
        preset_key = ""
        for cmd in commands:
            if cmd[0] == "-runpreset":
                if len(cmd[1]) > 0:
                    preset_key = cmd[1]
        if preset_key == "":
            print("No name was entered for the command: -runpreset")
            sys.exit(1)
        if preset_key not in presets:
            msg = print_presets(presets, False) + "\n\n"
            msg += "The preset entered '" + preset_key + "' could not be found. Cancelling backup. All presets have been listed above.\n"
            print(msg)
            sys.exit(1)
        preset = presets[preset_key]
        run_backup(0, preset["main_folder"], preset["backup_folders"])


if __name__ == '__main__':
    using_windows = False
    if 'win32' in platform or 'win64' in platform:
        using_windows = True
    using_gui = False
    if len(sys.argv) == 1:
        using_gui = True
    if not exists("EULA.txt"):
        agreed_to_eula(False)
    # Running with graphics
    if using_gui:
        if not eula_agreed_to():
            exit_app = show_eula_gui()
            if exit_app:
                print_to_log('Failed_To_Run',
                             'Agree to the EULA agreement in the file EULA.txt before using this please')
                print('Agree to the EULA before using this software please')
                sys.exit(1)
        agreed_to_eula(True)
        try:
            if gui.WIN_CLOSED:
                pass
        except:
            print(
                "PySimpleGui is not installed, please install using pip before using the graphical interface.\n Otherwise run the parameter -help to see all command line-only parameters")
            sys.exit(1)
        # only loading settings in the GUI for now, otherwise they must be entered with run command
        # to be used
        load_settings_from_config()
        show_gui()
    # Running with command-line parameters only
    else:
        if not eula_agreed_to():
            print(get_eula_text())
            print("Enter 'Yes' to confirm that you have read licence above and agree with its terms: ")
            result = input()
            if result.lower() == "yes":
                agreed_to_eula(True)
            else:
                print("Please agree to EULA before using the program. Thank you.")
                sys.exit(0)
        commands = sort_arguments(sys.argv)
        run_commands(commands)
