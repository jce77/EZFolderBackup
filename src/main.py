"""
EZ Folder Backup v1.1.4

Update v1.1.4
- Added setting to make deleting files optional, and off by default
- Deleting a preset now clears its backup locations and name
- Added a button to run every single backup preset
- Added command-line option to toggle on and off cleanup and nologging






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
from scripts import program
import sys


def testing_start(arguments):
    """ For Running Unit Tests """
    # print("START: " + str(arguments))
    program.start(arguments)


if __name__ == '__main__':
    program.start(sys.argv)


