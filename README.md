# EZ File Backup

## Running Instructions:
- Windows
  - Run _EZ Folder Backup.exe_
- Running on Linux with command line only:
  - View all commands with:
  - $ python main.py -help
- Running on Ubuntu Linux with graphics:
  - Install _PySimpleGUI_ on pip:
    - $ pip install pysimplegui 
  - Install _tkinter_ on your OS:
    - If using Ubuntu Linux with apt:
      - $ sudo apt-get install python3-tk
    - If using Fedora Linux with dnf:
      - $ sudo dnf install python3-tkinter
  - Run with:
    - $ python3 main.py

## Basic Usage With Graphical Interface
- Enter the _main folder_ which is what you want to back up.
- Enter one to five _backup locations_ that will become duplicates of the main folder.
- Enter a _backup preset name_.
- Click _Save_ if needed. 
- Click _Backup Files_.
- Click _View Backup Log_ to show the results of the backup.

## Basic Usage Command-Line Only
- Create a backup preset. _path1_ is the main folder that you want to back up, and _path2_ is the folder that will become an exact duplicate of the main folder.
  - $ python main.py -createpreset MyBackup -m path1 -b path2
- Run the backup
  - $ python main.py -runpreset MyBackup
- View the results
  - $ python main.py -viewlog
- View all commands to see other options
  - $ python main.py -help


## Getting Started Video For Both Windows and Linux
[![Windows Usage](http://img.youtube.com/vi/wE98Zrmvr-k/0.jpg)](https://youtu.be/wE98Zrmvr-k "Getting Started")


