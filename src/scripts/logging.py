from os.path import exists
import os
from datetime import datetime
from send2trash import send2trash

no_logging = False  # If true no log files will be created, False by default
log_file = ""
log_file_max_count = 50  # starts deleting the oldest file once 50 logs exist


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
        # os.remove("log/" + oldest_file)
        send2trash("log/" + oldest_file)


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
