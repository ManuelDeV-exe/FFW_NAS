from asyncio import subprocess
from multiprocessing.connection import wait
import sys, os
from tokenize import Number
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6 import QtGui, QtCore
import win32api
import win32gui
import win32con
import win32process
import time

import pathlib
import tempfile
import json
import shutil
import requests
from threading import Thread
import psutil

from ui_FFW_NAS import Ui_MainWindow
from ui_ERROR_MSG import Ui_ERROR_MSG

# Updater

window_IDs = 0

global AktulleVersion
AktulleVersion = ""
JsonURL = 'https://3ddruck-mb.de/UpdateChecker/FFW_NAS_CheckforUpdate.json'
headersURL = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
paramURL = dict()
DownloadUpdateFileURL = 'https://3ddruck-mb.de/UpdateChecker/Update_FFW_NAS_Converter.zip'

global NeusteVersion
NeusteVersion = ""
pfad_updatepfad = str(pathlib.Path(__file__).parents[0]) + "/FFW_NAS_CheckforUpdate.json"

TempPath = str(pathlib.Path(tempfile.gettempdir() + "/FFW_NAS").absolute())
TempPathZIPFILE = str(pathlib.Path(tempfile.gettempdir() + "/FFW_NAS/Update_FFW_NAS_Converter.zip").absolute())
TempPathEXE = str(pathlib.Path(tempfile.gettempdir() + "/FFW_NAS/Update_FFW_NAS_Converter.exe").absolute())

from ui_UpdateChecker_MainWindow import Ui_UpdateChecker
from ui_UpdateChecker_Fortschritt import Ui_Fortschritt

# Variablen
    
homePath = os.path.dirname(sys.executable)

homePath = os.path.dirname(__file__) # Ansonsten wird kein Icon angezeigt
logo_Pfad = os.path.join(homePath, 'data\\Icon.png')
logo_ERROR_Pfad = os.path.join(homePath, 'data\\ERROR_ICON.png')

Netzwerkordner = os.path.join(homePath, 'Netzwerkordner\\FFW-Prosdorf')
Network_Shortcuts = os.path.expandvars(r'%APPDATA%\Microsoft\Windows\Network Shortcuts\FFW-Prosdorf')

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

        self.ui.BTN_Trennen.setDisabled(True)

        self.ui.BTN_Verbinden.clicked.connect(Verbinden)
        self.ui.BTN_Trennen.clicked.connect(Trennen)

        self.show()

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

class Thread_UpdateChecker(Thread):
    def __init__(self, iD, name, make):
        Thread.__init__(self)
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
    
def winEnumHandler( hwnd, ctx ):
    global window_IDs
    if win32gui.IsWindowEnabled( hwnd ):
        if "FRITZ!Fernzugang" in win32gui.GetWindowText(hwnd):
            print(hex(hwnd), win32gui.GetWindowText(hwnd))
            print(hwnd) 
            window_IDs = hwnd
        print(hex(hwnd), win32gui.GetWindowText( hwnd ))
        # print(hex(hwnd))

def FRITZVPN():
    os.system("powershell.exe FRITZVPN.exe")

def NetzwerkOrdner():
    try:
        shutil.copytree(Netzwerkordner, Network_Shortcuts)
    except:
        MainWindow.ui.BTN_Verbinden.setDisabled(False)

def getWindowID():
    MainWindow.ui.IMG_Einstazbereit.setPixmap(QPixmap(u"data/Status_orange.png")) #Gelb
    time.sleep(1.5)
    global window_IDs
    win32gui.EnumWindows( winEnumHandler, None )
    try:
        window_IDs = window_IDs
        print(window_IDs)
    except:
        print("An exception occurred")
        MainWindow.ui.IMG_Einstazbereit.setPixmap(QPixmap(u"data/Status_red.png")) #GRÜN

    MainWindow.ui.BTN_Trennen.setDisabled(False)
    MainWindow.ui.IMG_Einstazbereit.setPixmap(QPixmap(u"data/Status_green.png")) #GRÜN


def Verbinden():
    # Threas definieren
    TH_FRITZVPN = Thread(target=FRITZVPN)
    TH_NetzwerkOrdner = Thread(target=NetzwerkOrdner)
    TH_WindowID = Thread(target=getWindowID)

    # restlicher Code
    MainWindow.ui.BTN_Trennen.setDisabled(False)
    MainWindow.ui.BTN_Verbinden.setDisabled(True)
    TH_FRITZVPN.start()
    MainWindow.ui.IMG_VPNStatus.setPixmap(QPixmap(u"data/Status_orange.png")) #Gelb

    TH_WindowID.start()

    ERROR_MSG.setWindowTitle("Hinweis")
    ERROR_MSG.ui.ERRO_MSG.setText("Bitte Bestätige mit OK wenn die Verbindung\naufgebaut wurde.\nFritzFernzugang bitte nur über Den Button \"Trennen\" Beenden.")
    ERROR_MSG.exec() # Warte auf bestätigung durch Nutzer

    MainWindow.ui.IMG_VPNStatus.setPixmap(QPixmap(u"data/Status_green.png")) #GRÜN

    try:
        win32gui.ShowWindow(window_IDs, win32con.SW_HIDE)
        win32gui.SetForegroundWindow(window_IDs)
    except:
        print("Error")

    TH_NetzwerkOrdner.start()
        
def Trennen():
    try:
        shutil.rmtree(Network_Shortcuts)
    except:
        print("Error")

    try:
        win32gui.ShowWindow(window_IDs, win32con.SW_SHOW)
        win32gui.SetForegroundWindow(window_IDs)
    except:
        print("Error")

    ERROR_MSG.setWindowTitle("Hinweis")
    ERROR_MSG.ui.ERRO_MSG.setText("Bitte klicke im FritzFernzugang auf Abbau.\nJetzt kann das Programm \"FritzFernzugang\" beendet werden. ")
    ERROR_MSG.exec() # Warte auf bestätigung durch Nutzer

    MainWindow.ui.BTN_Trennen.setDisabled(True)
    MainWindow.ui.BTN_Verbinden.setDisabled(False)
    MainWindow.ui.IMG_VPNStatus.setPixmap(QPixmap(u"data/Status_unknow.png")) #unknow
    MainWindow.ui.IMG_Einstazbereit.setPixmap(QPixmap(u"data/Status_unknow.png")) #unknow

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