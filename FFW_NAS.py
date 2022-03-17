from asyncio import subprocess
import sys, os
from tokenize import Number
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6 import QtGui, QtCore
import subprocess

import pathlib
import tempfile
import json
import shutil
import requests
import threading
import psutil

from ui_FFW_NAS import Ui_MainWindow
from ui_ERROR_MSG import Ui_ERROR_MSG

# Updater

global AktulleVersion
AktulleVersion = ""
JsonURL = 'https://3ddruck-mb.de/UpdateChecker/FFW_NAS_CheckforUpdate.json'
headersURL = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
paramURL = dict()
DownloadUpdateFileURL = 'https://3ddruck-mb.de/UpdateChecker/Update_FFW_NAS_Converter.zip'
global NeusteVersion
NeusteVersion = ""
pfad_updatepfad = str(pathlib.Path(__file__).parents[0]) + "/FFW_NAS_CheckforUpdate.json"

TempPath = str(pathlib.Path(tempfile.gettempdir() + "/Materialbestelltung_temp").absolute())
TempPathZIPFILE = str(pathlib.Path(tempfile.gettempdir() + "/Materialbestelltung_temp/Update_FFW_NAS_Converter.zip").absolute())
TempPathEXE = str(pathlib.Path(tempfile.gettempdir() + "/Materialbestelltung_temp/Update_FFW_NAS_Converter.exe").absolute())

from ui_UpdateChecker_MainWindow import Ui_UpdateChecker
from ui_UpdateChecker_Fortschritt import Ui_Fortschritt

# Variablen
    
homePath = os.path.dirname(sys.executable)

homePath = os.path.dirname(__file__) # Ansonsten wird kein Icon angezeigt
logo_Pfad = os.path.join(homePath, 'data\\Icon.png')
logo_ERROR_Pfad = os.path.join(homePath, 'data\\ERROR_ICON.png')

global filepath
global outputpath

filepath = ""
outputpath = ""

# Classes

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowIcon = windowIcon

        # self.ui.IMG_VPNStatus.setPixmap(QPixmap(u"data/Status_red.png")) Rot einblenden
        self.ui.BTN_Verbinden.clicked.connect(self.Verbinden)
        self.ui.BTN_Trennen.clicked.connect(self.Trennen)
        self.ui.BTN_Einstellungen.clicked.connect(self.Einstellungen)

        self.show()

    def Verbinden(self):
        print("Verbinden")

    def Trennen(self):
        print("Trennen")

    def Einstellungen(self):
        print("Einstellungen")
    
class ERROR_MSG(QDialog):
    def __init__(self):
        super(ERROR_MSG, self).__init__()
        self.ui = Ui_ERROR_MSG()
        self.ui.setupUi(self)
        self.setWindowIcon = windowERRORIcon

        self.ui.BTN_OK.clicked.connect(self.close) # Select File

# Updatechecker Classes

class UpdateChecker(QMainWindow):
    def __init__(self):
        super(UpdateChecker, self).__init__()
        self.ui = Ui_UpdateChecker()
        self.ui.setupUi(self)
        self.setWindowIcon(windowIcon)

        self.ui.BT_Update.clicked.connect(self.callUpdate)

    def callUpdate(self):
        Fortschritt_UpdateChecker.ui.LBL_Status.setText("Download...")
        Fortschritt_UpdateChecker.ui.progressBar.setValue(0)
        Fortschritt_UpdateChecker.show()
        UpdateChecker.close()
        t1 = Thread_UpdateChecker(1, "t1", "download")
        t1.start()

class Fortschritt_UpdateChecker(QMainWindow):
    def __init__(self):
        super(Fortschritt_UpdateChecker, self).__init__()
        self.ui = Ui_Fortschritt()
        self.ui.setupUi(self)
        self.setWindowIcon(windowIcon)

        self.ui.BT_Clos_ALL.hide()
        self.ui.BT_Clos_ALL.setDisabled(True)

        self.ui.BT_Clos_ALL.clicked.connect(self.closeit)

    def closeEvent(self, event: QtGui.QCloseEvent):
        current_system_pid = os.getpid()

        ThisSystem = psutil.Process(current_system_pid)

        try:
            os.remove(TempPathZIPFILE)
            os.remove(TempPathEXE)
        except:
            pass

        ThisSystem.terminate()

    def closeit(self):
        # Write JsonFile
        with open(pfad_updatepfad, "r") as jsonFile:
            data = json.load(jsonFile)

        data["Programmversion"] = NeusteVersion

        with open(pfad_updatepfad, "w") as jsonFile:
            json.dump(data, jsonFile)
        
        self.close()

class Thread_UpdateChecker(threading.Thread):
    def __init__(self, iD, name, make):
        threading.Thread.__init__(self)
        self.iD = iD
        self.name = name
        self.make = make

    def download(self):
        response = requests.get(DownloadUpdateFileURL, stream=True, headers=headersURL)

        total_size_in_bytes= int(response.headers.get('content-length', 0))
        block_size = 1024 #1 Kibibyte

        prozent = 0

        with open(TempPathZIPFILE, 'wb') as file:
            for data in response.iter_content(block_size):
                prozent = prozent + len(data)
                neuProzent = float(prozent / total_size_in_bytes * 100.00)
                Fortschritt_UpdateChecker.ui.progressBar.setValue(round(neuProzent))
                file.write(data)

        shutil.unpack_archive(TempPathZIPFILE, TempPath)
        os.system(TempPathEXE)
        Fortschritt_UpdateChecker.ui.LBL_Status.setText("Fertig!")

    def run(self):
        if self.make == "download":
            self.download()

# Funktionen Checkfor Update

def CheckVersion_forUpdate():
    global AktulleVersion
    # Installierte Version lesen.
    with open(pfad_updatepfad) as file:
        AktulleVersion = json.load(file)

    AktulleVersion = float(AktulleVersion["Programmversion"])
    UpdateChecker.ui.LBL_aktuelleVersion.setText(str(AktulleVersion))
    print("Aktuelle Version: " + str(AktulleVersion))

    # Neuste Version lesen.

    NeusteVersion = requests.get(url=JsonURL, headers=headersURL, params=paramURL)
    NeusteVersion = NeusteVersion.json()
    NeusteVersion = float(NeusteVersion["Programmversion"])
    UpdateChecker.ui.LBL_verfuegbareVersion.setText(str(NeusteVersion))
    print("Neuste Version: " + str(NeusteVersion))

    if AktulleVersion == NeusteVersion:
        pass
    else:
        UpdateChecker.show() # main window öffnen

# Updatechecker

if os.path.exists(TempPath) == False:
    os.makedirs(TempPath)

# Funktionen


# Programm Code

if __name__ == "__main__":
    app= QApplication(sys.argv)
    windowIcon = QIcon(logo_Pfad)
    windowERRORIcon = QIcon(logo_ERROR_Pfad)

    UpdateChecker = UpdateChecker()
    Fortschritt_UpdateChecker = Fortschritt_UpdateChecker()    
    MainWindow = MainWindow()
    ERROR_MSG = ERROR_MSG()

    CheckVersion_forUpdate()

    MainWindow.ui.LBL_Version.setText("V" + str(AktulleVersion))
    MainWindow.show() # main window öffnen
    sys.exit(app.exec_()) # alles beenden