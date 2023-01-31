# EZ Folder Backup

## About
_**EZ Folder Backup**_ is a free local file backup tool for Windows and Linux that 
ensures backup folders are exact clones of a folder you want to protect. 
Either using a graphical interface or command-line parameters you can easily ensure
all changes made are forced on the backup folders automatically including new files 
and deleted files. 

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
- Enter the _main folder_ which you want to be backed up to another location.
- Enter one to five _backup locations_ that will become duplicates of the main folder.
- Enter a _backup preset name_.
- Click _Save_ to save these settings. 
- Click _Backup Files_.
- Click _View Backup Log_ to show the results of the backup.

## Basic Usage Command-Line Only
- View all commands: `$ python main.py -help`
- Create a backup preset. _path1_ is the _main folder_ that you want to back up, and 
  _path2_ is the folder that will become an exact duplicate of the _main folder_. The
  `-b` command paired with a path can be repeated up to five fimes.
  
  - `$ python main.py -createpreset MyBackup -m path1 -b path2`
- Run the backup: `$ python main.py -runpreset MyBackup`
- View the results: ` $ python main.py -viewlog`

## Getting Started Video For Both Windows and Linux
[![Windows Usage](http://img.youtube.com/vi/jmEQumGNg7o/0.jpg)](https://youtu.be/jmEQumGNg7o "Getting Started")


