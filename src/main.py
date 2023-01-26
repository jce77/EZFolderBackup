"""
EZ Folder Backup v1.1.2

Update v1.1.2
- Added a trash function that replaces send2trash if its not installed, specifically to work with a fresh Ubuntu install
- Fixed a number of errors preventing command-line backing up from running


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


if __name__ == '__main__':
    program.start()

