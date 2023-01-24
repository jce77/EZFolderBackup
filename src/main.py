"""
EZ Folder Backup v1.0.7

Update v1.0.7
- Fixed a problem with the GUI not properly showing the current operation
- Added a loading bar for backup operations
- Added a cancel button for backup operations that pauses and prompts further confirmation

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

