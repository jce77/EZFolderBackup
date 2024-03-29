"""
EZ Folder Backup v1.1.7

Update v1.1.7
- Backup locations will now be created automatically if the root folder does not exist, otherwise
will be skipped if the drive is unplugged



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


