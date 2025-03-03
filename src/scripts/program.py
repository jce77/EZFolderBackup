import os
from scripts import eula
from scripts import ui
from scripts import saving
from scripts import logging
from scripts import files
from scripts import trash
import sys
from sys import platform
from os.path import exists

backup_folders = []

main_folder = ""

presets = {}
icon_file = ""
version = "1.1.6"
using_windows = False


def backup_operation(window, main_folder, backup_folders):
    """ Ensures the input backup_folders are all exact clones of the input main_folder """
    global using_windows
    # checking for main folder
    if not exists(main_folder):
        error_text = "The main folder was not found"
        if ui.using_gui:
            window["-ERROR-TEXT-"].update(error_text)
            window.refresh()
        print(error_text)
        logging.log_file += error_text + "\n"
        logging.print_log("Main_Folder_Not_Found")
        return "MAIN FOLDER NOT FOUND"
    # formatting input
    main_folder = files.format_text(main_folder, using_windows)
    for i in range(len(backup_folders)):
        backup_folders[i] = files.format_text(backup_folders[i], using_windows)
    # response to user
    if ui.using_gui:
        window["-ERROR-TEXT-"].update("Calculating backup... ")
    print("Calculating backup... ")
    # getting and formatting files in main folder
    list_of_files_to_backup = files.get_all_filenames(main_folder)
    list_of_files_to_backup = files.remove_path_to_root_folder_from_each(main_folder, list_of_files_to_backup)
    for i in range(len(list_of_files_to_backup)):
        list_of_files_to_backup[i] = files.format_text(list_of_files_to_backup[i], using_windows)

    # comparing the other directories and deleting files that no longer exist
    error_msg = ""
    response = ""
    count = -1
    if ui.using_gui:
        list_values = window["-BACKUP-LIST-"].get_list_values()
    for path in backup_folders:
        count += 1
        backup_directory = files.format_text(path, using_windows)

        # if backup folder does not exist, try to create it
        if not exists(backup_directory):
            try:
                # added a filename here because otherwise it assures a path to the folder above the directory
                files.assure_path_to_file_exists(backup_directory + "/file.b")
                logging.log_file += "Created directory: '" + backup_directory + "'." + "\n"
                print("Created directory: '" + backup_directory + "'." + "\n")
            except (FileNotFoundError, PermissionError):
                # the drive is not plugged in
                logging.log_file += "Skipping, drive not plugged in for : '" + backup_directory + "'." + "\n"
                print("Skipping, drive not plugged in for : '" + backup_directory + "'." + "\n")
                continue
            # maybe add this in the future. github should remind me about this in the future.
            # except OSError:
            #     # the drive
            #     logging.log_file += "Skipping, OSError for : '" + backup_directory + "'. Possibly corruption." + "\n"
            #     print("Skipping, OSError for : '" + backup_directory + "'. Possibly corruption." + "\n")
            #     continue

        if ui.using_gui:
            window["-BACKUP-LIST-"].set_value(list_values[count])  # selecting the preset in the GUI
        response = files.copy_from_main_to_backup_directory(using_windows, ui.using_gui, window, main_folder,
                                                            list_of_files_to_backup, backup_directory)
        if "NOT FOUND" in response:
            error_msg = response
        elif "BACKUP CANCELLED" in response:
            if ui.using_gui:
                window["-ERROR-TEXT-"].update("Backup Cancelled")
            print("Backup Cancelled")
            logging.log_file += "\n-------------------------------\nBackup Cancelled\n-------------------------------"
            logging.print_log("Backup")
            return "BACKUP CANCELLED"
        elif "INSUFFICIENT SPACE" in response:
            if ui.using_gui:
                window["-ERROR-TEXT-"].update("Cancelled, Insufficient Space for: " + str(backup_directory))
            print("Backup Cancelled, Insufficient Space inside: " + str(backup_directory))
            logging.log_file += "\n\nInsufficient Space inside: " + str(backup_directory)
            logging.log_file += "\n--------------------\nBackup Cancelled\n--------------------------------"
            logging.print_log("Backup")
            return "INSUFFICIENT SPACE"

    if ui.using_gui:
        if response == "BACKUP SUCCESSFUL":
            if logging.error_count() != 0:
                response = "BACKUP SUCCESSFUL WITH ERRORS. View log for details."
        if error_msg == "":
            window["-ERROR-TEXT-"].update(response)
        else:
            window["-ERROR-TEXT-"].update(error_msg)
        window.refresh()
    return "BACKUP COMPLETE"


def run_backup_all(window):
    """ Backs up every saved preset """
    print("RUNBACKUPALL")
    global presets
    logging.restart_log()
    logging.log_file += "BACKING UP ALL PRESETS:\n"
    logging.log_file += "==============================================================\n"
    logging.log_file += "==============================================================\n"
    print("Backup up all presets: \n===========================")
    files.total_moved = 0
    files.total_trashed = 0
    files.total_copied = 0
    for preset in presets:
        print("Backing Up '" + str(preset) + "'")
        if ui.using_gui:
            window["-PRESET LIST-"].set_value(preset)  # selecting the preset in the GUI
            saving.load_selected_preset(presets[preset], window, preset)
        print("Backing Up '" + str(preset) + "'\n")
        logging.log_file += "Backing Up '" + str(preset) + "'\n"
        print(main_folder + "\n\n")
        logging.log_file += main_folder + "\n\n"
        response = backup_operation(window, presets[preset]['main_folder'], presets[preset]['backup_folders'])
        if "BACKUP CANCELLED" in response:
            if ui.using_gui:
                window["-ERROR-TEXT-"].update("Backup Cancelled")
            logging.log_file += "\n-------------------------------\nBackup Cancelled\n-------------------------------"
            logging.print_log("Backup")
            return
        logging.log_file += "-----------------------------------------------------------------------\n"
        print("-----------------------------------------------------------------------")
    logging.log_backup_totals(files.total_moved, files.total_trashed, files.total_copied)
    logging.log_file += logging.get_errors()
    print(logging.get_errors())
    logging.print_log("Backup")
    pass


def run_backup(window, main_folder, backup_folders):
    """ Ensures the input backup_folders are all exact clones of the input main_folder """
    logging.restart_log()
    logging.log_file += "Backup Log For Main Folder:\n"
    logging.log_file += main_folder + "\n\n"
    print("Backup Log For Main Folder:\n" + main_folder + "\n\n")
    files.total_moved = 0
    files.total_trashed = 0
    files.total_copied = 0
    backup_operation(window, main_folder, backup_folders)
    logging.log_backup_totals(files.total_moved, files.total_trashed, files.total_copied)
    logging.log_file += logging.get_errors()
    print(logging.get_errors())
    logging.print_log("Backup")


def run_commands(commands):
    """ Running commands that were input as parameters in the console """
    global using_windows
    global main_folder
    # global no_logging
    # global log_file_max
    global presets
    presets = saving.load_presets()
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
        print("-runbackup can only be run once at a time, use '-runbackupall' to back up multiple in one command.")
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
                saving.save_presets_to_config(presets, using_windows)
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
                saving.save_presets_to_config(presets, using_windows)
    if "-setuptestenv" in keys:
        file_size = 0
        for cmd in commands:
            if type(cmd) == list and cmd[0] == "-setuptestenv":
                if cmd[1] != '':
                    file_size = int(cmd[1])
                else:
                    file_size = 2500000  # default size
        presets = {}
        for i in range(5):
            test_dir = os.getcwd() + "/unit_test_files" + str(i)
            # test_dir = test_dir.replace("\\", "/")
            test_dir = files.format_text(test_dir, using_windows)
            files.fully_delete_path(test_dir)
            files.create_test_files(test_dir, file_size)
            backup_name = "Test Backup" + str(i)
            presets[backup_name] = {}
            presets[backup_name]["main_folder"] = test_dir + "/main"
            presets[backup_name]["backup_folders"] = [
                test_dir + "/b1",
                test_dir + "/b2",
                test_dir + "/b3",
                test_dir + "/b4",
                test_dir + "/b5"
            ]
        saving.save_presets_to_config(presets, using_windows)
    if "-removetestenv" in keys:
        print("Removing test environment...")
        for i in range(5):
            test_dir = os.getcwd() + "/unit_test_files" + str(i)
            # test_dir = test_dir.replace("\\", "/")
            test_dir = files.format_text(test_dir, using_windows)
            files.fully_delete_path(test_dir)
        presets = {}
        saving.save_presets_to_config(presets, using_windows)
    if "-support" in keys:
        print("For questions or to report bugs please email help.jcecode@yahoo.com")
    if "-version" in keys:
        global version
        print("v" + version)
    if "-viewsettings" in keys:
        ui.print_settings()
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
                logging.log_file_max = int(cmd[1])
    if "-nologging" in keys:
        for cmd in commands:
            if cmd[0] == "-nologging":
                logging.no_logging = cmd[1] == "on"
    if "-trashfiles" in keys:
        for cmd in commands:
            if cmd[0] == "-trashfiles":
                files.delete_files = cmd[1] == "on"
    if "-skipfile" in keys:
        for cmd in commands:
            if cmd[0] == "-skipfile":
                if cmd[1][0:3] == "add":
                    name = cmd[1][4:len(cmd[1])]
                    if name not in files.skip_files:
                        files.skip_files.append(name)
                elif cmd[1][0:6] == "remove":
                    remove = cmd[1][7:len(cmd[1])]
                    for i in range(len(files.skip_files)):
                        if files.skip_files[i] == remove:
                            del files.skip_files[i]
                else:
                    print("-skipfile requires the add or remove command, see -help for details.")
    if "-skipfolder" in keys:
        for cmd in commands:
            if cmd[0] == "-skipfolder":
                if cmd[1][0:3] == "add":
                    name = cmd[1][4:len(cmd[1])]
                    if name not in files.skip_folders:
                        files.skip_folders.append(name)
                elif cmd[1][0:6] == "remove":
                    remove = cmd[1][7:len(cmd[1])]
                    for i in range(len(files.skip_folders)):
                        if files.skip_folders[i] == remove:
                            del files.skip_folders[i]
                else:
                    print("-skipfolder requires the add or remove command, see -help for details.")
        # for cmd in commands:
        #     if cmd[0] == "-skipfolder":
        #         files.skip_folders.append(cmd[1])
    saving.save_settings_to_config()


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
        saving.save_presets_to_config(presets, using_windows)
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
            saving.save_presets_to_config(presets, using_windows)
        else:
            print("Key entered '" + preset_key + "' could not be found to be deleted.")
    # Backup All Presets
    if "-runbackupall" in keys:
        run_backup_all(0)
    # Backup With Input Folders
    elif "-runbackup" in keys:
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
    # Backup a saved preset
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


def start(arguments):
    global using_windows
    global clicked_cancel_button
    using_windows = False
    if 'win32' in platform or 'win64' in platform:
        using_windows = True
    ui.using_gui = False
    if len(arguments) == 1:
        ui.using_gui = True
    if not exists("EULA.txt"):
        eula.agreed_to_eula(False)
    # start trash script, otherwise stop if failed
    msg = trash.start(ui.using_gui, using_windows)
    if msg != "Passed":
        print(msg)
        logging.log_file += msg
        logging.print_log("Failed_To_Run")
        return

    # loading settings
    saving.load_settings_from_config()

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
        # saving.load_settings_from_config()
        ui.show_gui(using_windows)
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
        commands = saving.sort_arguments(arguments)
        run_commands(commands)
