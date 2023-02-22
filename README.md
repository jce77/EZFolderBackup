# EZ Folder Backup

## About
_**EZ Folder Backup**_ is a versatile free open-source local file backup tool
for Windows and Linux operating systems with a graphical interface for standard users and
extensive command-line run parameters for advanced users. 

The latest version can be found [here](https://github.com/jce77/EZFolderBackup).

## Running Instructions:
- Running on Windows with graphics (easy way):
  - Download all project files, images folder is needed at least.
  - Run _EZ Folder Backup.exe_ inside the _build_ folder. 
- Running with graphics by compiling python files:
  - Download dependencies on pip:
    - _PySimpleGUI_: `$ pip install pysimplegui `
    - _send2trash_: `$ pip install send2trash `
  - If using Linux also download tkinter directly to your OS
    - If using Ubuntu Linux with apt:
      - `$ sudo apt-get install python3-tk`
    - Otherwise if using a Linux distribution with dnf:
      - `$ sudo dnf install python3-tkinter`
  - Start program by running `python3 main.py`
- Running command-line only by compiling python files:
  - Download dependencies on pip:
      - _send2trash_: `$ pip install send2trash`, its optional to skip downloading this, but not recommended. 
  - See all commands by running `python3 main.py -help`.
  - See _Basic Usage Command-Line Only_ below for further instructions. 

## Basic Usage With Graphical Interface
- Enter the _main folder_ which you want to be protected by this backup.
- On the right enter a _backup location_ and click the _add_ button. This will become
a clone of the _main folder_, and multiple _backup locations_ can be added. 
- Enter the _preset name_, a label for this _main folder_'s backup operation.
- Click _Save_ to save this preset for future backups. 
- Check _Settings_ menu for other options.
- Click _Run Backup_ and follow prompts.
- Click the X button to pause/cancel the backup if needed.
- Click _View Backup Log_ to show the results of the backup afterwards.

## Basic Usage Command-Line Only
- Note: Command `python` may be `python3` depending on the operating system.
- View all commands: `$ python main.py -help` or look below at the *All Run Parameters* section.
- Create a backup preset:
  - `$ python main.py -createpreset MyBackup -m path1 -b path2`
  - The path after `-m` is the main folder that you want to backup. The path
after `-b` is the folder you want the main folder copied into, this can be repeated if multiple backup locations are required, each location will require `-b` preceding it. 
- Run the backup preset: 
  - `$ python main.py -runpreset MyBackup`
- View the results:
  - ` $ python main.py -viewlog`

## Graphical Interface Usage Video
[![Windows Usage](http://img.youtube.com/vi/3_gKugIbbsE/0.jpg)](https://youtu.be/3_gKugIbbsE "Graphical Interface Usage Video")

## Command-Line Usage Video
[![Windows Usage](http://img.youtube.com/vi/gIA1575mpTo/0.jpg)](https://youtu.be/gIA1575mpTo "Command-Line Usage Video")

## All Run Parameters
 
`-createpreset name -m path -b path` Creates a preset with a name, main folder and one or more backup folders that are each preceded by `-b`.          
`-deletepreset name.` Deletes the preset with the input name.  
`-h` Show help menu and exit.                 
`-hf` Creates a file help.txt containing the help menu.                               
`-logfilemax count` Sets the maximum number of log files before the oldest file is always deleted.  
`-movedown name` Moves the input preset down in the list.  
`-moveup name` Moves the input preset up in the list.   
`-nologging on` Backups will not create log files.       
`-nologging off` Each backup will create a log file.      
`-runbackup -m path -b path` Runs backup for main folder `-m` and one or more backup folders that are each preceded by `-b.`                         
`-runbackupall` Runs backup for every saved preset.      
`-runpreset name` Runs backup for the input preset name.   
`-skipfile add filename` Skips this filename, use `-skipfile` once per new filename to be skipped. Do not enter a path, just the file name.        
`-skipfile remove filename` Removes a skipped file name.             
`-skipfolder add foldername` Skips this folder name, use `-skipfolder` once per new filename to be skipped. Do not enter a path, just the folder name.  
`-skipfolder remove foldername` Removes a skipped folder name.           
`-support` Show support email for questions.        
`-trashfiles on` Toggles on recycling/trashing of files that no longer exist in the main folder.  
`-trashfiles off` Toggles off recycling/trashing of files that no longer exist in the main folder.   
`-version` Show the current version of this program.  
`-viewlog` Show the latest log file.                    
`-viewpresets` Shows all presets.                       
`-viewsettings` Shows the current settings.

For updates and documentation, please visit: [https://github.com/jce77/EZFolderBackup  ](https://github.com/jce77/EZFolderBackup  )

To make a donation, please visit: [https://ko-fi.com/jcecode](https://ko-fi.com/jcecode)

--------------------------------------------------------------------------------

