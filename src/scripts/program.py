from scripts import eula
from scripts import ui
from scripts import saving
from scripts import logging
from scripts import files
import sys
from sys import platform
from os.path import exists

all_commands = ["-createpreset", "-b", "-deletepreset", "-h", "-help", "-hf", "-logfilemax", "-m", "-moveup",
                "-movedown",
                "-nologging", "-runbackup", "-runpreset", "-skipfile", "-support", "-version", "-viewlog",
                "-viewpresets", "-skipfolder"]
backup_folders = []

main_folder = ""

presets = {}
icon_file = ""
version = "1.0.5"
using_windows = False


def run_backup(window, main_folder, backup_folders):
    """ Ensures the input backup_folders are all exact clones of the input main_folder """
    use_graphics = type(window) != int
    global using_windows
    logging.log_file = "Backup Log For Main Folder:\n"
    logging.log_file += main_folder + "\n\n"
    if not exists(main_folder):
        if use_graphics:
            window["-ERROR-TEXT-"].update("The main folder was not found")
            logging.log_file += "The main folder was not found\n"
            logging.print_to_log("Main_Not_Found", logging.log_file)
            return
    for i in range(len(backup_folders)):
        backup_folders[i] = backup_folders[i].replace("/", "\\")
    # getting all file paths in the main storage directory
    list_of_files = files.get_all_filenames(main_folder)
    # formatting names
    list_of_files = files.remove_path_to_root_folder_from_each(main_folder, list_of_files)
    # comparing the other directories and deleting files that no longer exist
    error_msg = ""
    response = ""
    for backup_directory in backup_folders:
        response = files.copy_from_main_to_backup_directory(use_graphics, window, main_folder, list_of_files,
                                                            backup_directory, using_windows)
        if "NOT FOUND" in response:
            error_msg = response
    if use_graphics:
        if error_msg == "":
            window["-ERROR-TEXT-"].update(response)
        else:
            window["-ERROR-TEXT-"].update(error_msg)
    # debug log
    logging.print_to_log("Backup", logging.log_file)


def run_commands(commands):
    """ Running commands that were input as parameters in the console """
    global main_folder
    # global no_logging
    # global log_file_max_count
    global presets
    presets = saving.load_presets()
    files.skip_files = []
    files.skip_folders = []
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
                    msg = saving.print_presets(presets, False) + "\n\n"
                    msg += "The preset entered '" + cmd[1] + "' could not be found. Cannot do move operation.\n"
                    print(msg)
                    sys.exit(1)
                presets = files.move_index_in_dict(presets, cmd[1], True)
                # ensure changes are persistent
                saving.save_presets_to_config(presets)
    if "-movedown" in keys:
        for cmd in commands:
            if cmd[0] == "-movedown":
                if len(cmd[1]) == 0:
                    print("-movedown requires a preset name.")
                    sys.exit(1)
                if cmd[1] not in presets:
                    msg = saving.print_presets(presets, False) + "\n\n"
                    msg += "The preset entered '" + cmd[1] + "' could not be found. Cannot do move operation.\n"
                    print(msg)
                    sys.exit(1)
                presets = files.move_index_in_dict(presets, cmd[1], False)
                # ensure changes are persistent
                saving.save_presets_to_config(presets)
    if "-support" in keys:
        print("For questions or to report bugs please email help.jcecode@yahoo.com")
    if "-version" in keys:
        global version
        print("v" + version)
    if "-viewpresets" in keys:
        saving.print_presets(presets, True)
    if "-viewlog" in keys:
        logging.print_last_log_file()
    if "-h" in keys or "-help" in keys:
        ui.print_help_commands(True)
    if "-hf" in keys:
        ui.create_help_file()
        print("Created help.txt containing all commands.")
    if "-logfilemax" in keys:
        for cmd in commands:
            if cmd[0] == "-logfilemax":
                logging.log_file_max_count = int(cmd[1])
    if "-nologging" in keys:
        logging.no_logging = True
    if "-skipfile" in keys:
        for cmd in commands:
            if cmd[0] == "-skipfile":
                files.skip_files.append(cmd[1])
    if "-skipfolder" in keys:
        for cmd in commands:
            if cmd[0] == "-skipfolder":
                files.skip_folders.append(cmd[1])
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
        saving.save_presets_to_config(presets)
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
            saving.save_presets_to_config(presets)
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
            msg = saving.print_presets(presets, False) + "\n\n"
            msg += "The preset entered '" + preset_key + "' could not be found. Cancelling backup. All presets have " \
                                                         "been listed above.\n"
            print(msg)
            sys.exit(1)
        preset = presets[preset_key]
        run_backup(0, preset["main_folder"], preset["backup_folders"])


def start():
    global using_windows
    using_windows = False
    if 'win32' in platform or 'win64' in platform:
        using_windows = True
    ui.using_gui = False
    if len(sys.argv) == 1:
        ui.using_gui = True
    if not exists("EULA.txt"):
        eula.agreed_to_eula(False)
    # Running with graphics
    if ui.using_gui:
        if not eula.eula_agreed_to():
            exit_app = eula.show_eula_gui()
            if exit_app:
                logging.print_to_log('Failed_To_Run',
                                     'Agree to the EULA agreement in the file EULA.txt before using this please')
                print('Agree to the EULA before using this software please')
                sys.exit(1)
        eula.agreed_to_eula(True)
        try:
            if ui.gui.WIN_CLOSED:
                pass
        except:
            print("PySimpleGui is not installed, please install using pip before using the graphical interface.\n "
                  "Otherwise run the parameter -help to see all command line-only parameters")
            sys.exit(1)
        # only loading settings in the GUI for now, otherwise they must be entered with run command
        # to be used
        saving.load_settings_from_config()
        ui.show_gui()
    # Running with command-line parameters only
    else:
        if not eula.eula_agreed_to():
            print(eula.get_eula_text())
            print("Enter 'Yes' to confirm that you have read licence above and agree with its terms: ")
            result = input()
            if result.lower() == "yes":
                eula.agreed_to_eula(True)
            else:
                print("Please agree to EULA before using the program. Thank you.")
                sys.exit(0)
        commands = saving.sort_arguments(sys.argv)
        run_commands(commands)
