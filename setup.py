import sys
import os
from cx_Freeze import setup, Executable

# Build Optionen
build_exe_options = dict(packages = ["win32gui", "win32con", "win32api", "pathlib", "PySide6", "sys", "os", "tokenize", "tempfile", "json", "shutil", "requests", "threading", "psutil", "subprocess", "time", "win32process"], excludes = [], include_files = ["data/", "platforms/", "FFW_NAS_CheckforUpdate.json", "Netzwerkordner/"])

# Ziel
target = Executable(
    script="FFW_NAS.py",
    base="Win32GUI",
    icon="data/favicon.ico"
)

# Setup CX Freez
setup( 
    name = "FFW_NAS",
    version = "0.1",
    description = "VPN Tunnel aufbauen FFW-Haus Prosdorf",
    author= "Manuel Bücherl",
    options = {'build_exe' : build_exe_options},
    executables = [target]
    )