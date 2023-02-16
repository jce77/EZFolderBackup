import copy
import webbrowser
from scripts import program as main
from scripts import saving
from scripts import files
from scripts import logging
import os

try:
    import PySimpleGUI as gui
except ModuleNotFoundError:
    pass

using_gui = False
previous_skip_folders = []


def get_listbox_elements(window, key):
    """ Returns all values currently inside the listbox """
    return window[key].get_list_values()


def show_gui(using_windows):
    """ Shows the main GUI """
    main.presets = saving.load_presets()
    preset_keys = []
    for key in main.presets:
        preset_keys.append(str(key))

    BAR_MAX = 1

    gui.theme('DarkGrey')
    gui.theme_button_color('#7A7A7A')

    h1_font = ("Arial Bold", 12)
    h2_font = ("Arial Bold", 10)

    cancel_button_name = " "
    if not using_windows:
        cancel_button_name = " Cancel"

    left_column = [
        [gui.Frame('Backup Preset', [[gui.Button("New", size=(14, 1), image_filename='images/new_preset.png',
                                                 mouseover_colors=('#CBCBCB', '#333333')),
                                      gui.Button("Save", size=(14, 1), image_filename='images/save_preset.png',
                                                 mouseover_colors=('#CBCBCB', '#333333')),
                                      gui.Button("Delete", size=(14, 1), image_filename='images/delete_preset.png',
                                                 mouseover_colors=('#CBCBCB', '#333333'))]],
                   border_width=1)],

        [gui.Text("Preset Name", font=h2_font)],
        [gui.In(size=(45, 1), enable_events=True, key="-CURRENT-PRESET-NAME-")],

        [
            gui.Text("Backup Presets", font=h1_font),
        ],
        [
            gui.Listbox(
                values=preset_keys, enable_events=True, size=(55, 18), key="-PRESET LIST-"
            )
        ],
        [gui.Frame('', [
            [gui.Button(key='Move Up', image_filename='images/up_arrow.png', image_size=(48, 48), border_width=0,
                        button_color=(gui.theme_background_color(), gui.theme_background_color()), ),
             gui.Button(key='Move Down', image_filename='images/down_arrow.png', image_size=(48, 48),
                        border_width=0,
                        button_color=(gui.theme_background_color(), gui.theme_background_color()), ),
             gui.ProgressBar(BAR_MAX, orientation='h', size=(12.3, 31.5), key='-BAR-', visible=False),
             gui.Button(cancel_button_name, size=(14, 1), image_filename='images/cancel.png', visible=False,
                        mouseover_colors=('#CBCBCB', '#333333'), auto_size_button=False)
             ]], title_color='yellow', border_width=0)],
    ]

    right_column = [
        [gui.Text("Main Folder", font=h2_font)],
        [
            gui.In(size=(35, 1), enable_events=True, key="-MAIN-FOLDER-"),
            gui.FolderBrowse(),
        ],
        [gui.Text("Backup Locations", font=h1_font)],
        [
            gui.Listbox(
                values=[], enable_events=True, size=(55, 10), key="-BACKUP-LIST-"
            )
        ],

        [gui.Text("New Backup Location", font=h2_font)],
        [gui.In(size=(45, 1), enable_events=True, key="-NEW-BACKUP-LOCATION-"),
         gui.FolderBrowse(),
         ],



        [gui.Frame('Backup Location', [[gui.Button("New", key="-NEW-BACKUP-", size=(14, 1), image_filename='images/new_preset.png',
                                                 mouseover_colors=('#CBCBCB', '#333333')),
                                      gui.Button("Add", key="-ADD-NEW-BACKUP-", size=(14, 1), image_filename='images/add.png',
                                                 mouseover_colors=('#CBCBCB', '#333333')),
                                      gui.Button("Remove", key="-REMOVE-NEW-BACKUP-", size=(14, 1), image_filename='images/remove.png',
                                                 mouseover_colors=('#CBCBCB', '#333333'))]],
                   border_width=1)],



        [gui.Frame('', [[gui.Button("Run Backup", size=(14, 1), image_filename='images/backup_files.png',
                                    mouseover_colors=('#CBCBCB', '#333333')),
                         gui.Button("View Log", size=(14, 1), image_filename='images/view_log.png',
                                    mouseover_colors=('#CBCBCB', '#333333')),
                         gui.Button("Backup All", size=(14, 1), image_filename='images/backup_all.png',
                                    mouseover_colors=('#CBCBCB', '#333333'))
                         ]],
                   border_width=0)],
        [gui.Frame('', [[gui.Button("Settings", size=(14, 1), image_filename='images/settings.png',
                                    mouseover_colors=('#CBCBCB', '#333333')),
                         gui.Button("Get Help", size=(14, 1), image_filename='images/get_help.png',
                                    mouseover_colors=('#CBCBCB', '#333333')),
                         gui.Button("Donate", size=(14, 1), image_filename='images/make_donation.png',
                                    mouseover_colors=('#CBCBCB', '#333333'))]],
                   border_width=0)],
        [gui.Frame('', [[gui.Button("Exit", size=(14, 1), image_filename='images/exit.png',
                                    mouseover_colors=('#CBCBCB', '#333333'))]], border_width=0)],
        [gui.Text("", size=(50, 1), key="-ERROR-TEXT-")],
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
            else:  # its like this because OS on linux doesn't have a start file function
                logging.print_last_log_file()
                window["-ERROR-TEXT-"].update("Check console")
        elif event == "Move Up":
            if len(main.presets) > 0:
                preset_name = values["-CURRENT-PRESET-NAME-"]
                main.presets = files.move_index_in_dict(main.presets, preset_name, True)
                saving.save_presets_to_config(main.presets)
                refresh_presets_list(window, main.presets)
                window["-PRESET LIST-"].set_value(preset_name)
        elif event == "Move Down":
            if len(main.presets) > 0:
                preset_name = values["-CURRENT-PRESET-NAME-"]
                main.presets = files.move_index_in_dict(main.presets, preset_name, False)
                saving.save_presets_to_config(main.presets)
                refresh_presets_list(window, main.presets)
                window["-PRESET LIST-"].set_value(preset_name)
        elif event == "Backup All":
            if len(main.presets) > 0:
                check_box_text = 'Send deleted files to Recycle Bin?' if using_windows else \
                    'Send deleted files to Trash?'
                response = question_box_with_radio("Backup files for all presets?", check_box_text, files.delete_files,
                                                   80, 15)
                # user clicked x box or answered no
                if type(response) == bool or not response[0]:
                    continue
                files.delete_files = response[1]
                saving.save_settings_to_config()
                main.run_backup_all(window)
            else:
                window["-ERROR-TEXT-"].update("No presets are saved")
        elif event == "Run Backup":
            check_box_text = 'Send deleted files to Recycle Bin?' if using_windows else 'Send deleted files to Trash?'
            use_backup_folders = get_listbox_elements(window, "-BACKUP-LIST-")
            response = question_box_with_radio("Backup files for preset '" +
                                               str(values["-CURRENT-PRESET-NAME-"]) + "'?\n", check_box_text,
                                               files.delete_files, 80, 15)
            # user clicked x box or answered no
            if not files.valid_input_for_backup(window, values):
                window["-ERROR-TEXT-"].update("You must set the main drive and at least one backup drive")
                continue
            if type(response) == bool or not response[0]:
                continue
            files.delete_files = response[1]
            saving.save_settings_to_config()
            main.run_backup(window, values["-MAIN-FOLDER-"], use_backup_folders)
        elif event == "-NEW-BACKUP-":
            window["-NEW-BACKUP-LOCATION-"].update("")
            window["-BACKUP-LIST-"].update(set_to_index=[])
            window["-BACKUP-LIST-"].metadata = []
        elif event == "New":
            clear_preset_info(window)
        elif event == "-ADD-NEW-BACKUP-":  # adding a backup location to the right
            print("Added backup location from GUI: " + str(values["-NEW-BACKUP-LOCATION-"]))
            new_values = window["-BACKUP-LIST-"].get_list_values()
            if len(values["-NEW-BACKUP-LOCATION-"]) > 0 and values["-NEW-BACKUP-LOCATION-"] not in new_values:
                new_values.append(values["-NEW-BACKUP-LOCATION-"])
                window["-BACKUP-LIST-"].update(values=new_values)
                # refresh_backup_locations_list(window, main.presets)
                window["-BACKUP-LIST-"].set_value(values["-NEW-BACKUP-LOCATION-"])
        elif event == "-REMOVE-NEW-BACKUP-":  # deleting a backup location from the right
            new_values = window["-BACKUP-LIST-"].get_list_values()
            for i in range(len(new_values)):
                if new_values[i] == values["-NEW-BACKUP-LOCATION-"]:
                    del new_values[i]
                    break
            window["-BACKUP-LIST-"].update(values=new_values)
            print("Deleted backup location from GUI: " + str(values["-NEW-BACKUP-LOCATION-"]))
            # refresh_backup_locations_list(window, main.presets)
            window["-NEW-BACKUP-LOCATION-"].update("")
        elif event == "Delete":  # deleting a preset from the left
            if values["-CURRENT-PRESET-NAME-"] in main.presets:
                if not question_box("Delete preset '" + str(values["-CURRENT-PRESET-NAME-"]) + "'?", 80, 15):
                    continue
                print("Deleted Preset: " + str(values["-CURRENT-PRESET-NAME-"]))
                del main.presets[values["-CURRENT-PRESET-NAME-"]]
                refresh_presets_list(window, main.presets)
                saving.save_presets_to_config(main.presets)
                clear_preset_info(window)
            else:
                window["-ERROR-TEXT-"].update("Cannot Delete, Not Found")
        elif event == "Save":
            preset_key = values["-CURRENT-PRESET-NAME-"]
            if len(preset_key) == 0:
                window["-ERROR-TEXT-"].update("Backup Preset Name is not set")
            else:
                if preset_key in main.presets:
                    if not question_box("Overwrite preset '" + str(preset_key) + "'?", 65, 15):
                        continue
                main.presets[preset_key] = {}  # {"main_folder": values["-MAIN-FOLDER-"], "backup_folders": []}
                main.presets[preset_key]["main_folder"] = values["-MAIN-FOLDER-"]
                main.presets[preset_key]["backup_folders"] = window["-BACKUP-LIST-"].get_list_values()
                if len(main.presets[preset_key]["backup_folders"]) == 0:
                    window["-ERROR-TEXT-"].update("Enter at least one backup folder")
                    del main.presets[preset_key]
                    continue
                else:
                    refresh_presets_list(window, main.presets)
                    saving.save_presets_to_config(main.presets)
                    preset_name = values["-CURRENT-PRESET-NAME-"]
                    window["-PRESET LIST-"].set_value(preset_name)
                    print("Saved Preset: " + str(preset_key))

        elif event == "-BACKUP-LIST-":  # A backup location was chosen from the listbox on the right
            # list_values = window["-BACKUP-LIST-"].get_list_values()
            if len(values["-BACKUP-LIST-"]) > 0:
                clicked_key = str(values["-BACKUP-LIST-"][0])
                window["-NEW-BACKUP-LOCATION-"].update(value=values["-BACKUP-LIST-"][0])
        elif event == "-PRESET LIST-":  # A file was chosen from the listbox on the left
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


def clear_backup_locations_box(window):
    window["-BACKUP-LIST-"].update(values=[])


def clear_preset_info(window):
    window["-MAIN-FOLDER-"].update("")
    clear_backup_locations_box(window)
    window["-CURRENT-PRESET-NAME-"].update("")
    window["-NEW-BACKUP-LOCATION-"].update("")


def set_loading_bar_visible(window, value):
    window["-BAR-"].update(visible=value)
    window[" "].update(visible=value)
    # window["Cancel"].update(visible=value)


def refresh_backup_locations_list(window, backup_locations):
    """ Updates the list of backup locations in the right column """
    backup_location_keys = []
    for location in backup_locations:
        backup_location_keys.append(str(location))
    window["-BACKUP-LIST-"].update(values=backup_location_keys)


def refresh_presets_list(window, presets):
    """ Updates the list of backup presets in the left column """
    preset_keys = []
    for key in presets:
        preset_keys.append(str(key))
    window["-PRESET LIST-"].update(values=preset_keys)


def show_settings_box():
    global previous_skip_folders
    previous_skip_files = copy.copy(files.skip_files)

    # region 1. layout

    layout = [
        [gui.Text('Settings:')],
        [gui.Frame('', [[gui.Text("Max number of log files: "),
                         gui.Input("", size=(14, 1), key="-MAX-LOG-FILES-")]], border_width=0)],
        [gui.Frame('', [[gui.Text("Do not log backups: "),
                         gui.Checkbox("", size=(14, 1), key="-DO-NOT-LOG-")]], border_width=0)],
        [gui.Frame('', [[gui.Text("Recycle/Trash deleted files: "),
                         gui.Checkbox("", size=(14, 1), key="-DELETE-FILES-")]], border_width=0)],

        # IGNORE FILE
        [gui.Frame('', [[gui.Text("File names to ignore: ", size=(20, 1))]], title_color='yellow', border_width=0)],
        [gui.Frame('', [[gui.Listbox(
            values=files.skip_files, enable_events=True, size=(30, 10), key="-IGNORED-FILES-"
        )]], border_width=0)],

        [gui.Frame('',
                   [[gui.Text("Ignore File Name:", size=(16, 1)), gui.Input("", size=(14, 1), key="-IGNORE-FILENAME-"),
                     gui.Button("Add", size=(14, 1), key="-ADD-IGNORED-"),
                     gui.Button("Remove", size=(14, 1), key="-REMOVE-IGNORED-")]], border_width=0)],

        # IGNORE FOLDER
        [gui.Frame('', [[gui.Text("Folder names to ignore:", size=(20, 1))]], title_color='yellow', border_width=0)],
        [gui.Frame('', [[gui.Listbox(
            values=files.skip_folders, enable_events=True, size=(30, 10), key="-IGNORED-FOLDERS-"
        )]], border_width=0)],

        [gui.Frame('',
                   [[gui.Text("Ignore Folder Name:", size=(16, 1)), gui.Input("", size=(14, 1), key="-IGNORE-FOLDER-"),
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

    # endregion

    # previous_logfilemax = copy.copy(logfilemax)
    window["-MAX-LOG-FILES-"].update(str(logging.log_file_max))
    # previous_no_logging = copy.copy(no_logging)
    window["-DO-NOT-LOG-"].update(logging.no_logging)
    window["-DELETE-FILES-"].update(files.delete_files)
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
                if files.skip_folders[i] == to_remove:  # if file to remove found
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
            files.delete_files = values["-DELETE-FILES-"]
            logging.log_file_max = int(values["-MAX-LOG-FILES-"])
            saving.save_settings_to_config()
            break
        if event == "Apply":
            logging.no_logging = values["-DO-NOT-LOG-"]
            logging.log_file_max = int(values["-MAX-LOG-FILES-"])
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


def question_box_with_radio(question, radio_text, radio_value, x_size, y_size):
    """ Opens a binary question box with a radio button and returns a tuple with the two booleans """
    layout = [
        [gui.Text(str(question))],
        [gui.Frame('', [[gui.Button("Yes", size=(5, 1)),
                         gui.Button("No", size=(5, 1))],
                        [gui.Checkbox(radio_text, default=radio_value, key="Cleanup")]],
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
    return answered_yes, values["Cleanup"]


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


def bool_to_str(state):
    if state:
        return "On"
    else:
        return "Off"


def print_settings():
    saving.load_settings_from_config()
    msg = "-----------------------------------SETTINGS-------------------------------------\n"
    msg += "Max number of log files: " + str(logging.log_file_max) + "\n\n"
    msg += "Do not log backups: " + bool_to_str(logging.no_logging) + "\n\n"
    msg += "Recycle/Trash deleted files: " + bool_to_str(files.delete_files) + "\n\n"
    msg += "File Names to ignore: \n"
    if len(files.skip_files) == 0:
        msg += "    [None]\n"
    else:
        for name in files.skip_files:
            msg += "    " + name + "\n"
    msg += "\n"
    msg += "Folder Names to ignore: \n"
    if len(files.skip_folders) == 0:
        msg += "    [None]\n"
    else:
        for name in files.skip_folders:
            msg += "    " + name + "\n"
    msg += "--------------------------------------------------------------------------------"

    print(msg)


def print_help_commands(print_in_console):
    msg = "--------------------------------------------------------------------------------\n" \
          " EZ Folder Backup Parameters:                                                 \n" \
          "                                                                              \n" \
          "-cleanup on..........................Toggles on deletion of files that no     \n" \
          "                                     longer exist in the main folder.         \n" \
          "-cleanup off.........................Toggles off deletion of files that no    \n" \
          "                                     longer exist in the main folder.         \n" \
          "-createpreset name -m path -b path...Creates a preset with the input name,    \n" \
          "                                     main folder, and up to five backup       \n" \
          "                                     folder paths that are preceded by -b.    \n" \
          "-deletepreset name...................Deletes the preset with the input name.  \n" \
          "-h...................................Show help menu and exit.                 \n" \
          "-hf..................................Creates a file help.txt containing the   \n" \
          "                                     help menu.                               \n" \
          "-logfilemax count....................Sets the maximum number of log files     \n" \
          "                                     before the oldest file is deleted.       \n" \
          "-movedown name.......................Moves the input preset down in the list. \n" \
          "-moveup name.........................Moves the input preset up in the list.   \n" \
          "-nologging on........................Toggles on stopping debug logs from being\n" \
          "                                     printed after backups.                   \n" \
          "-nologging off.......................Toggles off stopping debug logs from     \n" \
          "                                     being printed after backups.             \n" \
          "-runbackup -m path -b path...........Runs backup for main folder -m and up to \n" \
          "                                     five backup folders that are each        \n" \
          "                                     preceded by -b. Optionally add '-cleanup'\n" \
          "                                     to delete files that no longer exist in  \n" \
          "                                     the main folder.                         \n" \
          "-runbackupall........................Runs backup for every saved preset.      \n" \
          "                                     Optionally add '-cleanup' to delete files\n" \
          "                                     that no longer exist in the main folder. \n" \
          "-runpreset name......................Runs backup for the input preset.        \n" \
          "-skipfile add filename...............Skips this filename, use -skipfile once  \n" \
          "                                     per new filename to be skipped. Do not   \n" \
          "                                     enter a path, just the file name.        \n" \
          "-skipfile remove filename............Removes a skipped file name.             \n" \
          "-skipfolder add foldername...........Skips this folder name, use -skipfolder  \n" \
          "                                     once per new filename to be skipped. Do  \n" \
          "                                     not enter a path, just the folder name.  \n" \
          "-skipfolder remove foldername........Removes a skipped folder name.           \n" \
          "-skippath remove pathname............Removes a skipped path name.             \n" \
          "-support.............................Show support email for questions.        \n" \
          "-version.............................Show the current version of this program.\n" \
          "-viewlog.............................Show latest log file.                    \n" \
          "-viewpresets.........................Shows all presets.                       \n" \
          "-viewsettings........................Shows the current settings.              \n" \
          "                                                                              \n" \
          "To make a donation, please visit https://ko-fi.com/jcecode                    \n" \
          "--------------------------------------------------------------------------------\n"

    # ^^ maybe implement later
    #  "-skippath add pathname...............Skips this specific location on your     \n" \
    #  "                                     system from being checked for backup.    \n" \
    #  "                                     Either a file or a folder.               \n" \

    if print_in_console:
        print(msg)
    return msg


def create_help_file():
    help_file_text = print_help_commands(False)
    with open("help.txt", "w",
              encoding="utf-8") as f:
        f.write(help_file_text)
