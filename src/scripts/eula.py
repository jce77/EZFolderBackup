from scripts import program as main
from scripts import ui


def eula_agreed_to():
    """ Returns True if the eula has already been agreed to """
    with open("EULA.txt", "r", encoding="utf-8") as f:
        line_count = 1
        for line in f:
            if 'agree=yes\n' == line.lower():
                return True
            if line_count > 1:
                break
            line_count += 1
    return False


def get_eula_text():
    eula_text = "--------------------------------------------------------------------------------\n"
    eula_text += 'MIT License\n\n'
    eula_text += 'Copyright (c) 2022 jce77\n\n'
    eula_text += 'Permission is hereby granted, free of charge, to any person obtaining a copy \n'
    eula_text += 'of this software and associated documentation files (the "Software"), to deal\n'
    eula_text += 'in the Software without restriction, including without limitation the rights \n'
    eula_text += 'to use, copy, modify, merge, publish, distribute, sublicense, and/or sell  \n'
    eula_text += 'copies of the Software, and to permit persons to whom the Software is \n'
    eula_text += 'furnished to do so, subject to the following conditions:\n\n'
    eula_text += 'The above copyright notice and this permission notice shall be included in \n'
    eula_text += 'all copies or substantial portions of the Software.\n\n'
    eula_text += 'THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\n'
    eula_text += 'IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\n'
    eula_text += 'FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\n'
    eula_text += 'AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\n'
    eula_text += 'LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\n'
    eula_text += 'OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\n'
    eula_text += 'SOFTWARE.\n'
    eula_text += "--------------------------------------------------------------------------------\n"
    eula_text += '\n'
    return eula_text


def agreed_to_eula(agreed):
    """ Updates EULA.txt to show that the EULA has been agreed to """
    eula_text = ""
    if agreed:
        eula_text += "Agree=Yes\n"
    else:
        eula_text += "Agree=No\n"
    eula_text += "Type Agree=Yes on the top line to show you have read the MIT License agreement and agree with its terms:\n\n"
    eula_text += get_eula_text()
    with open("EULA.txt", "w", encoding="utf-8") as f:
        f.write(eula_text)


def show_eula_gui():
    """ Open the eula agreement gui """
    eula = ""
    with open('EULA.txt') as f:
        eula += str(f.readlines())
    layout = [
        [ui.gui.Text("                            EULA AGREEMENT:")],
        [ui.gui.Multiline('MIT License\n\n'
                       'Copyright (c) 2022 jce77\n\n'
                       'Permission is hereby granted, free of charge, to any person obtaining a copy of this software and '
                       'associated documentation files (the "Software"), to deal in the Software without restriction, '
                       'including without limitation the rights to use, copy, modify, merge, publish, distribute, '
                       'sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is '
                       'furnished to do so, subject to the following conditions:\n\n'
                       'The above copyright notice and this permission notice shall be included in all'
                       'copies or substantial portions of the Software.\n\n'
                       'THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR'
                       'IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,'
                       'FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE'
                       'AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER'
                       'LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,'
                       'OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE'
                       'SOFTWARE.'
                       , size=(50, 25), background_color='grey30', text_color='grey95', disabled=True)],
        [ui.gui.Button("I Agree")],
        [ui.gui.Button("I Do Not Agree")]
    ]
    window = ui.gui.Window("EZ Folder Backup", layout, icon=main.icon_file, margins=(55, 55))
    exit_app = False
    while True:
        event, values = window.read()
        if event == "I Do Not Agree" or event == ui.gui.WIN_CLOSED:
            exit_app = True
            break
        if event == "I Agree" or event == ui.gui.WIN_CLOSED:
            break
    window.close()
    return exit_app