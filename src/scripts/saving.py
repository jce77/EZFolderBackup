from os.path import exists
import os
from scripts import program as main
from scripts import files
from scripts import logging

all_commands = ["-createpreset", "-b", "-deletepreset", "-h", "-help", "-hf", "-logfilemax", "-m", "-moveup",
                "-movedown", "-cleanup",
                "-nologging", "-runbackup", "-runpreset", "-skipfile", "-support", "-version", "-viewlog",
                "-viewpresets", "-skipfolder"]


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


def position_in_presets(preset_name):
    """ Returns index in list of presets, or -1 if not found """
    if not exists('presets/presets.cfg'):
        print("Presets file does not exist")
        return -1
    position = -1
    with open('presets/presets.cfg', 'r') as f:
        for line in f:
            line = line.strip()
            if 'preset=' in line:
                position += 1
                if line[7: len(line)].strip() == preset_name:
                    return position
    # not found
    print("Preset not found")
    return -1


def load_settings_from_config():
    if exists('settings.cfg'):
        files.skip_files = []
        files.skip_folders = []
        with open('settings.cfg', 'r') as f:
            for line in f:
                line = line.strip()
                if 'log_file_max=' in line:
                    # logging.log_file_max = int(line[13: len(line)])
                    logging.log_file_max = int(line[13: len(line)].strip())
                elif 'no_logging=' in line:
                    logging.no_logging = line[11: len(line)] == 'True'
                elif 'skip_file=' in line:
                    files.skip_files.append(line[10: len(line)])
                elif 'skip_folder=' in line:
                    files.skip_folders.append(line[12: len(line)])
                elif 'cleanup=' in line:
                    files.delete_files = line[8: len(line)] == 'True'
    else:
        files.skip_files = []
        files.skip_folders = []
        files.delete_files = False
        # save default settings to the config
        save_settings_to_config()


def save_settings_to_config():
    settings = "log_file_max=" + str(logging.log_file_max) + "\n"
    settings += "no_logging=" + str(logging.no_logging) + "\n"
    settings += "cleanup=" + str(files.delete_files) + "\n"
    for file in files.skip_files:
        settings += "skip_file=" + file + "\n"
    for folder_name in files.skip_folders:
        settings += "skip_folder=" + folder_name + "\n"
    with open('settings.cfg', 'w') as f:
        f.write(settings)


def save_presets_to_config(presets):
    """ Saves the input backup presets to the presets.cfg file """
    files.backup_file('presets/presets.cfg.old')
    files.backup_file('presets/presets.cfg')
    lines = ""
    for preset in presets:
        lines += "preset=" + preset + "\n"
        lines += "main_folder=" + str(presets[preset]["main_folder"]).replace("/", "\\") + "\n"
        for backup_folder in presets[preset]["backup_folders"]:
            lines += "backup_folder=" + str(backup_folder).replace("/", "\\") + "\n"
    with open('presets/presets.cfg', 'w') as f:
        f.write(lines)


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
    main.presets[name] = {'main_folder': main_folder, 'backup_folders': backup_folders}


def delete_preset(name):
    del main.presets[name]


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
