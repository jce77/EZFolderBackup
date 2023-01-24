import copy
import webbrowser

from scripts import program as main
from scripts import saving
from scripts import files
from scripts import logging
import os

try:
    import PySimpleGUI as gui
except:
    pass

using_gui = False
previous_skip_folders = []


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


def show_gui():
    """ Shows the main GUI """
    main.presets = saving.load_presets()
    preset_keys = []
    for key in main.presets:
        preset_keys.append(str(key))

    BAR_MAX = 1

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
                        button_color=(gui.theme_background_color(), gui.theme_background_color()), ),
             gui.ProgressBar(BAR_MAX, orientation='h', size=(12.3, 31.5), key='-BAR-', visible=False),
             gui.Button(" ", size=(14, 1), image_filename='images/cancel.png', visible=False)
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
    if main.using_windows:
        main.icon_file = 'images/icon.ico'
    else:
        main.icon_file = 'images/icon.png'

    # getting the window
    window = gui.Window("EZ Folder Backup", layout, icon=main.icon_file)
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
            if main.using_windows:
                logging.open_last_log_file()
            else:
                logging.print_last_log_file()
                window["-ERROR-TEXT-"].update("Check console")
        elif event == "Move Up":
            if len(main.presets) > 0:
                main.presets = files.move_index_in_dict(main.presets, values["-CURRENT-PRESET-NAME-"], True)
                saving.save_presets_to_config(main.presets)
                refresh_presets_list(window, main.presets)
        elif event == "Move Down":
            if len(main.presets) > 0:
                main.presets = files.move_index_in_dict(main.presets, values["-CURRENT-PRESET-NAME-"], False)
                saving.save_presets_to_config(main.presets)
                refresh_presets_list(window, main.presets)
        elif event == "Run Backup":
            use_backup_folders = get_backup_folders_from_gui(values)
            if files.valid_input_for_backup(values):
                if not question_box("Backup files for preset '" + str(values["-CURRENT-PRESET-NAME-"]) + "'?\n" +
                        "(Files that no longer exist in the Main Folder will be trashed)", 80, 15):
                    continue
                set_loading_bar_visible(window, True)
                main.run_backup(window, values["-MAIN-FOLDER-"], use_backup_folders)
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
            if values["-CURRENT-PRESET-NAME-"] in main.presets:
                if not question_box("Delete preset '" + str(values["-CURRENT-PRESET-NAME-"]) + "'?", 80, 15):
                    continue
                print("Deleted Preset: " + str(values["-CURRENT-PRESET-NAME-"]))
                del main.presets[values["-CURRENT-PRESET-NAME-"]]
                refresh_presets_list(window, main.presets)
                saving.save_presets_to_config(main.presets)
            else:
                window["-ERROR-TEXT-"].update("Cannot Delete, Not Found")
        elif event == "Save":
            preset_key = values["-CURRENT-PRESET-NAME-"]
            if len(preset_key) == 0:
                window["-ERROR-TEXT-"].update("Backup Preset Name is not set")
            else:
                print("Saved Preset: " + str(preset_key))
                if preset_key in main.presets:
                    if not question_box("Overwrite preset '" + str(preset_key) + "'?", 65, 15):
                        continue
                main.presets[preset_key] = {}  # {"main_folder": values["-MAIN-FOLDER-"], "backup_folders": []}
                main.presets[preset_key]["main_folder"] = values["-MAIN-FOLDER-"]
                main.presets[preset_key]["backup_folders"] = []
                if len(values["-BACKUP1-"].strip()) > 0:
                    main.presets[preset_key]["backup_folders"].append(values["-BACKUP1-"])
                if len(values["-BACKUP2-"].strip()) > 0:
                    main.presets[preset_key]["backup_folders"].append(values["-BACKUP2-"])
                if len(values["-BACKUP3-"].strip()) > 0:
                    main.presets[preset_key]["backup_folders"].append(values["-BACKUP3-"])
                if len(values["-BACKUP4-"].strip()) > 0:
                    main.presets[preset_key]["backup_folders"].append(values["-BACKUP4-"])
                if len(values["-BACKUP5-"].strip()) > 0:
                    main.presets[preset_key]["backup_folders"].append(values["-BACKUP5-"])
                if len(main.presets[preset_key]["backup_folders"]) == 0:
                    window["-ERROR-TEXT-"].update("Enter at least one backup folder")
                else:
                    refresh_presets_list(window, main.presets)
                    saving.save_presets_to_config(main.presets)
        elif event == "-PRESET LIST-":  # A file was chosen from the listbox
            if len(values["-PRESET LIST-"]) > 0:
                clicked_key = str(values["-PRESET LIST-"][0])
                preset = main.presets[clicked_key]
                saving.load_selected_preset(preset, window, clicked_key)
                try:
                    filename = os.path.join(
                        values["-MAIN-FOLDER-"], values["-PRESET LIST-"][0]
                    )
                except:
                    pass
        # ==============================================
    window.close()


def set_loading_bar_visible(window, value):
    window["-BAR-"].update(visible=value)
    window[" "].update(visible=value)
    # window["Cancel"].update(visible=value)



def refresh_presets_list(window, presets):
    """ Updates the list of backup presets in the left column """
    preset_keys = []
    for key in presets:
        preset_keys.append(str(key))
    window["-PRESET LIST-"].update(values=preset_keys)


def show_settings_box():
    global previous_skip_folders
    previous_skip_files = copy.copy(files.skip_files)
    layout = [
        [gui.Text('Settings:')],
        [gui.Frame('', [[gui.Text("Max number of log files: "),
                         gui.Input("", size=(14, 1), key="-MAX-LOG-FILES-")]], border_width=0)],
        [gui.Frame('', [[gui.Text("Do not log backups: "),
                         gui.Checkbox("", size=(14, 1), key="-DO-NOT-LOG-")]], border_width=0)],

        # IGNORE FILE
        [gui.Frame('', [[gui.Text("File Names to ignore:", size=(20, 1))]], title_color='yellow', border_width=0)],
        [gui.Frame('', [[gui.Listbox(
            values=files.skip_files, enable_events=True, size=(30, 10), key="-IGNORED-FILES-"
        )]], border_width=0)],

        [gui.Frame('',
                   [[gui.Text("Ignore Filename:", size=(16, 1)), gui.Input("", size=(14, 1), key="-IGNORE-FILENAME-"),
                     gui.Button("Add", size=(14, 1), key="-ADD-IGNORED-"),
                     gui.Button("Remove", size=(14, 1), key="-REMOVE-IGNORED-")]], border_width=0)],

        # IGNORE FOLDER
        [gui.Frame('', [[gui.Text("Folder Names to ignore:", size=(20, 1))]], title_color='yellow', border_width=0)],
        [gui.Frame('', [[gui.Listbox(
            values=files.skip_folders, enable_events=True, size=(30, 10), key="-IGNORED-FOLDERS-"
        )]], border_width=0)],

        [gui.Frame('',
                   [[gui.Text("Ignore Folder:", size=(16, 1)), gui.Input("", size=(14, 1), key="-IGNORE-FOLDER-"),
                     gui.Button("Add", size=(14, 1), key="-ADD-IGNORED-FOLDER-"),
                     gui.Button("Remove", size=(14, 1), key="-REMOVE-IGNORED-FOLDER-")]], border_width=0)],

        # VERSION
        [gui.Frame('', [[gui.Text('Version: ' + main.version)]], border_width=0)],

        [gui.Frame('', [[gui.Button("Save", size=(14, 1)),
                         gui.Button("Apply", size=(14, 1)),
                         gui.Button("Cancel", size=(14, 1))]], title_color='yellow', border_width=0)],
    ]
    window = gui.Window("EZ Folder Backup Settings", layout, margins=(8, 20), icon=main.icon_file,
                        element_justification='l', finalize=True)
    # previous_log_file_max_count = copy.copy(log_file_max_count)
    window["-MAX-LOG-FILES-"].update(str(logging.log_file_max_count))
    # previous_no_logging = copy.copy(no_logging)
    if logging.no_logging:
        window["-DO-NOT-LOG-"].update(True)
    while True:
        event, values = window.read()
        if event == "-ADD-IGNORED-":
            to_add = values["-IGNORE-FILENAME-"]
            if to_add not in files.skip_files:
                files.skip_files.append(to_add)
                window["-IGNORED-FILES-"].update(files.skip_files)
        if event == "-REMOVE-IGNORED-":
            to_remove = values["-IGNORE-FILENAME-"]
            if to_remove[0] == '(':
                to_remove = to_remove[2:len(to_remove) - 3]
            else:
                print("ERROR, input text is not being formatted correctly")
            # print("trying to remove " + str(to_remove) + " with " + str(len(files.skip_files)) + "files to skip")
            for i in range(0, len(files.skip_files)):
                # print(str(i))
                # print("comparing " + str(files.skip_files[i]) + " to " + str(to_remove))
                if files.skip_files[i] == to_remove:
                    # print("deleting from files to skip")
                    del files.skip_files[i]
                    window["-IGNORED-FILES-"].update(files.skip_files)
                    # ("files to skip now " + str(files.skip_files))
                    break

        # ADDING AND REMOVING IGNORED FOLDERS
        if event == "-ADD-IGNORED-FOLDER-":
            to_add = values["-IGNORE-FOLDER-"]
            if to_add not in files.skip_folders:
                files.skip_folders.append(to_add)
                window["-IGNORED-FOLDERS-"].update(files.skip_folders)
        if event == "-REMOVE-IGNORED-FOLDER-":
            to_remove = values["-IGNORE-FOLDER-"]
            if to_remove[0] == '(':
                to_remove = to_remove[2:len(to_remove) - 3]
            # print("trying to remove " + str(to_remove) + " with " + str(len(skip_folders)) + "files to skip")
            for i in range(0, len(files.skip_folders)):
                # print(str(i))
                # print("comparing " + str(skip_folders[i]) + " to " + str(to_remove))
                if files.skip_folders[i] == to_remove: # if file to remove found
                    # print("deleting from files to skip")
                    del files.skip_folders[i]
                    window["-IGNORED-FOLDERS-"].update(files.skip_folders)
                    # print("files to skip now " + str(skip_folders))
                    break
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
            logging.no_logging = values["-DO-NOT-LOG-"]
            logging.log_file_max_count = int(values["-MAX-LOG-FILES-"])
            saving.save_settings_to_config()
            break
        if event == "Apply":
            logging.no_logging = values["-DO-NOT-LOG-"]
            logging.log_file_max_count = int(values["-MAX-LOG-FILES-"])
            previous_skip_files = copy.copy(files.skip_files)
            previous_skip_folders = copy.copy(files.skip_folders)
            # skip_files should already be setup
            saving.save_settings_to_config()
        if event == "Cancel":
            files.skip_files = previous_skip_files  # this is important to revert changes
            files.skip_folders = previous_skip_folders  # this is important to revert changes
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
    window = gui.Window("EZ Folder Backup", layout, margins=(15, 20), icon=main.icon_file,
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
    window = gui.Window("EZ Folder Backup", layout, margins=(x_size, y_size), icon=main.icon_file,
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


def format_text_for_gui_display(text):
    """ Ensures no strange characters that will crash the GUI exist in the string of text """
    char_list = [text[j] for j in range(len(text)) if ord(text[j]) in range(65536)]
    text = ''
    for j in char_list:
        text = text + j
    return text


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


def create_help_file():
    help_file_text = print_help_commands(False)
    with open("help.txt", "w",
              encoding="utf-8") as f:
        f.write(help_file_text)

