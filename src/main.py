"""
EZ Folder Backup v1.1.3

Update v1.1.3
- GUI no longer freezes when clicked during a length copy operation
- Pausing the backup waits until the current copy is finished to pause
- Preset stays highlighted after saving now


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

