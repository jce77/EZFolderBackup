# EZ Folder Backup

## About
_**EZ Folder Backup**_ is a versatile open-source local file backup tool
for Windows and Linux operating systems with a graphical interface for standard users and
extensive command-line run parameters for advanced users. 

The latest version can be found [here](https://github.com/jce77/EZFolderBackup).

## Running Instructions:
- Running on Windows:
  - Ensure the _images_ folder is in the same folder as the included .exe file
  - Run _EZ Folder Backup.exe_
- Running on Linux with command line only:
  - (Optional) Install _send2trash_ on pip: `$ pip install send2trash `
  - View all commands with: `$ python3 main.py -help`, more in-depth instructions are below.
- Running on Ubuntu Linux with graphics:
  - Ensure the _images_ folder is in the same folder as _main.py_
  - Install _PySimpleGUI_ on pip: `$ pip install pysimplegui `
  - Install _send2trash_ on pip: `$ pip install send2trash `
  - Install _tkinter_ on your OS:
    - If using Ubuntu Linux with apt:
      - `$ sudo apt-get install python3-tk`
    - Otherwise if using a Linux distribution with dnf:
      - `$ sudo dnf install python3-tkinter`
  - Run with: `$ python3 main.py`

## Basic Usage With Graphical Interface
- Enter the _main folder_ which you want to be protected by this backup.
- On the right enter a _backup location_ and click the _add_ button. This will become
a clone of the _main folder_, and multiple _backup locations_ can be added. 
- Enter a _preset name_, specifically a label for this main folder's backup operation.
- Click _Save_ to save these settings for future backups. 
- Check _Settings_ menu for other options.
- Click _Run Backup_.
- Click _View Backup Log_ to show the results of the backup.

## Basic Usage Command-Line Only
- View all commands: `$ python main.py -help` or look below at *All Run Parameters* section.
- Create a backup preset. _path1_ is the _main folder_ that you want to back up, and 
  _path2_ is the folder that will become an exact duplicate of the _main folder_. The
  `-b` command paired with a path can be repeated up to five fimes.
  
  - `$ python main.py -createpreset MyBackup -m path1 -b path2`
- Run the backup: `$ python main.py -runpreset MyBackup`
- View the results: ` $ python main.py -viewlog`

## Getting Started Video For Both Windows and Linux
[![Windows Usage](http://img.youtube.com/vi/jmEQumGNg7o/0.jpg)](https://youtu.be/jmEQumGNg7o "Getting Started")

## All Run Parameters
 
`-cleanup on` Toggles on deletion of files that no longer exist in the main folder.         
`-cleanup off` Toggles off deletion of files that no longer exist in the main folder.         
`-createpreset name -m path -b path` Creates a preset with the input name, main folder, and up to five backup folder paths that are preceded by -b.    
`-deletepreset name` Deletes the preset with the input name.  
`-h` Show help menu and exit.                 
`-hf` Creates a file help.txt containing the help menu.                               
`-logfilemax count` Sets the maximum number of log files before the oldest file is deleted.       
`-movedown name` Moves the input preset down in the list.       
`-moveup name` Moves the input preset up in the list.       
`-nologging on` Toggles on stopping debug logs from being printed after backups.                   
`-nologging off` Toggles off stopping debug logs from being printed after backups.             
`-runbackup -m path -b path` Runs backup for main folder -m and up to five backup folders that are each preceded by -b. Optionally add '-cleanup' to delete files that no longer exist in the main folder.                         
`-runbackupall` Runs backup for every saved preset. Optionally add '-cleanup' to delete files that no longer exist in the main folder.        
`-runpreset name` Runs backup for the input preset.        
`-skipfile add filename` Skips this filename, use -skipfile once per new filename to be skipped. Do not enter a path, just the file name.        
`-skipfile remove filename` Removes a skipped file name.             
`-skipfolder add foldername` Skips this folder name, use -skipfolder once per new filename to be skipped. Do not enter a path, just the folder name.  
`-skipfolder remove foldername` Removes a skipped folder name.           
`-skippath remove pathname` Removes a skipped path name.             
`-support` Show support email for questions.        
`-version` Show the current version of this program.        
`-viewlog` Show latest log file.                    
`-viewpresets` Shows all presets.                       
`-viewsettings` Shows the current settings.

For updates and documentation, please visit: [https://github.com/jce77/EZFolderBackup  ](https://github.com/jce77/EZFolderBackup  )

To make a donation, please visit: [https://ko-fi.com/jcecode](https://ko-fi.com/jcecode)

--------------------------------------------------------------------------------

